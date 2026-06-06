from dataclasses import dataclass, field

from core.const import OptionKey, ToeicQuestionCol


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
    category: str    # 系統硬指標 (例如: "reading_multiple")
    theme: str       # 內容軟標籤 (例如: "Customer Complaints")
    passages: list[str] = field(default_factory=list)
    questions: list[ToeicSubQuestion] = field(default_factory=list)

    @classmethod
    def from_ai_dict(cls, ai_dict: dict) -> "ToeicQuestionModel":
        """
        AI 現在直接吐出巢狀字典
        """
        if not ai_dict:
            raise ValueError("AI 回傳的題目字典不可為空")

        sub_questions = []
        for q in ai_dict.get(ToeicQuestionCol.QUESTIONS.value, []):

            opts = q.get(ToeicQuestionCol.OPTIONS.value, {})

            options_obj = QuestionOptions(
                A=opts.get(OptionKey.A, ""),
                B=opts.get(OptionKey.B, ""),
                C=opts.get(OptionKey.C, ""),
                D=opts.get(OptionKey.D, "")
            )

            sub_questions.append(ToeicSubQuestion(
                question=q.get(ToeicQuestionCol.QUESTION.value, ""),
                options=options_obj,
                answer=q.get(ToeicQuestionCol.ANSWER.value, "").upper(),
                explanation=q.get(ToeicQuestionCol.EXPLANATION.value, "")
            ))

        return cls(
            category=ai_dict.get(ToeicQuestionCol.CATEGORY.value, "unknown"),
            theme=ai_dict.get(ToeicQuestionCol.THEME.value, "general"),
            passages=ai_dict.get(ToeicQuestionCol.PASSAGES.value, []),
            questions=sub_questions
        )