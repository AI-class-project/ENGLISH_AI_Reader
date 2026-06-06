from core.const import ToeicGenCol
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
        dbg.log(f"🏭 [出題工廠] 啟動開發者批次流水線！目標總數: {count}，指定大類: {category.name}")

        # 1. 決定允許指派的具體多益子題型
        allowed_types = list(QuestionType)
        if category == QuestionCategory.READING:
            allowed_types = [QuestionType.READING_SINGLE, QuestionType.READING_MULTIPLE]
        elif category == QuestionCategory.SINGLE_CHOICE:
            allowed_types = [QuestionType.VOCABULARY, QuestionType.GRAMMAR]

        # 2. 直接獲取 count 個「絕對不重複、依序排列」的新鮮語料劇本
        script_blueprints = MetaManager.get_sequential_configs(count, allowed_types)

        pool = []

        # 3. 依序推入生產線，確保每一條被抓下來的新聞都得到完美利用
        for idx, config in enumerate(script_blueprints):
            dbg.log(f"🔄 [工廠流水線] 正在消化第 {idx+1}/{count} 條網頁時事提示詞...")
            dbg.log(f"   ↳ 分配題型: [{config.get(ToeicGenCol.CATEGORY)}] | 時事核心: {config.get(ToeicGenCol.FORCED_CONTEXT)[:50]}...")

            result = self.runner.generate_batch(count=1, config=config)

            if result:
                pool.extend(result)
            else:
                dbg.war(f"⚠️ 第 {idx+1} 題生產失敗，跳過。")

        # 4. 統一存檔覆蓋
        if pool:
            dbg.log(f"📦 [出題工廠] 生產完畢！共產出 {len(pool)} 組題組，交付寫入儲存...")
            self.runner.save_to_json(pool)
        else:
            dbg.error("❌ [出題工廠] 本次任務完全無產出。")

        return pool