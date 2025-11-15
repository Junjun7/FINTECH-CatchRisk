#!/bin/bash
cd "$(dirname "$0")"

echo "============================================"
echo "  CatchRisk 合同审核系统 · 启动中"
echo "============================================"
echo

if ! command -v python3 &> /dev/null
then
    echo "[错误] 未检测到 python3，请先安装 Python 3.10+"
    exit 1
fi

if [ ! -d "venv" ]; then
  echo "[1] 正在创建虚拟环境 venv ..."
  python3 -m venv venv
fi

echo "[2] 正在激活虚拟环境并安装依赖..."
source venv/bin/activate

pip install --upgrade pip >/dev/null
pip install -r backend/requirements.txt

echo
echo "[3] 正在启动后端服务（http://127.0.0.1:8000）..."
echo "    如需停止，请在此终端按 Ctrl + C"
echo

cd backend
uvicorn main:app --host 127.0.0.1 --port 8000
