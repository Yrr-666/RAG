import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    NEWS_URL = "https://www.nuc.edu.cn/index/zbxw.htm"
    START_DATE = "2025-03-25"  # 按需设置起始日期
    DATA_DIR = os.path.join(BASE_DIR, "data")
    RAW_DATA_PATH = os.path.join(DATA_DIR, "raw", "news_data.csv")
    PROCESSED_DATA_PATH = os.path.join(DATA_DIR, "processed")
    FAISS_INDEX_PATH = os.path.join(PROCESSED_DATA_PATH, "news_index.faiss")
    NEWS_DF_PATH = os.path.join(PROCESSED_DATA_PATH, "news_df.pkl")
    # 模型路径
    EMBEDDING_MODEL_PATH = os.path.join(BASE_DIR, "core", "models", "all-MiniLM-L6-v2")
    DEEPSEEK_MODEL_PATH = os.path.join(BASE_DIR, "core", "models", "qwen2.5-0.5B")
    # Flask 配置
    SECRET_KEY = "your-secret-key"
    DEBUG = True
    @staticmethod
    def create_directories():
        """
        检查并创建所需的目录
        """
        directories = [
            Config.DATA_DIR,
            os.path.dirname(Config.RAW_DATA_PATH),
            Config.PROCESSED_DATA_PATH,
            os.path.dirname(Config.FAISS_INDEX_PATH),
            os.path.dirname(Config.NEWS_DF_PATH),
            os.path.dirname(Config.EMBEDDING_MODEL_PATH),
            os.path.dirname(Config.DEEPSEEK_MODEL_PATH)
        ]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
# 在程序启动时调用该方法创建目录
Config.create_directories()
