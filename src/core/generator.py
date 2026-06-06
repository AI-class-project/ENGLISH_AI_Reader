import json
import time
import traceback

from google import genai
from google.genai import types
from google.genai.errors import APIError

from core.security import KeyManager
from tool.debug import dbg


class ToeicGenerator:
    """
    多益題目 AI 生成引擎 (工業級重構版)
    採用新版 SDK 實作完美隔離的 API Key 切換機制與防彈 JSON 解析。
    """
    FALLBACK_MODELS = [
        'models/gemini-3.1-flash-lite-preview', # 🥇 (15 RPM) - 優先使用，速度快額度高
        'models/gemini-3-flash-preview',        # 🥈 (5 RPM) - 高智商備援
        'models/gemini-2.5-flash-lite',         # 🥉 (10 RPM) - 伺服器波動時替補
        'models/gemini-2.5-flash',              # 🎖️ (5 RPM) - 最後底線
    ]

    def __init__(self):
        self.api_keys = KeyManager.get_gemini_keys()
        if not self.api_keys:
            dbg.error("❌ 無法啟動生成引擎：金鑰池為空！")
            raise ValueError("Missing Gemini API Keys")

        dbg.log(f"✅ 引擎初始化成功，已載入 {len(self.api_keys)} 組備用金鑰。")
        self.system_instruction = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
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
          "answer": "字串 (只能是 A, B, C 或 D)",
          "explanation": "字串 (包含完整的【翻譯】與詳細的【解析】)"
        }
        """

    def generate_question(self, category: str, theme: str = "商務會議") -> dict | None:
        """嘗試以二維瀑布機制呼叫 Gemini 生成題目"""
        prompt = f"請生成一道【{category}】題型，情境設定為【{theme}】。"
        dbg.var(category=category, theme=theme)

        for model_name in self.FALLBACK_MODELS:
            for key_idx, current_key in enumerate(self.api_keys):
                key_tail = current_key[-4:] if len(current_key) > 4 else "UNKN"
                dbg.log(f"📡 嘗試出題 - 模型: {model_name} | 金鑰: #{key_idx + 1} (*{key_tail})")

                raw_text = ""
                try:
                    client = genai.Client(api_key=current_key)

                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=self.system_instruction,
                            response_mime_type="application/json",
                            temperature=0.7,
                        )
                    )

                    raw_text = response.text.strip() if response.text else ""
                    if not raw_text:
                        dbg.war(f"[{model_name}] 回傳空字串，嘗試下一把 Key...")
                        continue

                    if "```" in raw_text:
                        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

                    start_idx = raw_text.find('{')
                    end_idx = raw_text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        raw_text = raw_text[start_idx:end_idx+1]

                    result_dict = json.loads(raw_text)
                    dbg.log(f"🎉 成功生成題目！(使用模型: {model_name})")
                    dbg.dump(result_dict, label="Generated_Question")

                    return result_dict

                except APIError as api_err:
                    if api_err.code == 429:
                        dbg.war(f"🛑 [{model_name}] API Key #{key_idx + 1} 額度耗盡 (429 Too Many Requests)，切換下一把 Key...")
                        time.sleep(0.5)
                        continue
                    else:
                        dbg.error(f"🌩️ [{model_name}] 發生伺服器錯誤 (Code: {api_err.code}): {api_err.message}")
                        break

                except ValueError as ve:
                    # 通常是觸發安全審查被阻擋 (Safety Block)
                    dbg.war(f"🛡️ [{model_name}] 題目內容觸發安全過濾器: {ve}")
                    break

                except json.JSONDecodeError:
                    dbg.error(f"❌ [{model_name}] 徹底無法解析為 JSON。\nLLM 原始輸出為: {raw_text}")
                    break

                except Exception as e:
                    # 網路斷線等未知錯誤，換 Key 再試一次
                    dbg.error(f"❌ 發生未預期錯誤: {e}\n{traceback.format_exc()}")
                    continue

        dbg.error("🚨 嚴重警告：所有模型與金鑰池皆已嘗試完畢，生成徹底失敗！")
        return None