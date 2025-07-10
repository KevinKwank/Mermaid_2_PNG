@echo off
chcp 65001 > nul
echo 🚀 启动 Mermaid to PNG Web 应用

echo 📦 检查 Python 依赖...
py -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo 🌐 启动 Web 服务器...
echo 📱 浏览器将自动打开 http://localhost:5000
echo ⏹️  按 Ctrl+C 停止服务器

timeout /t 2 > nul
start http://localhost:5000

echo 🔍 使用正确的Python版本启动应用...
py web_app.py

pause
