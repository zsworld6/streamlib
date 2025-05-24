#!/bin/bash
# start.sh - 启动脚本

echo "🚀 启动图片标注工具..."

# 检查依赖
if ! command -v streamlit &> /dev/null; then
    echo "📦 安装 Streamlit..."
    pip install -r requirements.txt
fi

# 启动应用
echo "🌐 启动 Streamlit 应用..."
echo "📱 应用将在 http://localhost:8501 启动"
echo "🔗 局域网访问地址将显示在下方"

streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
