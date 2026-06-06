from core.engine.const import QuestionCategory
from core.engine.factory import ToeicQuestionFactory
from core.loader import ToeicPoolLoader
from tool.debug import dbg
from tool.path import PathConfig


def run_factory():
    print("\n" + "="*60)
    dbg.log("[出題工廠點火] 測試強型別 Enum API 調用")
    print("="*60)

    factory = ToeicQuestionFactory()

    factory.generate_questions(count=2, category=QuestionCategory.SINGLE_CHOICE)

    print("\n" + "-"*50)
    dbg.log("📖 驗證存檔結果...")

    loader = ToeicPoolLoader()
    verified_pool = loader.load_cached_pool(PathConfig.TOEIC_POOL)

    for idx, model in enumerate(verified_pool):
        print(f"✅ 第 {idx+1} 題載入成功 | 題型: {model.category} | 包含 {len(model.questions)} 小題")

    print("="*60 + "\n")

if __name__ == "__main__":
    run_factory()
