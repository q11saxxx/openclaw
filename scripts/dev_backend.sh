#!/usr/bin/env bash
# 本文件说明：一键启动后端开发服务，方便 VSCode 终端直接运行。
set -e
cd "$(dirname "$0")/../backend"
uvicorn app.main:app --reload
