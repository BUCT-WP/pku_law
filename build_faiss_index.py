import os
import re
import pickle
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_data_file_path(relative_path: str) -> str:
    """获取数据文件的绝对路径"""
    if os.path.isabs(relative_path):
        return relative_path
    
    # 相对于项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

# ========================
# 配置参数
# ========================
INPUT_DIR = './law'            # 存放法律文件的目录
# 从环境变量获取文件路径
INDEX_PATH = get_data_file_path(os.getenv("FAISS_INDEX_PATH", "law_index.bin"))
METADATA_PATH = get_data_file_path(os.getenv("METADATA_PATH", "metadata.pkl"))
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'  # 多语言句向量模型

# ========================
# 正则表达式匹配"第X条"结构
# ========================
def split_by_article(text):
    pattern = r'(第.*?条[\s\S]*?)(?=(第|$))'
    matches = re.findall(pattern, text, re.DOTALL)
    chunks = [match[0].strip() for match in matches if match[0].strip()]
    return chunks

def extract_law_name(filename):
    """从文件名提取法规名称"""
    # 移除 'English.txt' 后缀
    law_name = filename.replace('English.txt', '')
    return law_name

# ========================
# 主程序
# ========================

# 加载模型
print("Loading model...")
model = SentenceTransformer(MODEL_NAME)

all_chunks = []
all_metadata = []

# 遍历所有 .txt 文件
print("Processing files...")
for filename in tqdm(os.listdir(INPUT_DIR)):
    if filename.endswith('.txt'):
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # 按"第X条"切分
        chunks = split_by_article(text)
        
        # 提取法规名称
        law_name = extract_law_name(filename)

        # 添加到列表中
        all_chunks.extend(chunks)
        all_metadata.extend([{
            'filename': filename,
            'law_name': law_name,
            'content': chunk
        } for chunk in chunks])

# 向量化
print(f"Encoding {len(all_chunks)} chunks...")
vectors = model.encode(all_chunks, show_progress_bar=True, batch_size=32)
dimension = vectors.shape[1]

# 构建 FAISS 索引
print("Building FAISS index...")
index = faiss.IndexFlatL2(dimension)
index.add(np.array(vectors))

# 保存索引和元数据
print("Saving index and metadata...")
faiss.write_index(index, INDEX_PATH)
with open(METADATA_PATH, 'wb') as f:
    pickle.dump(all_metadata, f)

print("✅ Done!")
