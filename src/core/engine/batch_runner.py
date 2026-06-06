import dataclasses
import hashlib
import json
import os
import time

from core.const import ToeicGenCol
from core.engine.config import GENERATE_BATCH_CONFIG
from core.engine.models import ToeicQuestionModel
from core.llm.generator import ToeicGenerator, ToeicQuestionCol
from tool.debug import dbg
from tool.path import PathConfig


class ToeicBatchRunner:
    """批量出題與導出工具"""

    def __init__(self):
        self.generator = ToeicGenerator()
        self.output_dir = PathConfig.TOEIC_POOL

    def generate_batch(self, count: int, config: dict) -> list[ToeicQuestionModel]:
        """
        批次生成特定題型，並在第一時間將其轉換為 UI 友善的強型別巢狀物件 (ToeicQuestionModel)
        """
        category = config.get(ToeicGenCol.CATEGORY.value, "未定義題型")
        theme = config.get(ToeicGenCol.THEME.value, "通用商務")
        dbg.log(f"開始批次生產任務：【{category}】預計目標總數：{count} 題組，情境：{theme}")

        generated_list = []
        existing_fingerprints = set()

        attempt = 0
        max_attempts = int(count * GENERATE_BATCH_CONFIG.ATTEMPTS_RATIO_MAX)

        while len(generated_list) < count and attempt < max_attempts:
            attempt += 1
            dbg.log(f"進度：({len(generated_list)}/{count}) | 正在執行第 {attempt} 次生成嘗試...")

            # 呼叫 AI 引擎，取得符合巢狀結構的單一 dict 大物件
            questions_chunk = self.generator.generate_question(**config)

            if not questions_chunk:
                dbg.war("該次嘗試未取得有效資料，跳過。")
                continue

            raw_passages = questions_chunk.get(ToeicQuestionCol.PASSAGES.value, [])
            raw_questions = questions_chunk.get(ToeicQuestionCol.QUESTIONS.value, [])

            # 擷取第一篇文章的前 20 個字元作為文章指紋前綴
            passage_prefix = raw_passages[0][:GENERATE_BATCH_CONFIG.PASSAGE_PREFIX_MAX] if raw_passages else ""

            valid_questions = []
            for q in raw_questions:
                q_text = q.get(ToeicQuestionCol.QUESTION.value, "").strip()
                if not q_text:
                    continue

                # 組合特徵：文章前綴 + 問題主體
                unique_feature = f"{passage_prefix}_{q_text}"
                fingerprint = hashlib.md5(unique_feature.encode('utf-8')).hexdigest()

                if fingerprint in existing_fingerprints:
                    dbg.war(f"🔄 偵測到重複題目！自動跳過該子題目。")
                    continue

                existing_fingerprints.add(fingerprint)
                valid_questions.append(q)

            # 如果這一組所有的子題目都被重置濾光了，則放棄本組
            if not valid_questions: continue

            # 將通過去重的子題目重新塞回大物件中
            questions_chunk[ToeicQuestionCol.QUESTIONS.value] = valid_questions

            try:
                question_model = ToeicQuestionModel.from_ai_dict(questions_chunk)
                generated_list.append(question_model)
                dbg.var(current_pool_size=len(generated_list))
            except Exception as e:
                dbg.error(f"❌ 封裝模型失敗: {e}")

            time.sleep(1.2)

        dbg.log(f"批次生產結束！成功產出 {len(generated_list)} 個題組（總嘗試次數: {attempt}）")
        return generated_list[:count]

    def save_to_json(self, data: list[ToeicQuestionModel]):
        """將高階巢狀物件清單，完美序列化並附加 (Append) 到 JSON 存檔中"""
        try:
            new_serialized_data = [dataclasses.asdict(m) for m in data]

            existing_data = []

            file_exists = self.output_dir.exists() if hasattr(self.output_dir, "exists") else os.path.exists(self.output_dir)

            if file_exists:
                with open(self.output_dir, "r", encoding="utf-8") as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        dbg.war("⚠️ 舊 JSON 檔案為空或格式損毀，系統將重新建立題庫。")

            # 將新資料合併到舊資料池中
            combined_data = existing_data + new_serialized_data

            # 將合併後的完整大陣列，重新覆蓋寫入檔案
            with open(self.output_dir, "w", encoding="utf-8") as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)

            dbg.log(f"💾 【題庫累積匯出成功】本次新增 {len(data)} 組，題庫總計: {len(combined_data)} 組。")

        except Exception as e:
            dbg.error(f"❌ 寫入 JSON 題庫檔案失敗: {e}")