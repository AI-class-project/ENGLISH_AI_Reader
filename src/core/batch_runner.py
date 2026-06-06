import dataclasses
import hashlib
import json
import time

from core.const import ToeicGenCol
from core.generator import ToeicGenerator, ToeicQuestionCol
from core.models import ToeicQuestionModel
from tool.debug import dbg
from tool.path import PathConfig


class ToeicBatchRunner:
    """批量出題與導出工具"""

    def __init__(self):
        self.generator = ToeicGenerator()
        self.output_dir = PathConfig.TOEIC_POOL
        self.max_attempts_ratio: float = 2.0

    def generate_batch(self, count: int, config: dict) -> list[ToeicQuestionModel]:
        """
        批次生成特定題型，並在第一時間將其轉換為 UI 友善的強型別巢狀物件 (ToeicQuestionModel)
        """
        # ✅ 升級 1：使用 ToeicGenCol 安全獲取外部控制引數
        category = config.get(ToeicGenCol.CATEGORY.value, "未定義題型")
        theme = config.get(ToeicGenCol.THEME.value, "通用商務")
        dbg.log(f"開始批次生產任務：【{category}】預計目標總數：{count} 題組，情境：{theme}")

        generated_list = []
        existing_fingerprints = set()

        attempt = 0
        max_attempts = int(count * self.max_attempts_ratio)

        while len(generated_list) < count and attempt < max_attempts:
            attempt += 1
            dbg.log(f"進度：({len(generated_list)}/{count}) | 正在執行第 {attempt} 次生成嘗試...")

            # 呼叫 AI 引擎，取得符合巢狀結構的單一 dict 大物件
            questions_chunk = self.generator.generate_question(**config)

            if not questions_chunk:
                dbg.war("該次嘗試未取得有效資料，跳過。")
                continue

            # ✅ 升級 2：全面使用 ToeicQuestionCol 提取內層資料，消滅裸露的 "passages" 與 "questions" 字串
            raw_passages = questions_chunk.get(ToeicQuestionCol.PASSAGES.value, [])
            raw_questions = questions_chunk.get(ToeicQuestionCol.QUESTIONS.value, [])

            # 擷取第一篇文章的前 20 個字元作為文章指紋前綴
            passage_prefix = raw_passages[0][:20] if raw_passages else ""

            valid_questions = []
            for q in raw_questions:
                # ✅ 升級 3：使用 ToeicQuestionCol 安全提取子題目欄位 "question"
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
            if not valid_questions:
                continue

            # 將通過去重的子題目重新塞回大物件中
            questions_chunk[ToeicQuestionCol.QUESTIONS.value] = valid_questions

            # 💡 3. 將過濾完的強型別巢狀字典，完美還原封裝成高階物件
            try:
                # 這裡調用模型更新後的 from_ai_dict 轉換器
                question_model = ToeicQuestionModel.from_ai_dict(questions_chunk)
                generated_list.append(question_model)
                dbg.var(current_pool_size=len(generated_list))
            except Exception as e:
                dbg.error(f"❌ 封裝模型失敗: {e}")

            time.sleep(1.2)

        dbg.log(f"🏁 批次生產結束！成功產出 {len(generated_list)} 個題組（總嘗試次數: {attempt}）")
        return generated_list[:count]

    def save_to_json(self, data: list[ToeicQuestionModel]):
        """將高階巢狀物件清單，完美序列化為 JSON 存檔"""
        try:
            # 🚀 利用 dataclasses.asdict 一鍵將整個巢狀物件拆解回 dict，準備寫入 JSON
            serialized_data = [dataclasses.asdict(m) for m in data]

            with open(self.output_dir, "w", encoding="utf-8") as f:
                json.dump(serialized_data, f, ensure_ascii=False, indent=2)

            dbg.log(f"💾 【結構化巢狀題庫匯出成功】檔案已成功寫入至: {self.output_dir}")
        except Exception as e:
            dbg.error(f"❌ 寫入 JSON 題庫檔案失敗: {e}")