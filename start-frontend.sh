#!/bin/bash

echo "========================================"
echo "  OpenClaw Frontend 启动脚本"
echo "========================================"
echo ""

# 检查是否安装了 Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未检测到 Node.js，请先安装 Node.js"
    echo "下载地址: https://nodejs.org/"
    exit 1
fi

echo "[信息] Node.js 版本:"
node --version
echo ""

# 进入前端目录
cd "$(dirname "$0")/frontend" || exit 1

echo "[信息] 检查依赖..."
if [ ! -d "node_modules" ]; then
    echo "[信息] 首次运行，正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo ""
echo "[信息] 启动开发服务器..."
echo "[信息] 前端地址: http://localhost:3000"
echo "[信息] 按 Ctrl+C 停止服务器"
echo ""

npm run dev
