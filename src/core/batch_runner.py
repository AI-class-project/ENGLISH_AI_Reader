import json
import time

from core.generator import ToeicGenerator
from tool.debug import dbg
from tool.path import PathConfig


class ToeicBatchRunner:
    """批量出題與導出工具"""

    def __init__(self):
        self.generator = ToeicGenerator()
        self.output_dir = PathConfig.TOEIC_POOL

        # 預留兩倍的嘗試機會，防止因為重複或失敗無限死迴圈
        self.max_attempts_ratio: float = 2.0

    def generate_batch(self, category: str, count: int, theme: str = "通用商務") -> list[dict]:
        """
        批次生成特定題型，並具備自我去重指紋機制
        """
        dbg.log(f"開始批次生產任務：【{category}】預計生產 {count} 題，情境：{theme}")

        generated_list = []
        existing_fingerprints = set() # 用於本次批次內的防重複指紋庫

        attempt = 0
        max_attempts = count * self.max_attempts_ratio

        while len(generated_list) < count and attempt < max_attempts:
            attempt += 1
            dbg.log(f"進度：({len(generated_list)}/{count}) | 正在執行第 {attempt} 次生成嘗試...")

            # 呼叫你的核心引擎
            question_data = self.generator.generate_question(category=category, theme=theme)

            if not question_data:
                dbg.war("該次嘗試未取得有效資料，跳過。")
                continue

            # 指紋防重複機制：利用「題目問題主體 (question)」作為不重複指紋
            q_text = question_data.get("question", "").strip()
            if not q_text:
                continue

            if q_text in existing_fingerprints:
                dbg.war(f"偵測到重複題目指紋！自動捨棄該題。")
                continue

            # 檢驗通過，收入庫中
            existing_fingerprints.add(q_text)
            generated_list.append(question_data)
            dbg.var(current_pool_size=len(generated_list))

            # 防禦免費版 API 的每分鐘請求限制
            time.sleep(1.0)

        dbg.log(f"🏁 批次生產結束！成功產出 {len(generated_list)} 題（總嘗試次數: {attempt}）")
        return generated_list

    def save_to_json(self, data: list[dict]):
        """將產出的題目清單打包儲存為標準 JSON 檔案，供資料庫夥伴匯入"""
        try:
            with open(self.output_dir, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            dbg.log(f"💾 【題庫匯出成功】檔案已成功寫入至: {self.output_dir}")
            dbg.log(f"👉 請將此檔案交給負責 Supabase 的夥伴進行資料注入。")
        except Exception as e:
            dbg.error(f"❌ 寫入 JSON 題庫檔案失敗: {e}")

