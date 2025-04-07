import faiss
import pandas as pd
import numpy as np
from config import Config
from RAG.core.models.embedding_model import get_embedding_model


def retrieve_documents(query, top_k=3):
    model = get_embedding_model()
    # 使用获取到的嵌入模型model对查询语句query进行编码
    query_emb = model.encode(query, convert_to_numpy=True).astype("float32")

    #  使用faiss库的read_index函数读取预先构建好的Faiss索引
    index = faiss.read_index(Config.FAISS_INDEX_PATH)
    distances, indices = index.search(np.array([query_emb]), top_k)
    print(indices)
    # 使用pandas库的read_pickle函数读取存储文档信息的DataFrame
    df = pd.read_pickle(Config.NEWS_DF_PATH)
    # 根据检索得到的索引indices，从DataFrame中获取对应的文档
    retrieved_docs = df.iloc[indices[0]].to_dict("records")
    return retrieved_docs