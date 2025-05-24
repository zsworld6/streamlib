# 图片标注工具部署指南

## 📋 快速开始

### 本地运行
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run streamlit_app.py

# 或者使用启动脚本
./start.sh        # Linux/Mac
start.bat         # Windows
```

## 🌐 公网部署

### 方法1: Streamlit Cloud (推荐)
1. 上传代码到 GitHub
2. 访问 https://share.streamlit.io/
3. 连接 GitHub 并选择仓库
4. 设置主文件为 `streamlit_app.py`
5. 点击 Deploy

### 方法2: 使用 ngrok (临时公网访问)
```bash
# 安装 ngrok
# 下载地址: https://ngrok.com/download

# 启动应用
streamlit run streamlit_app.py

# 新终端窗口运行 ngrok
ngrok http 8501
```

### 方法3: 云服务器部署
```bash
# 在云服务器上
git clone your-repo
cd image-labeling-tool
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

## 📱 使用说明

1. **导航**: 使用侧边栏的上一张/下一张按钮
2. **标注**: 点击分类按钮为图片打标签
3. **进度**: 实时查看标注进度和统计
4. **导出**: 完成后导出 labels.json 文件

## 🔧 自定义配置

- 修改 `data.json` 添加更多图片
- 调整分类标签（在代码中修改 categories 列表）
- 自定义样式（修改 CSS 部分）

## 📊 数据格式

### data.json
```json
[
  {
    "image": "static/images/sample.png",
    "html": "<!DOCTYPE html>..."
  }
]
```

### labels.json (输出)
```json
[
  {
    "index": 0,
    "image": "static/images/sample.png", 
    "html": "<!DOCTYPE html>...",
    "label": "数学"
  }
]
```
