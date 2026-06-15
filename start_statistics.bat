@echo off
REM ========================================
REM OpenClaw 统计分析功能 - 快速启动脚本
REM ========================================

echo.
echo ========================================
echo   OpenClaw 审计统计分析功能
echo ========================================
echo.

REM 检查Python环境
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)
echo ✅ Python环境正常

REM 检查Node.js环境
echo.
echo [2/4] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)
echo ✅ Node.js环境正常

REM 运行测试
echo.
echo [3/4] 运行功能测试...
python test_statistics_feature.py
if errorlevel 1 (
    echo.
    echo ⚠️  测试失败，请检查错误信息
    pause
    exit /b 1
)

REM 提示用户选择启动方式
echo.
echo ========================================
echo [4/4] 选择启动方式
echo ========================================
echo.
echo 1. 仅启动后端服务
echo 2. 仅启动前端服务
echo 3. 同时启动后端和前端（推荐）
echo 4. 退出
echo.
set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" goto start_backend
if "%choice%"=="2" goto start_frontend
if "%choice%"=="3" goto start_both
if "%choice%"=="4" goto end

echo 无效选项，退出
pause
exit /b 1

:start_backend
echo.
echo 🚀 启动后端服务...
echo 访问地址: http://localhost:8000/docs
echo.
start uvicorn app.main:app --reload
goto end

:start_frontend
echo.
echo 🚀 启动前端服务...
echo 访问地址: http://localhost:3000
echo.
cd frontend
start npm run dev
goto end

:start_both
echo.
echo 🚀 同时启动后端和前端服务...
echo.
echo [后端] 访问: http://localhost:8000/docs
echo [前端] 访问: http://localhost:3000/statistics
echo.
echo 💡 提示: 
echo    - 后端将在新窗口启动
echo    - 前端将在新窗口启动
echo    - 请等待服务完全启动后访问
echo.
pause

REM 启动后端（新窗口）
start "OpenClaw Backend" cmd /k "uvicorn app.main:app --reload"

REM 等待2秒让后端先启动
timeout /t 2 /nobreak >nul

REM 启动前端（新窗口）
cd frontend
start "OpenClaw Frontend" cmd /k "npm run dev"

goto end

:end
echo.
echo ========================================
echo   感谢使用 OpenClaw!
echo ========================================
echo.
pause
