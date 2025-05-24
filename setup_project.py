# setup_project.py - 快速设置项目脚本
import os
import json
import shutil
from pathlib import Path

def setup_streamlit_project():
    """设置 Streamlit 标注项目"""
    
    print("🚀 开始设置 Streamlit 图片标注项目...")
    
    # 1. 创建项目目录结构
    directories = [
        "static/images",
        ".streamlit"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {directory}")
    
    # 2. 创建 requirements.txt
    requirements = """streamlit==1.28.0
Pillow==10.0.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    print("📝 创建 requirements.txt")
    
    # 3. 创建 Streamlit 配置文件
    config_toml = """[global]
developmentMode = false

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200

[browser]
gatherUsageStats = false
"""
    
    with open(".streamlit/config.toml", "w") as f:
        f.write(config_toml)
    print("⚙️ 创建 Streamlit 配置文件")
    
    # 4. 检查并处理现有的数据文件
    if os.path.exists("data.json"):
        print("✅ 发现现有的 data.json 文件")
        
        # 检查图片路径并尝试复制图片到 static/images
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        updated_data = []
        for i, item in enumerate(data):
            image_path = item["image"]
            
            # 如果是相对路径，尝试复制到 static/images
            if not image_path.startswith(("http://", "https://")) and os.path.exists(image_path):
                filename = os.path.basename(image_path)
                new_path = f"static/images/{filename}"
                
                try:
                    shutil.copy2(image_path, new_path)
                    item["image"] = new_path
                    print(f"📋 复制图片: {image_path} -> {new_path}")
                except Exception as e:
                    print(f"⚠️ 复制图片失败: {e}")
            
            updated_data.append(item)
        
        # 保存更新后的数据
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
    else:
        # 创建示例数据文件
        sample_data = [
            {
                "image": "static/images/sample1.png",
                "html": "<!DOCTYPE html><html><head><title>数学示例</title></head><body><h1>示例数学内容</h1></body></html>"
            },
            {
                "image": "static/images/sample2.png", 
                "html": "<!DOCTYPE html><html><head><title>物理示例</title></head><body><h1>示例物理内容</h1></body></html>"
            }
        ]
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        print("📝 创建示例 data.json 文件")
    
    # 5. 创建启动脚本
    start_script = """#!/bin/bash
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
"""
    
    with open("start.sh", "w") as f:
        f.write(start_script)
    
    # 在 Windows 上创建 .bat 文件
    start_bat = """@echo off
echo 🚀 启动图片标注工具...

:: 检查依赖
pip install -r requirements.txt

:: 启动应用
echo 🌐 启动 Streamlit 应用...
echo 📱 应用将在 http://localhost:8501 启动

streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
pause
"""
    
    with open("start.bat", "w") as f:
        f.write(start_bat)
    
    print("🎯 创建启动脚本 (start.sh / start.bat)")
    
    # 6. 创建部署说明文件
    deploy_readme = """# 图片标注工具部署指南

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
"""
    
    with open("DEPLOY.md", "w", encoding="utf-8") as f:
        f.write(deploy_readme)
    print("📖 创建部署说明文件 (DEPLOY.md)")
    
    print("\n✅ 项目设置完成！")
    print("\n🎯 下一步操作:")
    print("1. 将你的图片放入 static/images/ 目录")
    print("2. 更新 data.json 文件以包含你的图片")
    print("3. 运行 'streamlit run streamlit_app.py' 启动应用")
    print("4. 或者运行 './start.sh' (Linux/Mac) 或 'start.bat' (Windows)")
    print("\n🌐 部署到公网:")
    print("- 上传到 GitHub 然后使用 Streamlit Cloud")
    print("- 或使用 ngrok 进行临时公网访问")
    print("- 详细说明请查看 DEPLOY.md 文件")

if __name__ == "__main__":
    setup_streamlit_project()