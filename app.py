from flask import Flask, render_template, request, jsonify, send_file
import json
import io
import os

app = Flask(__name__)

DATA_FILE = 'data.json'
LABELS_FILE = 'labels.json'

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"{DATA_FILE} 文件不存在，请准备数据文件")

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    image_html_list = json.load(f)

# 预加载已有标注（如果存在）
labels = {}
if os.path.exists(LABELS_FILE):
    try:
        with open(LABELS_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            # loaded 应该是个列表，每个元素包含index和label
            for item in loaded:
                idx = item.get("index")
                label = item.get("label")
                if idx is not None and label is not None:
                    labels[int(idx)] = label
    except Exception as e:
        print(f"加载已有标注文件出错：{e}")

@app.route('/')
def index():
    return render_template('index.html', total=len(image_html_list))

@app.route('/get_data')
def get_data():
    try:
        index = int(request.args.get('index', 0))
        if index < 0 or index >= len(image_html_list):
            return jsonify({"error": "索引越界"})
        item = image_html_list[index]
        label = labels.get(index, None)
        return jsonify({
            "index": index,
            "image": item["image"],
            "html": item["html"],
            "label": label
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/submit_label', methods=['POST'])
def submit_label():
    data = request.get_json()
    index = data.get('index')
    label = data.get('label')
    if index is None or label is None:
        return jsonify({"error": "缺少参数"}), 400
    try:
        index = int(index)
        if index < 0 or index >= len(image_html_list):
            return jsonify({"error": "索引越界"}), 400
        labels[index] = label

        # 保存到文件，实现预导入功能
        save_data = []
        for i, item in enumerate(image_html_list):
            save_data.append({
                "index": i,
                "image": item["image"],
                "html": item["html"],
                "label": labels.get(i, "")
            })
        with open(LABELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/export_labels')
def export_labels():
    export_data = []
    for i, item in enumerate(image_html_list):
        export_data.append({
            "index": i,
            "image": item["image"],
            "html": item["html"],
            "label": labels.get(i, "")
        })
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    buf = io.BytesIO()
    buf.write(json_str.encode('utf-8'))
    buf.seek(0)
    return send_file(buf,
                     mimetype='application/json',
                     as_attachment=True,
                     download_name='labels.json')

if __name__ == '__main__':
    app.run(debug=True)
