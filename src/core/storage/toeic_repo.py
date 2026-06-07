import dataclasses
import hashlib

from core.const import ToeicQuestionCol
from core.engine.config import GENERATE_BATCH_CONFIG
from core.engine.models import ToeicQuestionModel
from core.storage.supabase_client import SupabaseManager
from tool.debug import dbg


class ToeicQuestionRepository:
    QUESTION_TABLE = "toeic_questions"
    FINGERPRINT_TABLE = "toeic_question_fingerprints"

    def __init__(self):
        self.client = SupabaseManager.get_client()

    def _build_fingerprint(self, passage_prefix: str, question_text: str) -> str:
        unique_feature = f"{passage_prefix}_{question_text}"
        return hashlib.md5(unique_feature.encode("utf-8")).hexdigest()

    def load_all_question_groups(self) -> list[dict]:
        """
        從 Supabase 載入所有題組。
        注意：Supabase 預設單次最多 1000 筆，這裡先做分頁。
        """
        all_rows = []
        page_size = 1000
        start = 0

        while True:
            end = start + page_size - 1

            response = (
                self.client
                .table(self.QUESTION_TABLE)
                .select("category, theme, passages, questions, created_at")
                .order("created_at", desc=False)
                .range(start, end)
                .execute()
            )

            rows = response.data or []
            all_rows.extend(rows)

            if len(rows) < page_size:
                break

            start += page_size

        dbg.log(f"📖 已從 Supabase 載入 {len(all_rows)} 組題組")
        return all_rows

    def load_all_fingerprints(self) -> set[str]:
        """
        從 Supabase 載入所有歷史題目指紋，用於防止重複出題。
        """
        fingerprints = set()
        page_size = 1000
        start = 0

        while True:
            end = start + page_size - 1

            response = (
                self.client
                .table(self.FINGERPRINT_TABLE)
                .select("fingerprint")
                .range(start, end)
                .execute()
            )

            rows = response.data or []

            for row in rows:
                fp = row.get("fingerprint")
                if fp:
                    fingerprints.add(fp)

            if len(rows) < page_size:
                break

            start += page_size

        dbg.log(f"🛡️ 已從 Supabase 載入 {len(fingerprints)} 筆歷史題目指紋")
        return fingerprints

    def insert_question_groups(self, data: list[ToeicQuestionModel]):
        """
        將 Gemini 生成的新題組寫入 Supabase。
        """
        if not data:
            dbg.war("⚠️ 沒有可寫入 Supabase 的題組")
            return

        for model in data:
            question_group = dataclasses.asdict(model)

            insert_response = (
                self.client
                .table(self.QUESTION_TABLE)
                .insert({
                    "category": question_group.get("category", "未定義題型"),
                    "theme": question_group.get("theme", "未定義主題"),
                    "passages": question_group.get("passages", []),
                    "questions": question_group.get("questions", []),
                })
                .execute()
            )

            inserted_rows = insert_response.data or []
            if not inserted_rows:
                dbg.war("⚠️ 題組寫入 Supabase 後沒有回傳資料，略過指紋寫入")
                continue

            toeic_question_id = inserted_rows[0]["id"]

            passages = question_group.get("passages", [])
            questions = question_group.get("questions", [])

            passage_prefix = (
                passages[0][:GENERATE_BATCH_CONFIG.PASSAGE_PREFIX_MAX]
                if passages else ""
            )

            fingerprint_rows = []

            for q in questions:
                q_text = q.get("question", "").strip()
                if not q_text:
                    continue

                fingerprint_rows.append({
                    "fingerprint": self._build_fingerprint(passage_prefix, q_text),
                    "toeic_question_id": toeic_question_id,
                })

            if fingerprint_rows:
                (
                    self.client
                    .table(self.FINGERPRINT_TABLE)
                    .upsert(
                        fingerprint_rows,
                        on_conflict="fingerprint",
                        ignore_duplicates=True
                    )
                    .execute()
                )

        dbg.log(f"💾 【Supabase 題庫寫入成功】本次新增 {len(data)} 組題組")