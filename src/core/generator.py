import json
import random
import traceback

import google.generativeai as genai
from google.api_core.exceptions import (InternalServerError, ResourceExhausted,
                                        ServiceUnavailable)
from google.generativeai.types import generation_types

from core.security import KeyManager
# 引入你的基礎建設
from tool.debug import dbg


class ToeicGenerator:
    """多益題目 AI 生成引擎 (具備高可用性模型降級與金鑰輪詢機制)"""

    # 將使用者的模型策略定為類別常數
    FALLBACK_MODELS = [
        'models/gemini-3.1-flash-lite-preview', # 🥇 (15 RPM / 500 RPD) - 海量掃描專用 (建議優先使用這個高額度模型來出題)
        'models/gemini-3-flash-preview',        # 🥈 (5 RPM / 20 RPD) - 高智商，專解複雜新聞
        'models/gemini-2.5-flash-lite',         # 🥉 (10 RPM / 20 RPD) - 伺服器波動時替補
        'models/gemini-2.5-flash',              # 🎖️ (5 RPM / 20 RPD) - 最後底線
    ]

    def __init__(self):
        # 1. 取得金鑰池
        self.api_keys = KeyManager.get_gemini_keys()
        if not self.api_keys:
            dbg.error("❌ 無法啟動生成引擎：金鑰池為空！")
            raise ValueError("Missing Gemini API Keys")

        dbg.log(f"✅ 引擎初始化成功，已載入 {len(self.api_keys)} 組備用金鑰。")

    def _create_model(self, model_name: str) -> genai.GenerativeModel:
        """根據指定的模型名稱建立 Model 實例"""
        return genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self._get_system_prompt(),
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )

    def _get_system_prompt(self) -> str:
        """核心系統提示詞"""
        return """
        你是一位專業的多益（TOEIC）首席出題官方與高階英文講師。
        請根據使用者的要求，生成符合多益商務情境的全新英文題目。

        【強制要求】
        你必須且只能輸出標準的 JSON 格式，絕對不能包含任何 Markdown 語法或額外文字。

        【JSON 欄位規格】
        {
          "category": "字串",
          "passage": "字串 (若為單字/文法題請留空字串 \"\"，若為閱讀題請給 100-200 字文章)",
          "question": "字串 (問題主體)",
          "option_a": "字串",
          "option_b": "字串",
          "option_c": "字串",
          "option_d": "字串",
          "answer": "字串 (A, B, C 或 D)",
          "explanation": "字串 (必須包含完整的【翻譯】與詳細的【解析】)"
        }
        """

    def generate_question(self, category: str, theme: str = "商務會議") -> dict | None:
        """
        呼叫 API 生成單道題目 (具備自動降級與金鑰切換機制)
        """
        prompt = f"請生成一道【{category}】題型，情境設定為【{theme}】。"
        dbg.var(category=category, theme=theme)

        # 💡 外層迴圈：模型降級策略
        for model_name in self.FALLBACK_MODELS:

            # 💡 內層迴圈：金鑰輪詢策略 (每次切換模型，都打亂 Key 確保負載均衡)
            keys_pool = list(self.api_keys)
            random.shuffle(keys_pool)

            for api_key in keys_pool:
                # 隱藏金鑰前綴，只印出最後 4 碼供 Debug 追蹤
                key_tail = api_key[-4:] if len(api_key) > 4 else "UNKN"

                try:
                    # 設定當前使用的 Key 並建立模型
                    genai.configure(api_key=api_key)
                    model = self._create_model(model_name)

                    dbg.log(f"📡 [呼叫中] 模型: {model_name} | 金鑰: *{key_tail}")
                    response = model.generate_content(prompt)

                    if not response.text:
                        dbg.war(f"⚠️ [{model_name} | *{key_tail}] 回傳空值，嘗試下一組設定...")
                        continue # 嘗試下一把 Key

                    result_dict = json.loads(response.text)
                    dbg.log(f"✅ 成功生成題目！(使用模型: {model_name} | 金鑰: *{key_tail})")
                    dbg.dump(result_dict, label="Gemini_Output")

                    return result_dict

                except ResourceExhausted:
                    # 這是最常發生的狀況：API 額度耗盡 (429 Too Many Requests)
                    dbg.war(f"🛑 [配額耗盡] 模型: {model_name} | 金鑰: *{key_tail} 已達 RPM/RPD 上限，切換金鑰...")
                    continue # 繼續內層迴圈，嘗試下一把 Key

                except (InternalServerError, ServiceUnavailable) as e:
                    # Google 伺服器端錯誤 (500 / 503)
                    dbg.war(f"🌩️ [伺服器異常] 模型: {model_name} 發生錯誤 ({e})，切換金鑰...")
                    continue # 繼續內層迴圈，嘗試下一把 Key

                except json.JSONDecodeError as e:
                    # JSON 格式崩潰：通常是該模型的該次生成發瘋，直接用同一把 Key 再試一次或換 Key
                    dbg.error(f"❌ [格式損壞] 模型: {model_name} 輸出的不是合法 JSON: {e}")
                    continue

                except generation_types.StopCandidateException as e:
                    dbg.error(f"❌ [安全阻擋] 題目內容觸發安全審查: {e}")
                    return None # 觸發安全審查通常與 Prompt 有關，不需盲目重試

                except Exception as e:
                    dbg.error(f"❌ [未預期錯誤]: {e}\n{traceback.format_exc()}")
                    continue

        # 如果雙層迴圈全部跑完還是沒有 return，代表徹底失敗
        dbg.error("🚨 嚴重警告：所有模型與金鑰池皆已嘗試完畢，生成徹底失敗！")
        return None
