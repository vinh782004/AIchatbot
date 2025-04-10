from flask import Flask, render_template, request, jsonify
import json
from difflib import SequenceMatcher

app = Flask(__name__)

def load_knowledge_base(file_path):
    """Tải cơ sở tri thức từ file JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Tệp {file_path} không tồn tại. Tạo cơ sở tri thức mới.")
        return {}
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu: {str(e)}")
        return {}


def find_closest_match(input_question, knowledge_base):
    """Tìm câu hỏi gần nhất trong cơ sở tri thức."""
    max_ratio = 0
    closest_question = None
    for question in knowledge_base.keys():
        ratio = SequenceMatcher(None, input_question, question).ratio()
        if ratio > max_ratio:
            max_ratio = ratio
            closest_question = question
    return closest_question if max_ratio > 0.6 else None


def get_response(question, knowledge_base):
    """Lấy câu trả lời từ cơ sở tri thức."""
    closest_question = find_closest_match(question, knowledge_base)
    if closest_question:
        return knowledge_base[closest_question]
    else:
        return None


def update_knowledge_base(file_path, question, answer, knowledge_base):
    """Cập nhật cơ sở tri thức."""
    knowledge_base[question] = answer
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(knowledge_base, file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Lỗi khi ghi dữ liệu: {str(e)}")


@app.route('/')
def index():
    """Trang chính."""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Xử lý cuộc trò chuyện."""
    user_input = request.form['user_input']
    file_path = 'knowledge_base.json'
    knowledge_base = load_knowledge_base(file_path)
    response = get_response(user_input, knowledge_base)
    if response:
        return jsonify({"response": response, "learn": False})
    else:
        return jsonify({"response": "Tôi không hiểu, bạn có thể dạy tôi không?", "learn": True})


@app.route('/learn', methods=['POST'])
def learn():
    """Cập nhật kiến thức mới."""
    user_question = request.form['user_question']
    user_answer = request.form['user_answer']
    file_path = 'knowledge_base.json'
    knowledge_base = load_knowledge_base(file_path)
    update_knowledge_base(file_path, user_question, user_answer, knowledge_base)
    return jsonify({"message": "Đã lưu kiến thức mới thành công!"})

if __name__ == '__main__':
    app.run(debug=True)
