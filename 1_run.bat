@echo off
cd /d "%~dp0"

echo ============================================
echo   CatchRisk 合同审核系统 · 启动中
echo ============================================
echo.

python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [错误] 未检测到 Python，請先安裝 Python 3.10+ 後再運行本腳本。
    pause
    exit /b 1
)

IF NOT EXIST venv (
    echo [1] 正在创建虚拟环境 venv ...
    python -m venv venv
)

echo [2] 正在激活虚拟环境并安装依赖...
call venv\Scripts\activate

pip install --upgrade pip >nul
pip install -r backend\requirements.txt

echo.
echo [3] 正在启动後端服務（http://127.0.0.1:8000）...
echo    如需停止，請在此窗口按 Ctrl + C
echo.

cd backend
uvicorn main:app --host 127.0.0.1 --port 8000
