from RAG.core.models.qwen_model import get_deepseek_model
from RAG.services.retrieval_service import retrieve_documents
from RAG.utils.text_processor import clean_text
from RAG.utils.logger import logger
import torch
from flask import session

# 全局加载模型（避免重复初始化）
model, tokenizer = None, None
def load_model_once():
    global model, tokenizer
    if model is None:
        model, tokenizer = get_deepseek_model()
        model = model.float().to("cpu")  # 确保全精度且在CPU

load_model_once()

def get_answer(question, session_id):
    # 获取会话历史
    history = session.get('history', [])

    # 检索文档
    docs = retrieve_documents(question)
    seen_links = set()
    unique_docs = []
    for doc in docs:
        link = doc['link']
        if link not in seen_links:
            unique_docs.append(doc)
            seen_links.add(link)
    # print(unique_docs)
    logger.info(f"检索到的文档数量：{len(unique_docs)}")
    if not unique_docs:
        return "未找到相关新闻内容。"

    # 列举相关新闻的场景
    if "有哪些" in question and "校党委" in question:
        result = []
        for doc in unique_docs[:3]:  # 限制为前3条
            content = clean_text(doc["content"])
            if len(content) > 50:
                content = content[:47] + "..."
            result.append({"title": doc["title"], "content": content, "link": doc["link"]})
        return result

    # 模型生成回答的场景
    # 构建上下文：包括历史对话和当前检索到的文档
    history_text = "\n".join([f"问题：{entry['question']}\n回答：{entry['answer']}" for entry in history])
    context = "\n".join([f"{doc['content']} (来源: {doc['link']})" for doc in unique_docs])
    prompt = f"""请严格根据以下新闻内容和历史对话回答问题，若内容不相关请回答“未知”：
    历史对话：
    {history_text}

    新闻内容：
    {context}

    问题：{question}
    回答："""

    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        num_beams=3,
        early_stopping=True,
        temperature=0.3
    )

    full_answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = full_answer.split("回答：")[-1].strip()
    logger.info(f"原始回答内容：{full_answer}")

    cleaned_answer = clean_text(answer)

    if "未知" not in cleaned_answer and docs:
        link = docs[0]["link"]  # 单一回答场景只取第一个链接
        return f"{cleaned_answer} (来源: {link})"

    return cleaned_answer