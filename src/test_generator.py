from core.batch_runner import ToeicBatchRunner
from core.meta.toeic import MetaManager, QuestionType
from tool.debug import dbg


def run_batch_pipeline_test():
    """驗證結合元資料中心 (Meta) 與批次工具 (Runner) 的全新管線測試"""
    print("\n" + "="*60)
    dbg.log("🚀 [開始測試] 啟動多益全自動出題管線綜合測試")
    print("="*60)

    try:
        # 初始化批次運行器
        runner = ToeicBatchRunner()

        # 1. 測試隨機文法選擇題批次生成
        dbg.log("1. [文法選擇] 測試隨機配置生成...")
        grammar_config = MetaManager.get_batch_config(QuestionType.GRAMMAR)

        # 執行生成 (數量給 2 題快速驗證即可)
        grammar_pool = runner.generate_batch(count=2, config=grammar_config)

        if grammar_pool:
            dbg.log(f"🎉 [文法選擇] 順利產出 {len(grammar_pool)} 題！")
        else:
            dbg.error("❌ [文法選擇] 生成失敗，未取得有效池資料。")

        print("-" * 50)

        # 2. 測試隨機單字克漏字批次生成
        dbg.log("2. [單字克漏字] 測試隨機配置生成...")
        vocab_config = MetaManager.get_batch_config(QuestionType.VOCABULARY)

        vocab_pool = runner.generate_batch(count=2, config=vocab_config)

        if vocab_pool:
            dbg.log(f"🎉 [單字克漏字] 順利產出 {len(vocab_pool)} 題！")
        else:
            dbg.error("❌ [單字克漏字] 生成失敗，未取得有效池資料。")

        # 3. 統一打包存檔測試 (會融合文法與單字)
        if grammar_pool or vocab_pool:
            total_pool = (grammar_pool or []) + (vocab_pool or [])
            dbg.log(f"3. [存檔測試] 正在將總計 {len(total_pool)} 題寫入本地儲存區...")
            runner.save_to_json(total_pool)

    except Exception as e:
        import traceback
        dbg.error(f"🚨 測試管線中途發生毀滅性崩潰: {e}")
        print(traceback.format_exc())

    print("="*60)
    dbg.log("🏁 [測試結束] 診斷程序執行完畢")
    print("="*60 + "\n")

if __name__ == "__main__":
    runner = ToeicBatchRunner()

    # 測試最高殿堂：隨機抽取「雙篇/多篇閱讀理解」配置！
    dbg.log("🔥 正在索取【雙篇/多篇閱讀理解】全自動配置藍圖...")
    multiple_reading_config = MetaManager.get_batch_config(QuestionType.READING_MULTIPLE)

    # 執行生成 4 題
    pool = runner.generate_batch(count=4, config=multiple_reading_config)

    if pool:
        runner.save_to_json(pool)