import json
import random
import traceback
import google.generativeai as genai
from google.generativeai.types import generation_types

# 引入你的強大基礎建設
from tool.debug import dbg
from core.security import KeyManager
from core.const import GlobalVar

class ToeicGenerator:
    """多益題目 AI 生成引擎"""

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        # 1. 取得金鑰池
        self.api_keys = KeyManager.get_gemini_keys()
        if not self.api_keys:
            dbg.error("❌ 無法啟動生成引擎：金鑰池為空！")
            raise ValueError("Missing Gemini API Keys")

        # 2. 隨機抽取一把 Key (簡單的負載均衡/防限流)
        active_key = random.choice(self.api_keys)
        genai.configure(api_key=active_key)
        dbg.log(f"啟動 Gemini 引擎，使用模型: {model_name} (已載入 {len(self.api_keys)} 組備用金鑰)")

        # 3. 初始化模型與強制 JSON 輸出設定
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self._get_system_prompt(),
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7 # 稍微保留一點創造力，讓題目不重複
            )
        )

    def _get_system_prompt(self) -> str:
        """核心系統提示詞：規定身分與 JSON 結構"""
        return """
        你是一位專業的多益（TOEIC）首席出題官方與高階英文講師。
        請根據使用者的要求，生成符合多益商務情境的全新英文題目。

        【強制要求】
        你必須且只能輸出標準的 JSON 格式，絕對不能包含任何 Markdown 語法（如 ```json 等）或額外文字。

        【JSON 欄位規格】
        {
          "category": "字串 (單字克漏字 / 文法選擇 / 閱讀理解)",
          "passage": "字串 (若為單字或文法題請留空字串 \"\"，若為閱讀題請給 100-200 字文章)",
          "question": "字串 (問題主體)",
          "option_a": "字串",
          "option_b": "字串",
          "option_c": "字串",
          "option_d": "字串",
          "answer": "字串 (只能是 A, B, C 或 D)",
          "explanation": "字串 (必須包含完整的【翻譯】與詳細的【解析】)"
        }
        """

    def generate_question(self, category: str, theme: str = "商務會議") -> dict | None:
        """
        呼叫 API 生成單道題目
        :param category: 題型 (例如: 單字克漏字)
        :param theme: 主題情境 (例如: 商務會議、採購、轉職)
        """
        prompt = f"請生成一道【{category}】題型，情境設定為【{theme}】。"
        dbg.var(category=category, theme=theme)

        try:
            dbg.log("📡 正在呼叫 Gemini API...")
            response = self.model.generate_content(prompt)

            # 確保有回應
            if not response.text:
                dbg.war("⚠️ Gemini 回傳了空值")
                return None

            # 解析 JSON
            result_dict = json.loads(response.text)
            dbg.log("✅ 成功生成並解析題目！")

            # 使用你的 dbg.dump 漂亮地印出 JSON 結果
            dbg.dump(result_dict, label="Gemini_Output")

            return result_dict

        except json.JSONDecodeError as e:
            dbg.error(f"❌ Gemini 回傳的不是合法 JSON: {e}")
            dbg.error(f"原始回傳內容: {response.text}")
            return None
        except generation_types.StopCandidateException as e:
            dbg.error(f"❌ 觸發安全過濾，生成被中斷: {e}")
            return None
        except Exception as e:
            dbg.error(f"❌ API 發生未預期錯誤: {e}\n{traceback.format_exc()}")
            return None

# ==========================================
# 測試區塊 (只有直接執行此檔案時才會跑)
# ==========================================
if __name__ == "__main__":
    try:
        # 初始化引擎 (預設使用 flash 模型，速度最快、最便宜)
        engine = ToeicGenerator()

        # 測試生成一題單字題
        question_data = engine.generate_question(category="單字克漏字", theme="電子郵件與日程安排")

    except Exception as e:
        dbg.error(f"測試失敗: {e}")