import json

from core.engine.models import ToeicQuestionModel
from core.storage.toeic_repo import ToeicQuestionRepository
from tool.path import PathConfig
from tool.debug import dbg


def main():
    json_path = PathConfig.TOEIC_POOL

    if not json_path.exists():
        dbg.error(f"❌ 找不到舊題庫 JSON：{json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    models = []

    for item in raw_data:
        try:
            models.append(ToeicQuestionModel.from_ai_dict(item))
        except Exception as e:
            dbg.war(f"⚠️ 有一筆資料轉換失敗，已略過：{e}")

    repo = ToeicQuestionRepository()
    repo.insert_question_groups(models)

    dbg.log(f"✅ 舊 JSON 題庫匯入完成，共匯入 {len(models)} 組")


if __name__ == "__main__":
    main()