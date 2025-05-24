@echo off
echo 🚀 启动图片标注工具...

:: 检查依赖
pip install -r requirements.txt

:: 启动应用
echo 🌐 启动 Streamlit 应用...
echo 📱 应用将在 http://localhost:8501 启动

streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
pause
