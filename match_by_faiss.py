import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 加载模型和索引
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
index = faiss.read_index('law_index.bin')

with open('metadata.pkl', 'rb') as f:
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