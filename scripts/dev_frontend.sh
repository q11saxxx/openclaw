#!/usr/bin/env bash
# 本文件说明：一键启动前端开发服务，方便团队统一命令。
set -e
cd "$(dirname "$0")/../frontend"
npm run dev
