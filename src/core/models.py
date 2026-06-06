import re
from dataclasses import dataclass, field

from core.const import ToeicQuestionCol


@dataclass(frozen=True)
class QuestionOptions:
    A: str; B: str; C: str; D: str

@dataclass(frozen=True)
class ToeicSubQuestion:
    question: str
    options: QuestionOptions
    answer: str
    explanation: str

@dataclass(frozen=True)
class ToeicQuestionModel:
    """
    多益題組的終極通用介面
    完美整合單字、文法與多篇閱讀理解
    """
    category: str
    passages: list[str] = field(default_factory=list)
    questions: list[ToeicSubQuestion] = field(default_factory=list)

    @classmethod
    def from_ai_dict(cls, ai_dict: dict) -> "ToeicQuestionModel":
        """
        AI 現在直接吐出巢狀字典，我們只需做極輕量的防呆轉型
        """
        if not ai_dict:
            raise ValueError("AI 回傳的題目字典不可為空")

        sub_questions = []
        for q in ai_dict.get("questions", []):
            opts = q.get("options", {})
            options_obj = QuestionOptions(
                A=opts.get("A", ""),
                B=opts.get("B", ""),
                C=opts.get("C", ""),
                D=opts.get("D", "")
            )
            sub_questions.append(ToeicSubQuestion(
                question=q.get("question", ""),
                options=options_obj,
                answer=q.get("answer", "").upper(),
                explanation=q.get("explanation", "")
            ))

        return cls(
            category=ai_dict.get("category", "未定義題型"),
            passages=ai_dict.get("passages", []),
            questions=sub_questions
        )