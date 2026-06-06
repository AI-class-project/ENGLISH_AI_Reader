import json
import random
import time
import traceback

from google import genai
from google.genai import types
from google.genai.errors import APIError

from core.const import ToeicQuestionCol
from core.meta.toeic import QuestionType, ToeicGenCol
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
        """核心系統提示詞：利用 Enum 動態動態建構規格，消滅任何手滑打錯字的可能性"""
        return f"""
        你是一位專業的多益（TOEIC）首席出題官方與高階英文講師。
        請根據使用者的要求，生成符合多益商務情境的全新英文題目。

        【強制要求】
        你必須且只能輸出標準的 JSON ARRAY (外層為方括號 [ ... ])，絕對不能包含任何 Markdown 語法或額外文字。

        【JSON 陣列內單一物件的欄位規格】
        {{
          "{ToeicQuestionCol.CATEGORY.value}": "字串",
          "{ToeicQuestionCol.PASSAGE.value}": "字串 (若為單字/文法選擇請留空字串 \"\")",
          "{ToeicQuestionCol.QUESTION.value}": "字串 (問題主體)",
          "{ToeicQuestionCol.OPTION_A.value}": "字串",
          "{ToeicQuestionCol.OPTION_B.value}": "字串",
          "{ToeicQuestionCol.OPTION_C.value}": "字串",
          "{ToeicQuestionCol.OPTION_D.value}": "字串",
          "{ToeicQuestionCol.ANSWER.value}": "字串 (只能是 A, B, C 或 D)",
          "{ToeicQuestionCol.EXPLANATION.value}": "字串"
        }}
        """

    def generate_question(self, **kwargs) -> list[dict] | None:
        """
        呼叫 Gemini 生成題目 (支援單題與多題題組回傳)
        """
        category = kwargs.get(ToeicGenCol.CATEGORY.value, "文法選擇")
        theme = kwargs.get(ToeicGenCol.THEME.value, "通用商務")

        if category == QuestionType.GRAMMAR.value:
            focus = kwargs.get(ToeicGenCol.GRAMMAR_FOCUS.value, "動詞時態")
            prompt = f"請生成 1 個【文法選擇】題目，情境為【{theme}】。核心文法考點：【{focus}】。因為只生 1 題，JSON 陣列內只會包含 1 個物件。"
            dbg.var(category=category, theme=theme, focus=focus)

        elif category == QuestionType.VOCABULARY.value:
            prompt = f"請生成 1 個【單字克漏字】題目，情境為【{theme}】。四個選項必須是相同詞性但字義不同的高頻多益商務字彙。JSON 陣列內只會包含 1 個物件。"
            dbg.var(category=category, theme=theme)

        elif category == QuestionType.READING_SINGLE.value:
            sub_count = random.randint(2, 3) # 隨機決定子題目數量為 2~3 題
            prompt = (
                f"請生成 1 個【單篇閱讀理解】題組，情境設定為【{theme}】。\n"
                f"1. 你必須先寫出 1 篇 100-150 字的多益商務文章（放在 passage 欄位）。\n"
                f"2. 針對這篇文章，你必須出 {sub_count} 個互不相同的子題目（對應 JSON 陣列中的 {sub_count} 個物件）。\n"
                f"3. 關鍵防呆：這 {sub_count} 個物件中的 `passage` 欄位內容必須完全一致，不可有任何字元差異！"
            )
            dbg.var(category=category, theme=theme, sub_questions=sub_count)

        elif category == QuestionType.READING_MULTIPLE.value:
            sub_count = random.randint(4, 5)
            relation = kwargs.get(ToeicGenCol.READING_RELATION.value, "一篇廣告 + 一篇郵件")
            prompt = (
                f"請生成 1 個進階的【多篇閱讀理解】題組，情境設定為【{theme}】。\n"
                f"1. 你必須嚴格按照以下關聯結構撰寫 2 到 3 篇文章：【{relation}】。\n"
                f"   關鍵要求：每篇文章之間，必須使用『 [DOC 1] 』、『 [DOC 2] 』作為明確的開頭標記！例如：\n"
                f"   [DOC 1]\n(第一篇文章內容...)\n\n[DOC 2]\n(第二篇文章內容...)\n"
                f"   請將整套內容打包放在唯一的 `passage` 欄位中。\n"
                f"2. 針對這組互相關聯的文章，出 {sub_count} 個子題目..."
            )

        else:
            prompt = f"請生成一組【{category}】題目，情境設定為【{theme}】。"

        # 外層迴圈：模型降級策略
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
                        continue

                    # 防彈 JSON 陣列解析邏輯 (尋找第一個 [ 和最後一個 ])
                    if "```" in raw_text:
                        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

                    start_idx = raw_text.find('[')
                    end_idx = raw_text.rfind(']')
                    if start_idx != -1 and end_idx != -1:
                        raw_text = raw_text[start_idx:end_idx+1]

                    result_list = json.loads(raw_text)

                    if isinstance(result_list, list) and len(result_list) > 0:
                        dbg.log(f"🎉 成功生成題組！包含 {len(result_list)} 個題目物件。(使用模型: {model_name})")
                        return result_list
                    else:
                        dbg.war("⚠️ 回傳的 JSON 不是預期的非空陣列，換 Key 重試...")
                        continue

                except APIError as api_err:
                    if api_err.code == 429:
                        dbg.war(f"🛑 [{model_name}] API Key #{key_idx + 1} 額度耗盡 (429)，切換下一把 Key...")
                        time.sleep(0.5)
                        continue
                    else:
                        dbg.error(f"🌩️ [{model_name}] 發生伺服器錯誤 (Code: {api_err.code}): {api_err.message}")
                        break

                except Exception as e:
                    dbg.error(f"❌ 發生未預期錯誤: {e}\n{traceback.format_exc()}")
                    continue

        dbg.error("🚨 嚴重警告：所有模型與金鑰池皆已嘗試完畢，生成徹底失敗！")
        return None