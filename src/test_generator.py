import os
import sys

# 確保 Python 執行時能正確將 src 的上一層（專案根目錄）加入路徑
# 這樣在不同資料夾下執行都不會噴出 ModuleNotFoundError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import ToeicGenerator
from tool.debug import dbg


def run_pipeline_test():
    """執行生成引擎的核心管線測試"""
    print("\n" + "="*60)
    dbg.log("🚀 [開始測試] 啟動多益 AI 出題引擎管線功能綜合測試")
    print("="*60)

    try:
        # 1. 測試引擎初始化
        dbg.log("1. 正在嘗試實例化 ToeicGenerator...")
        engine = ToeicGenerator()

        # 2. 測試單字克漏字題型 (Passage 應該為空)
        dbg.log("2. [功能測試] 嘗試生成【單字克漏字】題型...")
        vocab_result = engine.generate_question(category="單字克漏字", theme="商業採購合約")

        if vocab_result:
            dbg.log("🎉 【單字克漏字】測試成功！")
            # 檢查防呆：單字題文章欄位必須為空
            if vocab_result.get("passage") != "":
                dbg.war(f"⚠️ 警告：單字題的 passage 欄位不為空，內容為: {vocab_result.get('passage')}")
        else:
            dbg.error("❌ 【單字克漏字】生成失敗，未取得回傳資料。")

        print("-" * 50)

        # 3. 測試閱讀理解題型 (Passage 應該要有文章)
        dbg.log("3. [功能測試] 嘗試生成【閱讀理解】題型...")
        reading_result = engine.generate_question(category="閱讀理解", theme="公司人事變動公告")

        if reading_result:
            dbg.log("🎉 【閱讀理解】測試成功！")
            # 檢查防呆：閱讀題必須要有文章內容
            if not reading_result.get("passage"):
                dbg.war("⚠️ 警告：閱讀理解題型的 passage 欄位居然是空的！")
        else:
            dbg.error("❌ 【閱讀理解】生成失敗，未取得回傳資料。")

    except Exception as e:
        import traceback
        dbg.error(f"🚨 測試管線中途發生毀滅性崩潰: {e}")
        print(traceback.format_exc())

    print("="*60)
    dbg.log("🏁 [測試結束] 診斷程序執行完畢")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_pipeline_test()