import sys
from dataclasses import dataclass
from pathlib import Path

from tool.debug import dbg


def _resource_path(*paths):
    """
    取得外部資源路徑：
    - 打包成 exe 時：使用 exe 同目錄
    - 開發模式：使用專案根目錄
    """
    if getattr(sys, "frozen", False):
        # exe 打包後使用的路徑
        base_path = Path(sys.executable).resolve().parent.parent.parent
    else:
        # 開發環境使用的路徑
        base_path = Path(__file__).resolve().parent.parent.parent

    return base_path.joinpath(*paths)


@dataclass(frozen = True)
class _PathFile:
    """第一層：專門定義資料夾骨架，確保裡面全部都是純目錄"""
    root = _resource_path()

    @classmethod
    def get_all_paths(cls):
        return [v for k, v in vars(cls).items() if isinstance(v, Path) and not k.startswith("_")]

@dataclass(frozen = True)
class PathConfig:
    """第二層：面向應用的配置，組合或繼承第一層，可以包含檔案"""
    GEMINI_KEY = _PathFile.root / "key.env"


def setup_filesystem():
    """
    確保所有靜態路徑的「資料夾」都存在。
    """
    try:
        for folder in _PathFile.get_all_paths():
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)
                dbg.log(f"[系統初始化] 建立新資料夾: {folder}")

    except Exception as e:
        dbg.error(f"路徑系統初始化警告: {e}")

setup_filesystem()
