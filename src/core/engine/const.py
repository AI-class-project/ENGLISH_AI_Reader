from enum import StrEnum


class QuestionCategory(StrEnum):
    """
    工廠專用的廣義題型分類 Enum (徹底消滅中文魔法字串)
    """
    READING = "reading"
    SINGLE_CHOICE = "single_choice"
    RANDOM = "random"