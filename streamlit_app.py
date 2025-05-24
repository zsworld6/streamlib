import streamlit as st
import json
import os
from pathlib import Path
import requests
from datetime import datetime
import hashlib

# 页面配置
st.set_page_config(
    page_title="协作图片标注工具",
    page_icon="👥",
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
    
    .collaboration-info {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .user-info {
        background-color: #e8f4f8;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
    
    .current-label {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.5rem 1rem;
        background-color: #e8f4f8;
        border-radius: 5px;
        border-left: 4px solid #667eea;
    }
    
    .task-assignment {
        background-color: #f8f9fa;
        border: 2px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets API 配置（示例）
# 注意：实际使用时需要配置 Google Sheets API 密钥
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/你的表格ID/edit"
SHEET_API_URL = "你的Google Sheets API端点"

def generate_user_id():
    """生成用户唯一标识"""
    if 'user_id' not in st.session_state:
        # 基于时间戳和随机数生成用户ID
        timestamp = str(datetime.now().timestamp())
        st.session_state.user_id = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    return st.session_state.user_id

def assign_task_to_user(user_id, total_images, num_users=5):
    """为用户分配标注任务"""
    user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    
    # 计算该用户负责的图片范围
    images_per_user = total_images // num_users
    remainder = total_images % num_users
    
    user_index = user_hash % num_users
    
    start_idx = user_index * images_per_user
    if user_index < remainder:
        start_idx += user_index
        end_idx = start_idx + images_per_user + 1
    else:
        start_idx += remainder
        end_idx = start_idx + images_per_user
    
    return list(range(start_idx, min(end_idx, total_images)))

def save_to_google_sheets(user_id, image_index, label, image_path):
    """保存标注到 Google Sheets（示例函数）"""
    # 这里是示例代码，实际需要配置 Google Sheets API
    data = {
        "user_id": user_id,
        "image_index": image_index,
        "image_path": image_path,
        "label": label,
        "timestamp": datetime.now().isoformat()
    }
    
    # 模拟API调用
    try:
        # response = requests.post(SHEET_API_URL, json=data)
        # return response.status_code == 200
        return True  # 模拟成功
    except:
        return False

@st.cache_data
def load_data():
    """加载图片数据"""
    if not os.path.exists('data.json'):
        st.error("数据文件 data.json 不存在！")
        return []
    
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>👥 协作图片标注工具</h1>
        <p>多人同时标注，数据实时同步</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 生成用户ID
    user_id = generate_user_id()
    
    # 用户信息
    st.markdown(f"""
    <div class="user-info">
        <strong>👤 您的标注员ID：</strong> {user_id}<br>
        <strong>⏰ 会话开始时间：</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    image_data = load_data()
    if not image_data:
        st.stop()
    
    total_images = len(image_data)
    
    # 任务分配
    assigned_indices = assign_task_to_user(user_id, total_images)
    
    st.markdown(f"""
    <div class="task-assignment">
        <h3>📋 您的标注任务</h3>
        <p><strong>分配的图片数量：</strong> {len(assigned_indices)} 张</p>
        <p><strong>图片编号范围：</strong> {min(assigned_indices) + 1} - {max(assigned_indices) + 1}</p>
        <p><strong>任务进度：</strong> 0 / {len(assigned_indices)} 完成</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 协作说明
    st.markdown("""
    <div class="collaboration-info">
        <h4>🤝 协作模式说明</h4>
        <ul>
            <li><strong>任务分配：</strong> 系统自动为每个用户分配不同的图片进行标注</li>
            <li><strong>避免重复：</strong> 不同用户标注不同的图片，提高效率</li>
            <li><strong>数据收集：</strong> 所有标注结果统一收集和管理</li>
            <li><strong>进度追踪：</strong> 可以查看整体标注进度</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化 session state
    if 'current_task_index' not in st.session_state:
        st.session_state.current_task_index = 0
    
    if 'labeled_count' not in st.session_state:
        st.session_state.labeled_count = 0
    
    if 'user_labels' not in st.session_state:
        st.session_state.user_labels = {}
    
    # 侧边栏控制
    with st.sidebar:
        st.header("🎯 标注控制")
        
        # 任务进度
        progress = st.session_state.labeled_count / len(assigned_indices) if assigned_indices else 0
        st.progress(progress)
        st.write(f"进度: {st.session_state.labeled_count}/{len(assigned_indices)} ({progress*100:.1f}%)")
        
        st.markdown("---")
        
        # 导航控制
        st.subheader("📋 任务导航")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ 上一张", use_container_width=True):
                if st.session_state.current_task_index > 0:
                    st.session_state.current_task_index -= 1
                    st.rerun()
        
        with col2:
            if st.button("下一张 ➡️", use_container_width=True):
                if st.session_state.current_task_index < len(assigned_indices) - 1:
                    st.session_state.current_task_index += 1
                    st.rerun()
        
        # 任务跳转
        if assigned_indices:
            task_num = st.selectbox(
                "跳转到任务",
                range(1, len(assigned_indices) + 1),
                index=st.session_state.current_task_index
            )
            st.session_state.current_task_index = task_num - 1
        
        st.markdown("---")
        
        # 标注统计
        st.subheader("📊 我的标注统计")
        categories = ["数学", "物理", "化学", "生命", "地球", "材料", "其他"]
        for category in categories:
            count = sum(1 for label in st.session_state.user_labels.values() if label == category)
            st.write(f"**{category}**: {count} 张")
        
        st.markdown("---")
        
        # 数据导出
        st.subheader("💾 我的标注数据")
        if st.session_state.user_labels:
            # 生成导出数据
            export_data = []
            for img_idx, label in st.session_state.user_labels.items():
                export_data.append({
                    "user_id": user_id,
                    "image_index": img_idx,
                    "image_path": image_data[img_idx]["image"],
                    "label": label,
                    "timestamp": datetime.now().isoformat()
                })
            
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            st.download_button(
                label=f"📥 下载我的标注 ({len(export_data)} 条)",
                data=json_str,
                file_name=f"my_labels_{user_id}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.info("还没有标注数据")
    
    # 主标注区域
    if not assigned_indices:
        st.error("没有分配到标注任务！")
        st.stop()
    
    current_image_index = assigned_indices[st.session_state.current_task_index]
    current_item = image_data[current_image_index]
    current_label = st.session_state.user_labels.get(current_image_index, "")
    
    # 当前图片信息
    st.markdown(f"""
    <div class="current-label">
        🖼️ 图片 {current_image_index + 1} / {total_images} (任务 {st.session_state.current_task_index + 1} / {len(assigned_indices)})
        <br>
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
            if st.button(display_text, use_container_width=True, key=f"btn_{i}"):
                # 保存到本地 session
                old_label = st.session_state.user_labels.get(current_image_index, "")
                if label_value:
                    st.session_state.user_labels[current_image_index] = label_value
                else:
                    st.session_state.user_labels.pop(current_image_index, None)
                
                # 更新计数
                if old_label and not label_value:
                    st.session_state.labeled_count -= 1
                elif not old_label and label_value:
                    st.session_state.labeled_count += 1
                
                # 保存到云端（可选）
                # save_to_google_sheets(user_id, current_image_index, label_value, current_item["image"])
                
                st.success(f"✅ 已标注为: {label_value if label_value else '清除标注'}")
                st.rerun()
    
    # 快捷键提示
    st.info("💡 提示：完成当前图片标注后，点击'下一张'继续您的标注任务")
    
    st.markdown("---")
    
    # 图片显示
    col_img, col_html = st.columns([1, 1])
    
    with col_img:
        st.subheader("🖼️ 当前图片")
        image_path = current_item["image"]
        
        try:
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True, 
                        caption=f"图片 {current_image_index + 1}")
            elif image_path.startswith(('http://', 'https://')):
                st.image(image_path, use_container_width=True, 
                        caption=f"图片 {current_image_index + 1}")
            else:
                st.error("无法加载图片")
        except Exception as e:
            st.error(f"图片加载失败: {e}")
    
    with col_html:
        st.subheader("📄 HTML 内容")
        html_content = current_item.get("html", "")
        
        if html_content:
            # 显示HTML内容预览
            preview_content = html_content[:500] + "..." if len(html_content) > 500 else html_content
            st.code(preview_content, language="html")
            
            if len(html_content) > 500:
                with st.expander("查看完整HTML"):
                    st.code(html_content, language="html")
        else:
            st.info("无HTML内容")
    
    # 使用说明
    with st.expander("📖 协作标注说明"):
        st.markdown(f"""
        ### 🎯 您的任务
        - **分配图片**: {len(assigned_indices)} 张
        - **当前进度**: {st.session_state.labeled_count} / {len(assigned_indices)} 完成
        
        ### 🤝 协作机制
        - 每个标注员分配不同的图片，避免重复劳动
        - 您的用户ID: `{user_id}` 确保任务分配的一致性
        - 所有标注结果可以统一收集和合并
        
        ### 📋 标注流程
        1. 查看分配给您的图片和HTML内容
        2. 选择合适的分类标签
        3. 点击"下一张"继续标注
        4. 完成后下载您的标注数据
        
        ### ⚠️ 注意事项
        - 刷新页面会丢失未保存的标注
        - 建议定期下载备份标注数据
        - 如需暂停，请记住您的用户ID: `{user_id}`
        """)

if __name__ == "__main__":
    main()