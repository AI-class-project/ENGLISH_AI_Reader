from enum import StrEnum


class ToeicGenCol(StrEnum):
    """【輸入端】發射器控制參數專用 Key"""
    CATEGORY = "category"
    THEME = "theme"
    GRAMMAR_FOCUS = "grammar_focus"
    READING_RELATION = "reading_relation"

    FORCED_CONTEXT = "forced_context"
    FORCED_CHAR_1 = "forced_char_1"
    FORCED_CHAR_2 = "forced_char_2"
    FORCED_DATE = "forced_date"

class ToeicQuestionCol(StrEnum):
    """【輸出端】AI 生成 JSON 與 DTO 物件欄位專用 Key"""
    CATEGORY = "category"
    THEME = "theme"
    PASSAGES = "passages"
    QUESTIONS = "questions"
    QUESTION = "question"
    OPTIONS = "options"
    ANSWER = "answer"
    EXPLANATION = "explanation"

class OptionKey(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"