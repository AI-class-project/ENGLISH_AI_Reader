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
    多益題目的終極通用介面 (多文章 List 升級版)
    """
    category: str
    passages: list[str] = field(default_factory=list)
    questions: list[ToeicSubQuestion] = field(default_factory=list)

    @classmethod
    def from_ai_chunk(cls, ai_chunk: list[dict]) -> "ToeicQuestionModel":
        if not ai_chunk:
            raise ValueError("AI 回傳的題目資料塊不可為空")

        base_data = ai_chunk[0]
        category = base_data.get(ToeicQuestionCol.CATEGORY.value, "未定義題型")
        raw_passage = base_data.get(ToeicQuestionCol.PASSAGE.value, "").strip()

        # 💡 【核心分水嶺技術】：後台自動切分多篇文章
        passages_list = []
        if raw_passage:
            # 使用正則表達式，尋找 [DOC 1], [DOCUMENT 2], --- 等常見 AI 標記進行切分
            # 這樣不論 AI 用哪種分隔線，都能被強硬切開，且自動過濾掉空字串
            split_pieces = re.split(r'---+|\[DOCUMENT \d+\]|\[DOC \d+\]', raw_passage)
            passages_list = [piece.strip() for piece in split_pieces if piece.strip()]

        # 如果是單字或文法題（原本就沒文章），維持空 list
        if not passages_list and raw_passage:
            passages_list = [raw_passage]

        # 解析子題目
        sub_questions = []
        for item in ai_chunk:
            options_obj = QuestionOptions(
                A=item.get(ToeicQuestionCol.OPTION_A.value, ""),
                B=item.get(ToeicQuestionCol.OPTION_B.value, ""),
                C=item.get(ToeicQuestionCol.OPTION_C.value, ""),
                D=item.get(ToeicQuestionCol.OPTION_D.value, "")
            )
            sub_questions.append(ToeicSubQuestion(
                question=item.get(ToeicQuestionCol.QUESTION.value, ""),
                options=options_obj,
                answer=item.get(ToeicQuestionCol.ANSWER.value, "").upper(),
                explanation=item.get(ToeicQuestionCol.EXPLANATION.value, "")
            ))

        return cls(
            category=category,
            passages=passages_list, # 注入切分好的乾淨 list
            questions=sub_questions
        )