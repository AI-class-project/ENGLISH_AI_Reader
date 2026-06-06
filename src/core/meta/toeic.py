import random
from dataclasses import dataclass
from enum import StrEnum

from core.const import ToeicGenCol


class QuestionType(StrEnum):
    """多益題型嚴格定義 (使用 Enum 防呆)"""
    VOCABULARY = "單字克漏字"
    GRAMMAR = "文法選擇"
    READING_SINGLE = "單篇閱讀理解"
    READING_MULTIPLE = "雙篇/多篇閱讀理解"

@dataclass(frozen=True)
class ToeicMetaPool:
    """多益出題情境與考點資料庫"""

    # 1. 商業情境庫
    THEMES = [
        "辦公室日常與人事公告 (Office & HR Announcement)",
        "採購合約與供應商談判 (Purchasing & Supplier Contracts)",
        "產品發表與行銷企劃 (Product Launch & Marketing)",
        "客戶投訴與售後服務 (Customer Complaints & Service)",
        "國際商務出差與行程安排 (Business Travel & Itinerary)",
        "公司財務報表與預算會議 (Financial Reports & Budgets)",
        "廠房公安與生產線維護 (Factory Safety & Maintenance)",
        "跨部門電子郵件溝通 (Interdepartmental Email Communication)"
    ]

    # 2. 文法考點庫 (Grammar Focus)
    GRAMMAR_FOCUSES = [
        "動詞時態 (例如: 現在完成式、過去完成式、進行式)",
        "主動與被動語態的辨析 (Active vs. Passive voice)",
        "不定詞 (to V) 與動名詞 (V-ing) 的選用",
        "分詞當形容詞使用 (例如: boring vs. bored, confusing vs. confused)",
        "關係代名詞與關係副詞 (who, which, that, whose, where, when)",
        "連接詞與介係詞的辨析 (例如: Although vs. Despite, Because of vs. Since)",
        "假設語氣 (If 子句與 suggest/demand 後省略 should 的用法)",
        "比較級與最高級的修飾 (例如: much more, by far the best)"
    ]

    # 3. 多篇閱讀關聯庫 (Article Relations)
    READING_RELATIONS = [
        "一篇廣告宣傳單 (Advertisement) + 一篇顧客抱怨信 (Complaint Email)",
        "一篇公司內部公告 (Memo) + 一篇員工詢問回覆 (Reply Email)",
        "一篇徵才啟事 (Job Advertisement) + 一篇應徵者求職信 (Cover Letter)",
        "一篇活動行程表 (Schedule) + 一篇異動通知信 (Change Notice)"
    ]

class MetaManager:
    """負責提供各種隨機組合的管理器"""

    @staticmethod
    def get_random_theme() -> str:
        """隨機抽取一個商務情境"""
        return random.choice(ToeicMetaPool.THEMES)

    @staticmethod
    def get_random_grammar_focus() -> str:
        """隨機抽取一個文法考點"""
        return random.choice(ToeicMetaPool.GRAMMAR_FOCUSES)

    @staticmethod
    def get_random_reading_relation() -> str:
        """隨機抽取多篇閱讀的文章關聯結構"""
        return random.choice(ToeicMetaPool.READING_RELATIONS)

    @staticmethod
    def get_batch_config(category: QuestionType) -> dict:
        """
        根據指定的題型，回傳一次完整的生成配置。
        這可以讓外部的 batch_runner 直接拿到設定好的劇本。
        """
        config = {
            ToeicGenCol.CATEGORY: category.value,
            ToeicGenCol.THEME: MetaManager.get_random_theme()
        }

        # 如果是文法題，多給一個文法考點
        if category == QuestionType.GRAMMAR:
            config[ToeicGenCol.GRAMMAR_FOCUS] = MetaManager.get_random_grammar_focus()

        # 如果是多篇閱讀，多給一個文章結構要求
        if category == QuestionType.READING_MULTIPLE:
            config[ToeicGenCol.READING_RELATION] = MetaManager.get_random_reading_relation()

        return config