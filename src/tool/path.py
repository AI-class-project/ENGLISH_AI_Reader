import sys
from dataclasses import dataclass
from pathlib import Path

from debug import dbg


def _resource_path(*paths):
    """
    取得外部資源路徑：
    - 打包成 exe 時：使用 exe 同目錄
    - 開發模式：使用專案根目錄
    """
    if getattr(sys, "frozen", False):
        # exe 打包後使用的路徑
        base_path = Path(sys.executable).resolve().parent
    else:
        # 開發環境使用的路徑
        base_path = Path(__file__).resolve().parent.parent

    return base_path.joinpath(*paths)


@dataclass(frozen = True)
class _PathFile:
    root = _resource_path()

    @classmethod
    def get_all_paths(cls):
        return [v for _, v in vars(cls).items() if isinstance(v, Path)]

@dataclass(frozen = True)
class PathConfig:
    pass
    # REPORT_RESULT = _PathFile.report
    # EXPERIMENT_DETAILS = _PathFile.report / "experiment_detail.csv"


def setup_filesystem():
    """
    確保所有靜態路徑的「資料夾」都存在。
    """
    try:
        for d in _PathFile.get_all_paths():
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                dbg.log(f"[系統初始化] 建立新資料夾: {d}")

    except Exception as e:
        dbg.error(f"路徑系統初始化警告: {e}")

setup_filesystem()
