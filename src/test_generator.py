import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.batch_runner import ToeicBatchRunner
from core.loader import ToeicPoolLoader
from core.toeic_meta import MetaManager, QuestionType
from tool.debug import dbg


def run_end_to_end_pipeline_test():
    print("\n" + "="*60)
    dbg.log("🔥 [終極管線測試] 啟動多益 API 出題、儲存、提出並還原物件全流程測試")
    print("="*60)

    # --------------------------------------------------
    # 【前半段：出題與儲存】
    # --------------------------------------------------
    runner = ToeicBatchRunner()
    dbg.log("【1/3】向元資料中心索取［雙篇/多篇閱讀理解］配置藍圖...")
    multiple_reading_config = MetaManager.get_batch_config(QuestionType.READING_MULTIPLE)

    dbg.log("【2/3】啟動 AI 引擎進行批次出題與後台自動分水嶺文章切分...")
    # 這裡我們模擬生成 1 大組（內含 4~5 小題）
    pool_data = runner.generate_batch(count=4, config=multiple_reading_config)

    if not pool_data:
        dbg.error("❌ 前半段生成失敗，測試中斷")
        return

    dbg.log("【3/3】將生成數據結構化並寫入本地 JSON 緩存...")
    runner.save_to_json(pool_data)

    print("-" * 50)

    # --------------------------------------------------
    # 【後半段：提出 JSON、還原物件、UI 模擬印出】
    # --------------------------------------------------
    dbg.log("【4/6】實例化載入器，準備從本地檔案提出 JSON...")
    loader = ToeicPoolLoader()

    dbg.log("【5/6】執行反序列化，將 JSON 數據徹底封裝成強型別物件模型...")
    object_pool = loader.load_cached_pool()

    if not object_pool:
        dbg.error("❌ 後半段載入轉換失敗")
        return

    dbg.log("【6/6】［模擬 UI 端接收］正式對著物件取用屬性並印出畫面驗證...")
    for group_idx, exam_model in enumerate(object_pool):
        print(f"\n🖥️ ======= UI 渲染視窗 (第 {group_idx + 1} 組題組) =======")
        print(f"📌 題型分類: {exam_model.category}")

        # UI 取用明確的分水嶺文章清單
        print(f"📖 偵測到本題組包含 {len(exam_model.passages)} 篇文章：")
        for doc_idx, doc_text in enumerate(exam_model.passages):
            print(f"  --- [文章分頁 {doc_idx + 1}] ---")
            print(f"  {doc_text[:100]}... (略)") # 只印前100字代表分頁成功

        print(f"\n📝 右側子題目渲染：")
        # UI 取用子題目清單
        for sub_idx, sub_q in enumerate(exam_model.questions):
            print(f"  {sub_idx + 1}. {sub_q.question}")
            print(f"     (A) {sub_q.options.A}")
            print(f"     (B) {sub_q.options.B}")
            print(f"     (C) {sub_q.options.C}")
            print(f"     (D) {sub_q.options.D}")
            print(f"     👉 官方標準答案: [{sub_q.answer}]")
        print("==================================================\n")

    print("="*60)
    dbg.log("🏁 [測試結束] 全管線點火成功，後台與 UI 完美合約對接！")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_end_to_end_pipeline_test()