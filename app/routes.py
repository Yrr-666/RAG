from flask import Blueprint, render_template, request, jsonify, session
from RAG.services.qa_service import get_answer

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET"])
def index():
    # 初始化会话
    if 'session_id' not in session:
        session['session_id'] = str(hash(str(request.remote_addr) + str(request.user_agent)))
        session['history'] = []  # 存储对话历史
    return render_template("index.html", history=session.get('history', []))

@bp.route("/ask", methods=["POST"])
def ask():
    # 获取问题和会话ID
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据必须为 JSON 格式"}), 415

    question = data.get("question")
    session_id = data.get("session_id")

    if not question or not session_id:
        return jsonify({"error": "缺少问题或会话ID"}), 400

    # 确保会话一致
    if session.get('session_id') != session_id:
        return jsonify({"error": "会话ID不匹配"}), 400

    # 获取回答
    answer = get_answer(question, session_id)

    # 更新会话历史
    history = session.get('history', [])
    history.append({"question": question, "answer": answer})
    session['history'] = history

    return jsonify({"answer": answer})