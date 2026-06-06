import json

from core.models import QuestionOptions, ToeicQuestionModel, ToeicSubQuestion
from tool.debug import dbg
from tool.path import PathConfig


class ToeicPoolLoader:
    """題庫載入器：專門負責將本地 JSON 檔案還原為高階物件模型"""

    def __init__(self):
        self.pool_path = PathConfig.TOEIC_POOL

    def load_cached_pool(self) -> list[ToeicQuestionModel]:
        """讀取本地 JSON 檔案並全自動還原為 Model 物件清單"""
        if not self.pool_path.exists():
            dbg.error(f"❌ 找不到題庫檔案: {self.pool_path}，請先執行 batch_runner 生成題庫！")
            return []

        try:
            dbg.log(f"📖 正在讀取本地題庫檔案: {self.pool_path}")
            with open(self.pool_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            models_pool = []
            for chunk in raw_data:
                # 💡 對齊純字串合約，直接使用一般字串提取資料
                sub_qs = []
                for q in chunk.get("questions", []):
                    opts = q.get("options", {})

                    # 提取選項
                    options_obj = QuestionOptions(
                        A=opts.get("A", ""),
                        B=opts.get("B", ""),
                        C=opts.get("C", ""),
                        D=opts.get("D", "")
                    )

                    # 提取子題目核心屬性
                    sub_qs.append(ToeicSubQuestion(
                        question=q.get("question", ""),
                        options=options_obj,
                        answer=q.get("answer", ""),
                        explanation=q.get("explanation", "")
                    ))

                # 組裝頂層大物件
                model_obj = ToeicQuestionModel(
                    category=chunk.get("category", "未定義題型"),
                    passages=chunk.get("passages", []),
                    questions=sub_qs
                )
                models_pool.append(model_obj)

            dbg.log(f"✅ 成功載入並強型別封裝 {len(models_pool)} 組多益題組物件！")
            return models_pool

        except Exception as e:
            dbg.error(f"❌ 載入題庫檔案並轉換物件時發生崩潰: {e}")
            return []