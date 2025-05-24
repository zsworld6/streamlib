import streamlit as st
import json
import os
from pathlib import Path
import base64
from PIL import Image
import io

# 页面配置
st.set_page_config(
    page_title="图片标注工具",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .label-button {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        background-color: #f0f2f6;
        border: 1px solid #ddd;
        border-radius: 20px;
        text-decoration: none;
        color: #333;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .label-button:hover {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    .current-label {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.5rem 1rem;
        background-color: #e8f4f8;
        border-radius: 5px;
        border-left: 4px solid #667eea;
    }
    
    .progress-bar {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 3px;
        margin: 1rem 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 20px;
        border-radius: 7px;
        transition: width 0.3s ease;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    .html-preview {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        max-height: 300px;
        overflow-y: auto;
        white-space: pre-wrap;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# 数据文件路径
DATA_FILE = 'data.json'
LABELS_FILE = 'labels.json'

@st.cache_data
def load_data():
    """加载图片数据"""
    if not os.path.exists(DATA_FILE):
        st.error(f"数据文件 {DATA_FILE} 不存在！")
        return []
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_labels():
    """加载标注数据"""
    if os.path.exists(LABELS_FILE):
        try:
            with open(LABELS_FILE, 'r', encoding='utf-8') as f:
                labels_data = json.load(f)
                # 转换为字典格式 {index: label}
                if isinstance(labels_data, list):
                    return {item.get("index", i): item.get("label", "") for i, item in enumerate(labels_data)}
                return labels_data
        except Exception as e:
            st.error(f"加载标注文件出错：{e}")
    return {}

def save_labels(labels_dict, image_data):
    """保存标注数据"""
    try:
        # 创建完整的标注数据
        labels_data = []
        for i, item in enumerate(image_data):
            labels_data.append({
                "index": i,
                "image": item["image"],
                "html": item["html"],
                "label": labels_dict.get(i, "")
            })
        
        with open(LABELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(labels_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存标注失败：{e}")
        return False

def get_image_base64(image_path):
    """获取图片的base64编码（如果是本地文件）"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except:
        pass
    return None

def main():
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🏷️ 图片标注工具</h1>
        <p>欢迎参与数据标注！您的贡献将帮助改进AI模型</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    image_data = load_data()
    if not image_data:
        st.stop()
    
    labels_dict = load_labels()
    
    # 初始化session state
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    
    # 侧边栏 - 控制面板
    with st.sidebar:
        st.header("🎯 控制面板")
        
        # 进度统计
        total_images = len(image_data)
        labeled_count = sum(1 for label in labels_dict.values() if label)
        progress = labeled_count / total_images if total_images > 0 else 0
        
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-number">{st.session_state.current_index + 1}</div>
                <div class="stat-label">当前图片</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{total_images}</div>
                <div class="stat-label">总计图片</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{labeled_count}</div>
                <div class="stat-label">已标注</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 进度条
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress*100}%"></div>
        </div>
        <p style="text-align: center; color: #666;">完成进度: {progress*100:.1f}%</p>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 导航控制
        st.subheader("📋 导航控制")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ 上一张", use_container_width=True):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.rerun()
        
        with col2:
            if st.button("下一张 ➡️", use_container_width=True):
                if st.session_state.current_index < total_images - 1:
                    st.session_state.current_index += 1
                    st.rerun()
        
        # 快速跳转
        st.session_state.current_index = st.number_input(
            "跳转到图片", 
            min_value=1, 
            max_value=total_images, 
            value=st.session_state.current_index + 1
        ) - 1
        
        st.markdown("---")
        
        # 分类统计
        st.subheader("📊 分类统计")
        categories = ["数学", "物理", "化学", "生命", "地球", "材料", "其他"]
        for category in categories:
            count = sum(1 for label in labels_dict.values() if label == category)
            st.write(f"**{category}**: {count} 张")
        
        unlabeled = total_images - labeled_count
        st.write(f"**未标注**: {unlabeled} 张")
        
        st.markdown("---")
        
        # 导出数据
        st.subheader("💾 数据管理")
        if st.button("📥 导出标注数据", use_container_width=True):
            if save_labels(labels_dict, image_data):
                with open(LABELS_FILE, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="⬇️ 下载 labels.json",
                        data=f.read(),
                        file_name="labels.json",
                        mime="application/json",
                        use_container_width=True
                    )
                st.success("✅ 数据导出成功！")
    
    # 主内容区域
    current_item = image_data[st.session_state.current_index]
    current_label = labels_dict.get(st.session_state.current_index, "")
    
    # 当前标注状态
    st.markdown(f"""
    <div class="current-label">
        🏷️ 当前标注: {current_label if current_label else "未标注"}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 分类按钮
    st.subheader("🎯 选择分类")
    col1, col2, col3, col4 = st.columns(4)
    
    categories = [
        ("📐 数学", "数学"),
        ("⚛️ 物理", "物理"),
        ("🧪 化学", "化学"),
        ("🧬 生命", "生命"),
        ("🌍 地球", "地球"),
        ("🔬 材料", "材料"),
        ("📝 其他", "其他"),
        ("❌ 清除标注", "")
    ]
    
    for i, (display_text, label_value) in enumerate(categories):
        col = [col1, col2, col3, col4][i % 4]
        with col:
            if st.button(display_text, use_container_width=True):
                labels_dict[st.session_state.current_index] = label_value
                save_labels(labels_dict, image_data)
                st.success(f"✅ 已标注为: {label_value if label_value else '清除标注'}")
                st.rerun()
    
    st.markdown("---")
    
    # 图片显示和HTML预览
    col_img, col_html = st.columns([1, 1])
    
    with col_img:
        st.subheader("🖼️ 当前图片")
        
        image_path = current_item["image"]
        
        # 尝试显示图片
        try:
            if os.path.exists(image_path):
                # 本地文件
                image = Image.open(image_path)
                st.image(image, use_container_width=True, caption=f"图片 {st.session_state.current_index + 1}")
            elif image_path.startswith(('http://', 'https://')):
                # 网络图片
                st.image(image_path, use_container_width=True, caption=f"图片 {st.session_state.current_index + 1}")
            else:
                st.error("无法加载图片")
                st.write(f"图片路径: {image_path}")
        except Exception as e:
            st.error(f"图片加载失败: {e}")
            st.write(f"图片路径: {image_path}")
    
    with col_html:
        st.subheader("📄 HTML 内容")
        
        html_content = current_item.get("html", "")
        
        # 显示HTML内容的前1000个字符
        if html_content:
            preview_content = html_content[:1000] + "..." if len(html_content) > 1000 else html_content
            st.markdown(f'<div class="html-preview">{preview_content}</div>', unsafe_allow_html=True)
            
            # 显示完整HTML的展开选项
            if len(html_content) > 1000:
                with st.expander("查看完整HTML内容"):
                    st.text(html_content)
        else:
            st.info("此图片没有关联的HTML内容")
    
    # 键盘快捷键提示
    with st.expander("⌨️ 键盘快捷键"):
        st.markdown("""
        - **数字键 1-7**: 快速标注对应分类
        - **左右方向键**: 切换图片（需要刷新页面生效）
        
        **分类对应数字:**
        1. 数学  2. 物理  3. 化学  4. 生命
        5. 地球  6. 材料  7. 其他
        """)

if __name__ == "__main__":
    main()