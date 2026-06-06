import random
from typing import Optional

from core.engine.batch_runner import ToeicBatchRunner
from core.engine.const import QuestionCategory
from core.engine.models import ToeicQuestionModel
from core.meta.toeic import MetaManager, QuestionType
from tool.debug import dbg


class ToeicQuestionFactory:
    """
    多益出題工廠 (Facade 模式)
    封裝複雜的引擎與劇本庫，對外提供極簡且強型別的 API
    """
    def __init__(self):
        self.runner = ToeicBatchRunner()

    def generate_questions(self, count: int, category: QuestionCategory = QuestionCategory.RANDOM) -> list[ToeicQuestionModel]:
        """
        一鍵生成題庫方法
        :param count: 想要生成的題組總數
        :param category: QuestionCategory Enum (預設為全境隨機)
        """
        dbg.log(f"🏭 [出題工廠] 啟動流水線！目標數量: {count}，指定大類: {category.name}")

        # 1. 依據 Enum 狀態，精準過濾允許抽籤的題型池
        allowed_types = list(QuestionType)

        if category == QuestionCategory.READING:
            allowed_types = [QuestionType.READING_SINGLE, QuestionType.READING_MULTIPLE]
        elif category == QuestionCategory.SINGLE_CHOICE:
            allowed_types = [QuestionType.VOCABULARY, QuestionType.GRAMMAR]
        # 若為 RANDOM，則維持全清單大亂鬥

        pool = []

        # 2. 啟動逐題抽籤流水線 (保證每一題的情境、考點都完全不同)
        for i in range(count):
            dbg.log(f"🔄 [工廠流水線] 正在調度第 {i+1}/{count} 題的劇本...")

            # 🎲 獨立抽籤決定本題的具體題型
            current_type = random.choice(allowed_types)

            # 🎲 向 MetaManager 索取專屬隨機劇本
            config = MetaManager.get_batch_config(current_type)

            # 🚀 呼叫 Runner 進行單次高規格生產
            result = self.runner.generate_batch(count=1, config=config)

            if result:
                pool.extend(result)
            else:
                dbg.war(f"⚠️ 第 {i+1} 題生產失敗，跳過。")

        # 3. 統一打包存檔
        if pool:
            dbg.log(f"📦 [出題工廠] 生產完畢！共產出 {len(pool)} 組題組，準備封裝寫入 JSON...")
            self.runner.save_to_json(pool)
        else:
            dbg.error("❌ [出題工廠] 生產線癱瘓，本次任務無任何產出。")

        return pool