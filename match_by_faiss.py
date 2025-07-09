import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
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

# 加载模型和索引
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 从环境变量获取文件路径
faiss_index_path = get_data_file_path(os.getenv("FAISS_INDEX_PATH", "law_index.bin"))
metadata_path = get_data_file_path(os.getenv("METADATA_PATH", "metadata.pkl"))

index = faiss.read_index(faiss_index_path)

with open(metadata_path, 'rb') as f:
    metadata = pickle.load(f)

# 查询
query = "夫妻共同债务如何认定"
query_vec = model.encode([query])
k = 5
distances, indices = index.search(np.array(query_vec), k)

print("Top results:")
for idx, i in enumerate(indices[0]):
    print(f"\nScore: {1 / (1 + distances[0][idx]):.4f}")
    print(f"法规名称: {metadata[i]['law_name']}")
    print(f"文件名: {metadata[i]['filename']}")
    print(f"内容: {metadata[i]['content']}")
    print("-" * 50)