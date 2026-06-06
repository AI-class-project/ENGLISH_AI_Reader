import hashlib
import json
import time

from core.generator import ToeicGenerator
from core.meta.toeic import ToeicGenCol
from tool.debug import dbg
from tool.path import PathConfig


class ToeicBatchRunner:
    """批量出題與導出工具"""

    def __init__(self):
        self.generator = ToeicGenerator()
        self.output_dir = PathConfig.TOEIC_POOL
        self.max_attempts_ratio: float = 2.0

    def generate_batch(self, count: int, config: dict) -> list[dict]:
        """
        批次生成特定題型，支援單題與閱讀題組的指紋去重機制
        """
        category = config.get(ToeicGenCol.CATEGORY.value, "未定義題型")
        theme = config.get(ToeicGenCol.THEME.value, "通用商務")
        dbg.log(f"開始批次生產任務：【{category}】預計目標總數：{count} 題，情境：{theme}")

        generated_list = []
        existing_fingerprints = set()

        attempt = 0
        max_attempts = int(count * self.max_attempts_ratio)

        # 只要目前的題目庫數量還沒達到指定的 count，就繼續生
        while len(generated_list) < count and attempt < max_attempts:
            attempt += 1
            dbg.log(f"進度：({len(generated_list)}/{count}) | 正在執行第 {attempt} 次生成嘗試...")

            # 呼叫更新後的引擎 (此處回傳的必然是 list[dict])
            questions_chunk = self.generator.generate_question(**config)

            if not questions_chunk:
                dbg.war("該次嘗試未取得有效資料，跳過。")
                continue

            # 處理這一批次吐出來的題目
            valid_chunk = []
            for question_data in questions_chunk:
                passage_text = question_data.get("passage", "").strip()
                q_text = question_data.get("question", "").strip()

                # 指紋依據
                fingerprint_source = passage_text if passage_text else q_text
                if not fingerprint_source:
                    continue

                fingerprint = hashlib.md5(fingerprint_source.encode('utf-8')).hexdigest()

                if fingerprint in existing_fingerprints:
                    dbg.war(f"🔄 偵測到重複指紋！自動跳過該子題目。")
                    continue

                existing_fingerprints.add(fingerprint)
                valid_chunk.append(question_data)

            # 將通過去重審查的題目塞進大池子裡
            generated_list.extend(valid_chunk)
            dbg.var(current_pool_size=len(generated_list))

            time.sleep(1.2) # 稍微加長一點睡眠，因為閱讀題生成的 Token 量較大

        dbg.log(f"🏁 批次生產結束！成功產出 {len(generated_list)} 題（總嘗試次數: {attempt}）")
        # 如果因為隨機數量導致多生了幾題（例如目標 3 題，但閱讀題一吐就是 4 題），我們用切片精準裁切給使用者
        return generated_list[:count]

    def save_to_json(self, data: list[dict]):
        try:
            with open(self.output_dir, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            dbg.log(f"💾 【題庫匯出成功】檔案已成功寫入至: {self.output_dir}")
        except Exception as e:
            dbg.error(f"❌ 寫入 JSON 題庫檔案失敗: {e}")

