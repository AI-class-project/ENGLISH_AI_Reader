from core.const import OptionKey, ToeicQuestionCol
from core.engine.models import (QuestionOptions, ToeicQuestionModel,
                                ToeicSubQuestion)
from core.storage.toeic_repo import ToeicQuestionRepository
from tool.debug import dbg


class ToeicPoolLoader:
    """題庫載入器：負責將 Supabase 題庫還原為高階物件模型"""

    def __init__(self):
        self.repo = ToeicQuestionRepository()

    def load_cached_pool(self) -> list[ToeicQuestionModel]:
        """
        從 Supabase 載入。
        """
        try:
            dbg.log("📖 正在從 Supabase 讀取題庫")
            raw_data = self.repo.load_all_question_groups()

            models_pool = []

            for chunk in raw_data:
                sub_qs = []

                for q in chunk.get(ToeicQuestionCol.QUESTIONS.value, []):
                    opts = q.get(ToeicQuestionCol.OPTIONS.value, {})

                    options_obj = QuestionOptions(
                        A=opts.get(OptionKey.A.value, ""),
                        B=opts.get(OptionKey.B.value, ""),
                        C=opts.get(OptionKey.C.value, ""),
                        D=opts.get(OptionKey.D.value, "")
                    )

                    sub_qs.append(ToeicSubQuestion(
                        question=q.get(ToeicQuestionCol.QUESTION.value, ""),
                        options=options_obj,
                        answer=q.get(ToeicQuestionCol.ANSWER.value, ""),
                        explanation=q.get(ToeicQuestionCol.EXPLANATION.value, "")
                    ))

                model_obj = ToeicQuestionModel(
                    category=chunk.get(ToeicQuestionCol.CATEGORY.value, "未定義題型"),
                    theme=chunk.get(ToeicQuestionCol.THEME.value, "未定義主題"),
                    passages=chunk.get(ToeicQuestionCol.PASSAGES.value, []),
                    questions=sub_qs
                )

                models_pool.append(model_obj)

            dbg.log(f"✅ 成功從 Supabase 載入並封裝 {len(models_pool)} 組多益題組物件")
            return models_pool

        except Exception as e:
            dbg.error(f"❌ 從 Supabase 載入題庫並轉換物件時發生錯誤: {e}")
            return []