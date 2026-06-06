import json
import random
from dataclasses import dataclass
from enum import StrEnum

from core.const import ToeicGenCol
from tool.debug import dbg
from tool.path import PathConfig


class QuestionType(StrEnum):
    """多益題型嚴格定義 (使用 Enum 防呆)"""
    VOCABULARY = "單字克漏字"
    GRAMMAR = "文法選擇"
    READING_SINGLE = "單篇閱讀理解"
    READING_MULTIPLE = "雙篇/多篇閱讀理解"

    @classmethod
    def get_all_type(cls):
        return [member for member in cls]

@dataclass(frozen=True)
class ToeicMetaPool:
    """多益出題情境與考點資料庫"""

    # 1. 商業情境庫
    THEME_MATRIX = {
        "辦公室日常與人事公告 (Office & HR Announcement)": [
            "office renovation causing temporary noise disturbance", # 環境景色
            "annual local charity marathon sponsorship",           # 社交日常
            "implementation of a new remote work flexible policy"
        ],
        "客戶投訴與售後服務 (Customer Complaints & Service)": [
            "unacceptable billing discrepancy on the monthly invoice",
            "rude behavior from a delivery courier last Tuesday",
            "received damaged wooden office desk with scratches"
        ],
        "國際商務出差與行程安排 (Business Travel & Itinerary)": [
            "flight cancellation due to a sudden severe blizzard",   # 天氣情境
            "hotel overbooking during the peak conference season",
            "heavy monsoon rainfall causing train schedule delays"  # 天氣情境
        ],
        "廠房公安與生產線維護 (Factory Safety & Maintenance)": [
            "upgraded facility ventilation system inspection",      # 廠房景色
            "mandatory chemical spill emergency drill next Thursday", # 突發公安
            "replacing worn-out conveyor belts on the assembly floor"
        ],
        "跨部門電子郵件溝通 (Interdepartmental Email Communication)": [
            "server room air conditioning failure causing system lag", # 環境突發
            "coordinating the catering menu for the upcoming banquet",
            "relocating the design team to the newly painted West Wing" # 景色空間
        ]
    }

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

    # 4. 高頻多益英文人名庫
    CHARACTERS = [
        "Elena Rostova", "David Vance", "Chloe Laurent", "Kenji Tanaka",
        "Amara Diallo", "Oliver Sterling", "Sofia Martinez", "Vikram Patel",
        "Rachel Green", "Simon de Almeida", "Fiona Gallagher", "Nolan Ross"
    ]



class MetaManager:
    """負責提供各種隨機組合的管理器（具備策略二自動降級機制）"""

    @staticmethod
    def _get_active_theme_matrix() -> dict:
        """
        核心防線：嘗試讀取策略二網頁動態語料，若失手則無縫降級回靜態備援池
        """
        dynamic_path = PathConfig.DYNAMIC_META_POOL

        if dynamic_path and dynamic_path.exists():
            try:
                with open(dynamic_path, "r", encoding="utf-8") as f:
                    dynamic_matrix = json.load(f)
                    if isinstance(dynamic_matrix, dict) and dynamic_matrix:
                        # 策略二點火成功：完美使用即時網頁語料情境
                        return dynamic_matrix
            except Exception as e:
                dbg.war(f"⚠️ 策略二動態語料讀取失敗 ({e})，自動啟動靜態備援防線。")

        # 策略二失手時，無縫使用目前的靜態矩陣庫
        return ToeicMetaPool.THEME_MATRIX

    @staticmethod
    def get_random_theme() -> str:
        """隨機抽取一個商務情境 """
        matrix = MetaManager._get_active_theme_matrix()
        return random.choice(list(matrix.keys()))

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
        根據指定的題型，動態分流並注入【動態網頁/靜態備援】的強型別安全變數配置
        """
        matrix = MetaManager._get_active_theme_matrix()
        chosen_theme = random.choice(list(matrix.keys()))
        specific_context = random.choice(matrix[chosen_theme])
        chars = random.sample(ToeicMetaPool.CHARACTERS, k=2)

        config = {
            ToeicGenCol.CATEGORY: category.value,
            ToeicGenCol.THEME: chosen_theme,
            ToeicGenCol.FORCED_CONTEXT: specific_context,
            ToeicGenCol.FORCED_CHAR_1: chars[0],
            ToeicGenCol.FORCED_CHAR_2: chars[1],
            ToeicGenCol.FORCED_DATE: f"{random.choice(['January', 'April', 'July', 'October'])} {random.randint(1, 28)}"
        }

        if category == QuestionType.GRAMMAR:
            config[ToeicGenCol.GRAMMAR_FOCUS] = MetaManager.get_random_grammar_focus()

        if category == QuestionType.READING_MULTIPLE:
            config[ToeicGenCol.READING_RELATION] = MetaManager.get_random_reading_relation()

        return config