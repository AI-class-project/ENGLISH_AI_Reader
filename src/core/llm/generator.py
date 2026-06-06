import json
import random
import time

from google import genai
from google.genai import types
from google.genai.errors import APIError

from core.const import OptionKey, ToeicGenCol, ToeicQuestionCol
from core.llm.security import KeyManager
from core.meta.toeic import QuestionType
from tool.debug import dbg


class ToeicGenerator:
    """
    多益題目 AI 生成引擎 (動態 System Prompt 分流版)
    職責：依據不同題型派發專屬的 JSON 格式合約，確保 AI 輸出結構絕對穩定
    """

    FALLBACK_MODELS = [
        'models/gemini-3.1-flash-lite-preview', # 🥇 主力
        'models/gemini-3-flash-preview',        # 🥈 備援一
        'models/gemini-2.5-flash-lite',         # 🥉 備援二
        'models/gemini-2.5-flash',              # 🎖️ 底線
    ]

    def __init__(self):
        self.api_keys = KeyManager.get_gemini_keys()
        if not self.api_keys:
            dbg.error("❌ 無法啟動生成引擎：金鑰池為空！")
            raise ValueError("Missing Gemini API Keys")
        dbg.log(f"✅ 核心引擎初始化成功，已載入 {len(self.api_keys)} 組備用金鑰。")

    def generate_question(self, **kwargs) -> dict | None:
        """
        核心出題與動態格式派發方法 (全面 Enum 升級版)
        """
        # 1. 拔除魔法字串，改用 ToeicGenCol 獲取外部控制參數
        category = kwargs.get(ToeicGenCol.CATEGORY, "文法選擇")
        theme = kwargs.get(ToeicGenCol.THEME, "通用商務")

        # --------------------------------------------------
        # 2. 使用 f-string 與 ToeicQuestionCol 動態建構鏡像 JSON 合約
        # --------------------------------------------------
        categories_str = ", ".join(QuestionType.get_all_type())

        if category in [QuestionType.GRAMMAR.value, QuestionType.VOCABULARY.value]:
            system_instruction = f"""
            你是一位專業的多益出題官方。請生成符合商務情境的全新【單選選擇題】。

            【強制要求】
            請直接輸出一個標準的 JSON 物件 (外層為大括號 {{ ... }})。

            【JSON 結構必須完全符合以下規格】
            {{
              "{ToeicQuestionCol.CATEGORY}": "字串 (必須從以下選項中嚴格擇一填入: {categories_str})",
              "{ToeicQuestionCol.THEME}": "字串 (關於文章內容的情境標題)",
              "{ToeicQuestionCol.PASSAGES}": [],
              "{ToeicQuestionCol.QUESTIONS}": [
                {{
                  "{ToeicQuestionCol.QUESTION}": "字串 (問題主體，預留 ______ 供填空)",
                  "{ToeicQuestionCol.OPTIONS}": {{
                    "{OptionKey.A}": "字串",
                    "{OptionKey.B}": "字串",
                    "{OptionKey.C}": "字串",
                    "{OptionKey.D}": "字串"
                  }},
                  "{ToeicQuestionCol.ANSWER}": "字串 (A, B, C 或 D)",
                  "{ToeicQuestionCol.EXPLANATION}": "字串 (翻譯與解析)"
                }}
              ]
            }}
            """
            focus = kwargs.get(ToeicGenCol.GRAMMAR_FOCUS, "高頻商務字彙辨析")
            user_prompt = f"請生成 1 個【{category}】題目，情境設定為【{theme}】。核心考點必須鎖定在：【{focus}】。"
            dbg.var(category=category, theme=theme, focus=focus)

        elif category in [QuestionType.READING_SINGLE.value, QuestionType.READING_MULTIPLE.value]:
            system_instruction = f"""
            你是一位專業的多益閱讀題組設計專家。請生成具備情境深度的【閱讀理解題組】。

            【強制要求】
            請直接輸出一個標準的 JSON 物件 (外層為大括號 {{ ... }})。

            【JSON 結構必須完全符合以下規格】
            {{
              "{ToeicQuestionCol.CATEGORY}": "字串 (必須從以下選項中嚴格擇一填入: {categories_str})",
              "{ToeicQuestionCol.THEME}": "字串 (關於文章內容的情境標題)",
              "{ToeicQuestionCol.PASSAGES}": [
                "字串 (第一篇文章內容)",
                "字串 (第二篇文章內容，若為單篇則此陣列只有一個元素)"
              ],
              "{ToeicQuestionCol.QUESTIONS}": [
                {{
                  "{ToeicQuestionCol.QUESTION}": "字串 (針對文章內容的問題)",
                  "{ToeicQuestionCol.OPTIONS}": {{
                    "{OptionKey.A}": "字串",
                    "{OptionKey.B}": "字串",
                    "{OptionKey.C}": "字串",
                    "{OptionKey.D}": "字串"
                  }},
                  "{ToeicQuestionCol.ANSWER}": "字串 (A, B, C 或 D)",
                  "{ToeicQuestionCol.EXPLANATION}": "字串 (翻譯與解析)"
                }}
              ]
            }}
            """
            relation = kwargs.get(ToeicGenCol.READING_RELATION, "單篇商務公告信件")
            sub_count = random.randint(4, 5) if QuestionType.READING_MULTIPLE.value in category else random.randint(2, 3)

            user_prompt = (
                f"請生成 1 個【{category}】題組，情境設定為【{theme}】。\n"
                f"1. 你必須嚴格按照以下結構撰寫文章：【{relation}】。若包含多篇文章，每篇文章開頭請加上 [DOC 1] 或 [DOC 2] 標記。\n"
                f"2. 針對這組文章，出 {sub_count} 個互不相同的子題目。"
            )
            dbg.var(category=category, theme=theme, relation=relation, sub_questions=sub_count)

        else:
            dbg.error(f"❌ 引擎不支援此題型分類: {category}")
            return None

        # --------------------------------------------------
        # 3. 發動機點火與防彈 JSON 解析
        # --------------------------------------------------
        for model_name in self.FALLBACK_MODELS:
            for key_idx, current_key in enumerate(self.api_keys):
                key_tail = current_key[-4:] if len(current_key) > 4 else "UNKN"
                dbg.log(f"📡 嘗試出題 - 模型: {model_name} | 金鑰: #{key_idx + 1} (*{key_tail})")

                try:
                    client = genai.Client(api_key=current_key)
                    response = client.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            response_mime_type="application/json",
                            temperature=0.7,
                        )
                    )

                    raw_text = response.text.strip() if response.text else ""
                    if not raw_text:
                        continue

                    if "```" in raw_text:
                        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

                    start_idx = raw_text.find('{')
                    end_idx = raw_text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        raw_text = raw_text[start_idx:end_idx+1]

                    result_dict = json.loads(raw_text)

                    # 確認回傳的是字典，且包含我們要求的核心 questions 欄位
                    if isinstance(result_dict, dict) and ToeicQuestionCol.QUESTIONS in result_dict:
                        dbg.log(f"🎉 成功生成題組大物件！")
                        return result_dict
                    else:
                        continue

                except APIError as api_err:
                    if api_err.code == 429:
                        dbg.war(f"[{model_name}] 金鑰 #{key_idx + 1} 限流 (429)，換 Key...")
                        time.sleep(0.5)
                        continue
                    else:
                        dbg.error(f"🌩️ [{model_name}] 伺服器錯誤 (Code: {api_err.code})，跳出換模型...")
                        break
                except Exception as e:
                    dbg.error(f"❌ 未預期錯誤: {e}")
                    continue

        dbg.error("🚨 嚴重警告：核心出題引擎全面癱瘓！")
        return None