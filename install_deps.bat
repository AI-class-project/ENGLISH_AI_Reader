@echo off
:: 設定編碼為 UTF-8，避免中文亂碼
chcp 65001 > nul

echo ===================================================
echo   正在為您的 VS Code 環境安裝必要的 Python 套件...
echo ===================================================
echo.

:: 升級 pip 到最新版本（強烈建議，避免安裝新版 SDK 時出錯）
echo [1/3] 正在檢查並升級 pip...
python -m pip install --upgrade pip

echo.
:: 安裝 Google GenAI SDK
echo [2/3] 正在安裝 google-genai...
python -m pip install google-genai

echo.
:: 安裝 Feedparser
echo [3/3] 正在安裝 feedparser...
python -m pip install feedparser

echo.
echo ===================================================
echo   🎉 所有套件安裝程序已完成！
echo   現在您可以在 VS Code 中順利執行您的 Python 程式了。
echo ===================================================
echo.
pause