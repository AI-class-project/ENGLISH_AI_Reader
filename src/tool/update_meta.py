import json

import feedparser
from google import genai
from google.genai import types

from core.llm.security import KeyManager
from tool.debug import dbg
from tool.path import PathConfig


class DynamicMetaUpdater:
    """非同步語料庫更新管線 (ETL Pipeline)"""

    # 鎖定您的五大核心情境，讓 AI 只能分發到這些類別
    TARGET_THEMES = [
        "辦公室日常與人事公告 (Office & HR Announcement)",
        "客戶投訴與售後服務 (Customer Complaints & Service)",
        "國際商務出差與行程安排 (Business Travel & Itinerary)",
        "廠房公安與生產線維護 (Factory Safety & Maintenance)",
        "跨部門電子郵件溝通 (Interdepartmental Email Communication)",
        "採購合約與供應商談判 (Purchasing & Supplier Contracts)",
        "產品發表與行銷企劃 (Product Launch & Marketing Campaign)",
        "公司財務報表與預算會議 (Financial Reports & Budget Planning)",
        "餐飲宴會與商務社交日常 (Catering, Banquets & Corporate Socials)",
        "物流倉儲與交通異動通知 (Logistics, Warehousing & Transit Updates)"
    ]

    # 精準化多益語料 RSS 來源池 (全面覆蓋零售、科技、航空、旅遊、人力資源等日常商務層面)
    RSS_FEEDS = [
        # 1. 綜合商務與總體經濟 (主力基本盤)
        "http://feeds.bbci.co.uk/news/business/rss.xml",                         # BBC Business
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?id=10001147",   # CNBC Technology & Business

        # 2. 國際出差、航空異動與旅遊情境 (專攻：Business Travel 題型)
        "https://www.businesstravelnews.com/rss/all",                           # Business Travel News
        "https://www.aviation24.be/feed/",                                      # Aviation24 (即時航班、機場突發異動)

        # 3. 零售行銷、採購、產品發表與供應職缺 (專攻：Marketing & Job Advertisement)
        "https://www.retaildive.com/feeds/news/",                               # Retail Dive (零售、產品上市、供應鏈)
        "https://www.marketingdive.com/feeds/news/",                             # Marketing Dive (廣告行銷、企劃案異動)

        # 4. 人事公告、辦公日常與跨部門溝通 (專攻：Office HR & Management)
        "https://www.hrdive.com/feeds/news/",                                    # HR Dive (人資管理、辦公室新政策、薪酬福利)

        # 5. 廠房維護、公安與科技研發 (專攻：Factory Safety & Tech Update)
        "https://www.manufacturing.net/home/rss/20864380/manufacturingnet",     # Manufacturing.net (製造業、廠房安全維護)
    ]

    def __init__(self):
        # 取得金鑰並初始化輕量級模型
        keys = KeyManager.get_gemini_keys()
        if not keys:
            raise ValueError("無可用 API Key")

        self.client = genai.Client(api_key=keys[0])

        # 清洗語料用 Flash 即可，速度快成本低
        self.model_name = 'models/gemini-2.5-flash'
        self.output_path = PathConfig.DYNAMIC_META_POOL

    def fetch_raw_news(self, max_items: int) -> list[str]:
        """[Extract] 從 RSS 獲取最新商務新聞摘要 (已修正總數限制盲點)"""
        dbg.log("📡 [Extract] 開始從 RSS 來源抓取真實商務新聞...")
        raw_texts = []

        for url in self.RSS_FEEDS:
            # 如果在外迴圈發現總數已經達標，直接收工，連下一站的網頁都不用解碼
            if len(raw_texts) >= max_items: break

            feed = feedparser.parse(url)

            for entry in feed.entries:
                # 每成功塞入一條，就檢查是否達到總數上限
                if len(raw_texts) >= max_items:
                    break

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                if title and summary:
                    raw_texts.append(f"Title: {title} | Summary: {summary}")

        dbg.log(f"✅ 成功抓取 {len(raw_texts)} 條新聞素材 (嚴格符合總數上限)。")
        return raw_texts

    def transform_to_toeic_matrix(self, raw_texts: list[str]) -> dict:
        """[Transform] 批次化升級版：將所有新聞打包一次送出，徹底絕殺 429 限流問題"""
        dbg.log("🧠 [Transform] 啟動工業級『批次打包』清洗與分類程序...")

        dynamic_matrix = {theme: [] for theme in self.TARGET_THEMES}

        # 建立結構化的系統提示詞，強制要求 AI 吞下一個陣列，並吐出一個結構化的結果陣列
        system_prompt = f"""
        你是一位高階多益測驗語料庫清洗專家。
        我會提供你一個包含多條真實商務新聞的清單。請你閱讀完畢後，為每一條新聞執行：
        1. 判斷它最適合歸類到以下哪一個多益標準情境：
           {json.dumps(self.TARGET_THEMES, ensure_ascii=False)}
        2. 將新聞內容精煉成 1 句（20 個英文字以內）的「多益風格背景描述（環境/突發事件/商業動態）」。

        【強制要求】
        你必須直接輸出一個標準的 JSON 物件 (外層為 {{ ... }})，內部包含一個名為 "results" 的陣列。

        【JSON 結構規格】
        {{
            "results": [
                {{
                    "category": "上述五大情境擇一",
                    "context": "1 句簡短的英文背景描述"
                }}
            ]
        }}
        """

        # 將條新聞合併成一個有條理的文本 block
        user_content = "請批次處理以下新聞清單：\n"
        for i, text in enumerate(raw_texts):
            user_content += f"[{i + 1}] {text}\n"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )

            raw_json = json.loads(response.text)
            results_list = raw_json.get("results", [])

            dbg.log(f"📥 AI 批次處理完畢，開始分發 {len(results_list)} 條結果...")

            for result in results_list:
                category = result.get("category")
                context = result.get("context")

                if category in self.TARGET_THEMES and context:
                    dynamic_matrix[category].append(context)
                    dbg.log(f"   ↳ 批次萃取成功 [{category}]: {context}")

        except Exception as e:
            dbg.error(f"❌ 批次處理新聞時發生嚴重崩潰: {e}")

        # 過濾掉空陣列
        clean_matrix = {k: v for k, v in dynamic_matrix.items() if len(v) > 0}
        return clean_matrix

    def save_to_json(self, matrix: dict):
        """將清洗好的動態矩陣寫入 JSON"""
        if not matrix:
            dbg.error("❌ 清洗後的矩陣為空，中止寫入。")
            return

        dbg.log("💾 [Load] 準備將動態情境庫覆寫至本地儲存...")
        try:
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(matrix, f, ensure_ascii=False, indent=2)
            dbg.log(f"🎉 動態語料庫更新完成！檔案位置: {self.output_path}")
        except Exception as e:
            dbg.error(f"寫入 JSON 失敗: {e}")

    def run_pipeline(self, max_items: int = 15):
        print("\n" + "="*50)
        dbg.log("🚀 啟動非同步語料清洗管線")
        print("="*50)

        raw_news = self.fetch_raw_news(max_items=max_items)
        if not raw_news: return

        matrix = self.transform_to_toeic_matrix(raw_news)
        self.save_to_json(matrix)
