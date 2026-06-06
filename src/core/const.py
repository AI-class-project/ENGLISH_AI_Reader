from enum import StrEnum


class ToeicGenCol(StrEnum):
    CATEGORY = "category"
    THEME = "theme"
    GRAMMAR_FOCUS = "grammar_focus"
    READING_RELATION = "reading_relation"

class ToeicQuestionCol(StrEnum):
    """AI 回傳題目 JSON 欄位的專用 Key (徹底消滅魔法字串)"""
    CATEGORY = "category"
    PASSAGE = "passage"
    QUESTION = "question"

    # 選項原始欄位
    OPTION_A = "option_a"
    OPTION_B = "option_b"
    OPTION_C = "option_c"
    OPTION_D = "option_d"

    ANSWER = "answer"
    EXPLANATION = "explanation"
