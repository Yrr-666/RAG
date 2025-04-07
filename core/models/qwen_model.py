import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from RAG.config import Config

def get_deepseek_model():
    tokenizer = AutoTokenizer.from_pretrained(Config.DEEPSEEK_MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        Config.DEEPSEEK_MODEL_PATH,
        torch_dtype=torch.float32,  # 指定全精度
        device_map="cpu"  # 明确使用CPU
    ).float()  # 双重保险：转换为float32
    # 强制将模型加载到 GPU（如果可用）
    if torch.cuda.is_available():
        model = model.to("cuda")
    return model, tokenizer
