from core.engine.const import QuestionCategory
from core.engine.factory import ToeicQuestionFactory
from core.loader import ToeicPoolLoader
from tool.debug import dbg
from tool.path import PathConfig
from tool.update_meta import DynamicMetaUpdater


def run_factory():
    print("\n" + "="*60)
    dbg.log("🔥 [全系統實戰整合點火] 測試動態語料清洗 ➔ 工廠隨機出題 ➔ 強型別還原全管線")
    print("="*60)

    # --------------------------------------------------
    # 【階段 1：非同步語料庫即時更新 (ETL 管線點火)】
    # --------------------------------------------------
    dbg.log("📡 [E-T-L Pipeline] 正在調度動態語料更新器，衝去 BBC/CNBC 撈取今日即時新聞...")
    updater = DynamicMetaUpdater()

    updater.run_pipeline(max_items=10)

    print("\n" + "-"*50)
    dbg.log("⚡ 階段 1：今日新鮮語料已成功清洗並存入 dynamic_meta_pool.json！")
    print("-"*50 + "\n")

    # --------------------------------------------------
    # 【階段 2：出題工廠啟動 ➔ 自動配對新鮮語料】
    # --------------------------------------------------
    dbg.log("🏭 [Factory Pipeline] 啟動出題工廠，準備調度 MetaManager 機制...")
    factory = ToeicQuestionFactory()

    dbg.log("👤 使用者請求：給我 1 題『單選題』與 1 題『閱讀題』...")

    dbg.log("🔄 正在生產單選題大物件...")
    factory.generate_questions(count=1, category=QuestionCategory.SINGLE_CHOICE)

    dbg.log("🔄 正在生產閱讀題大物件...")
    factory.generate_questions(count=1, category=QuestionCategory.READING)

    # --------------------------------------------------
    # 【階段 3：持久化防線 ➔ 透過 Loader 強型別還原驗證】
    # --------------------------------------------------
    print("\n" + "-"*50)
    dbg.log("📖 階段 3：驗證 toeic_pool.json 最終覆蓋存檔結果與型別完整性...")
    print("-"*50 + "\n")

    loader = ToeicPoolLoader()
    verified_pool = loader.load_cached_pool(PathConfig.TOEIC_POOL)

    if not verified_pool:
        dbg.error("❌ 嚴重錯誤：最終還原題庫 pool 為空，請檢查儲存或模型轉換端！")
        return

    dbg.log("🖥️  [題庫還原成功] 正式對著產出的強型別物件進行結構複查：")
    for idx, model in enumerate(verified_pool):
        print(f"   [題組 {idx+1}]")
        print(f"   📂 系統核心題型 (Category) : {model.category}")
        print(f"   📌 今日新聞實事主題 (Theme) : {model.theme}")
        print(f"   📝 包含子題目數量 (Questions): {len(model.questions)} 題")

        if model.questions:
            print(f"   👉 小題 1 搶先看: {model.questions[0].question[:60]}...")
        print("-" * 40)

    print("="*60)
    dbg.log("🏁 [終極完全體測試成功] 從真實世界時事到強型別題庫，全自動化大閉環完美通車！")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_factory()