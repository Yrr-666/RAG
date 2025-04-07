# RAG
这是基于QWen的RAG问答系统
文件介绍：
app里放入前端页面
  app/routes.py:路由
core/data_preparation/crawler.py:爬取中北大学新闻页的文件生成news_data.csv
core/embedding_processor.py:创建faiss库生成news_index.faiss和news_df.pkl文件
models里放入大模型和嵌入模型
     models/embedding_model.py:加载嵌入模型
     models/qwen_model.py:加载大模型，比如千问，deepseek等等
services:服务（后端）
    services/qa_service.py：问答服务，前后端交互的函数get_anser
    services/retrieval_service.py:文件检索
config：配置文件，包含路径等信息
requirements.txt:包以及相应的版本
run.py:运行
运行步骤：
1.先安装对应的包 pip install requirements.txt
2.运行crawler.py文件
3.运行embedding_processor.py文件
4.运行run.py文件
模型：
这里没有放模型，可以从Huggingface官网（https://huggingface.co/）、魔搭社区（https://www.modelscope.cn/home）下载
