import pandas as pd
import numpy as np
import faiss
from RAG.config import Config
from RAG.core.models.embedding_model import get_embedding_model
from RAG.utils.logger import logger
def process_embeddings():
    df = pd.read_csv(Config.RAW_DATA_PATH)
    model = get_embedding_model()

    # 将 content 列转换为字符串类型
    df["content"] = df["content"].astype(str)

    # 生成嵌入
    # 创建一个空列表embeddings，用于存储新闻内容的向量表示。
    embeddings = []
    # 遍历df["content"]中的每一个新闻内容
    for content in df["content"]:
        # 将每个新闻内容转换为向量,convert_to_numpy=True参数表示将结果转换为numpy数组
        emb = model.encode(content, convert_to_numpy=True)
        embeddings.append(emb)
    # faiss库通常要求输入的向量数据类型为float32
    embeddings = np.array(embeddings).astype("float32")

    # 创建FAISS索引
    # 获取向量的维度，embeddings.shape[1]表示向量的特征维度（假设embeddings是一个二维数组，第一维是样本数量，第二维是特征维度）
    dimension = embeddings.shape[1]
    # 创建一个faiss索引对象
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # 保存索引和元数据
    # FAISS_INDEX_PATH = os.path.join(PROCESSED_DATA_PATH, "news_index.faiss")
    # NEWS_DF_PATH = os.path.join(PROCESSED_DATA_PATH, "news_df.pkl")
    faiss.write_index(index, Config.FAISS_INDEX_PATH)
    df.to_pickle(Config.NEWS_DF_PATH)
    logger.info(f"Processed embeddings and saved to {Config.FAISS_INDEX_PATH}")


if __name__ == "__main__":
    process_embeddings()