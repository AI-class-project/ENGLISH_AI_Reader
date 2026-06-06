import json
from typing import TYPE_CHECKING

from core.const import OptionKey, ToeicQuestionCol
from core.engine.models import (QuestionOptions, ToeicQuestionModel,
                                ToeicSubQuestion)
from tool.debug import dbg

if TYPE_CHECKING:
    from tool.path import PathConfig

class ToeicPoolLoader:
    """題庫載入器：專門負責將本地 JSON 檔案還原為高階物件模型"""

    def __init__(self):
        pass

    def load_cached_pool(self, pool_path: "PathConfig") -> list[ToeicQuestionModel]:
        """讀取本地 JSON 檔案並全自動還原為 Model 物件清單"""
        if not pool_path.exists():
            dbg.error(f"❌ 找不到題庫檔案: {pool_path}，請先執行 batch_runner 生成題庫！")
            return []

        try:
            dbg.log(f"📖 正在讀取本地題庫檔案: {pool_path}")
            with open(pool_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

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

            dbg.log(f"✅ 成功載入並強型別封裝 {len(models_pool)} 組多益題組物件！")
            return models_pool

        except Exception as e:
            dbg.error(f"❌ 載入題庫檔案並轉換物件時發生崩潰: {e}")
            return []