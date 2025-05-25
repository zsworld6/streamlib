import streamlit as st
import json
import os
from pathlib import Path
import base64
from datetime import datetime

# 可选导入 Pillow
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

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
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0c5460;
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
</style>
""", unsafe_allow_html=True)

# 数据文件路径
DATA_FILE = 'data.json'

@st.cache_data
def load_data():
    """加载图片数据"""
    if not os.path.exists(DATA_FILE):
        st.error(f"数据文件 {DATA_FILE} 不存在！")
        return []
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def init_session_labels(total_images):
    """初始化 session state 中的标注数据"""
    if 'labels_dict' not in st.session_state:
        st.session_state.labels_dict = {}
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

def export_labels_data(labels_dict, image_data):
    """生成导出数据"""
    labels_data = []
    for i, item in enumerate(image_data):
        labels_data.append({
            "index": i,
            "image": item["image"],
            "html": item["html"],
            "label": labels_dict.get(i, ""),
            "session_id": st.session_state.session_id,
            "timestamp": datetime.now().isoformat()
        })
    return labels_data

def display_image(image_path, caption):
    """显示图片，兼容有无 Pillow 的情况"""
    try:
        if os.path.exists(image_path):
            if PILLOW_AVAILABLE:
                image = Image.open(image_path)
                st.image(image, use_container_width=True, caption=caption)
            else:
                st.image(image_path, use_container_width=True, caption=caption)
        elif image_path.startswith(('http://', 'https://')):
            st.image(image_path, use_container_width=True, caption=caption)
        else:
            st.error("无法加载图片")
            st.write(f"图片路径: {image_path}")
    except Exception as e:
        st.error(f"图片加载失败: {e}")
        st.write(f"图片路径: {image_path}")

def main():
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🏷️ 图片标注工具</h1>
        <p>欢迎参与数据标注！您的贡献将帮助改进AI模型</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 重要提示
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ 重要提示：</strong> 本应用部署在 Streamlit Cloud 上，标注数据仅在当前会话中保存。
        请在完成标注后及时下载数据，应用重启后数据将丢失！
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    image_data = load_data()
    if not image_data:
        st.stop()
    
    # 初始化 session state
    total_images = len(image_data)
    init_session_labels(total_images)
    
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    
    # 侧边栏 - 控制面板
    with st.sidebar:
        st.header("🎯 控制面板")
        
        # 会话信息
        st.markdown(f"""
        <div class="info-box">
            <strong>📅 会话ID：</strong> {st.session_state.session_id}<br>
            <strong>⏰ 开始时间：</strong> {st.session_state.session_id[:8]}_{st.session_state.session_id[9:]}
        </div>
        """, unsafe_allow_html=True)
        
        # 进度统计
        labels_dict = st.session_state.labels_dict
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
        new_index = st.number_input(
            "跳转到图片", 
            min_value=1, 
            max_value=total_images, 
            value=st.session_state.current_index + 1
        ) - 1
        
        if new_index != st.session_state.current_index:
            st.session_state.current_index = new_index
            st.rerun()
        
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
        
        # 数据导出
        st.subheader("💾 数据导出")
        
        if labeled_count > 0:
            export_data = export_labels_data(labels_dict, image_data)
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            st.download_button(
                label=f"📥 下载标注数据 ({labeled_count} 条)",
                data=json_str,
                file_name=f"labels_{st.session_state.session_id}.json",
                mime="application/json",
                use_container_width=True
            )
            
            # 显示导出预览
            with st.expander("📋 导出数据预览"):
                st.json(export_data[:3])  # 只显示前3条
        else:
            st.info("还没有标注数据可导出")
    
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
                st.session_state.labels_dict[st.session_state.current_index] = label_value
                st.success(f"✅ 已标注为: {label_value if label_value else '清除标注'}")
                st.rerun()
    
    st.markdown("---")
    
    # 图片显示和HTML预览
    col_img, col_html = st.columns([1, 1])
    
    with col_img:
        st.subheader("🖼️ 当前图片")
        display_image(current_item["image"], f"图片 {st.session_state.current_index + 1}")
    
    with col_html:
        st.subheader("📄 HTML 内容")
        html_content = current_item.get("html", "")
        
        if html_content:
            # 显示HTML内容的前500个字符
            preview_content = html_content[:500] + "..." if len(html_content) > 500 else html_content
            st.code(preview_content, language="html")
            
            # 显示完整HTML的展开选项
            if len(html_content) > 500:
                with st.expander("查看完整HTML内容"):
                    st.code(html_content, language="html")
        else:
            st.info("此图片没有关联的HTML内容")
    
    # 使用说明
    with st.expander("📖 使用说明"):
        st.markdown("""
        ### 🎯 标注流程
        1. 查看当前图片和相关HTML内容
        2. 点击对应的分类按钮进行标注
        3. 使用导航按钮切换到下一张图片
        4. 完成后点击"下载标注数据"保存结果
        
        ### ⚠️ 重要提醒
        - 本应用数据仅在当前浏览器会话中保存
        - 刷新页面或关闭浏览器会导致数据丢失
        - 请及时下载标注结果
        
        ### 📋 分类说明
        - **数学**: 数学公式、计算器、数学教学内容
        - **物理**: 物理实验、公式、教学内容
        - **化学**: 化学方程式、实验、教学内容
        - **生命**: 生物学、医学相关内容
        - **地球**: 地理、地质、环境科学
        - **材料**: 材料科学、工程相关
        - **其他**: 不属于以上分类的内容
        """)

if __name__ == "__main__":
    main()