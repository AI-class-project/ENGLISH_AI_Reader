from enum import StrEnum


class ToeicGenCol(StrEnum):
    """【輸入端】發射器控制參數專用 Key"""
    CATEGORY = "category"
    THEME = "theme"
    GRAMMAR_FOCUS = "grammar_focus"
    READING_RELATION = "reading_relation"

class ToeicQuestionCol(StrEnum):
    """【輸出端】AI 生成 JSON 與 DTO 物件欄位專用 Key"""
    CATEGORY = "category"
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