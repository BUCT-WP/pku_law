import pandas as pd
from openai import OpenAI
import time

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-izTwXHKjIe5OPSt9C1D81115329747C29dB29c6eEc074222",
    base_url="http://10.12.112.166:5555/v1"
)

# 定义评估函数
def evaluate_answer(question, expected_answer, model_output):
    prompt = f"""
你是一个法律专家，负责评估一个大语言模型输出的答案是否准确地回答了问题，并与标准答案一致。
不要输出markdown格式，只输出纯文本，不能包含换行符
请对比以下内容：
问题：{question}
标准答案：{expected_answer}
模型输出：{model_output}

请回答以下两个问题：
1. 模型输出是否与标准答案一致？（是/否）
2. 如果不一致，请简要说明差异（如果一致请写“无差异”）。
请以以下格式输出：
一致性: 是/否
差异说明: ...
"""

    try:
        response = client.chat.completions.create(
            model="qwen2.5:14b",
            messages=[
                {"role": "system", "content": "你是一个法律专家，擅长评估法律问答的一致性。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"调用模型失败: {e}")
        return "评估失败"

# 文件路径
input_file = 'law_qa_samples_100.csv'

# 读取原始数据
df = pd.read_csv(input_file)

# 确保 'note' 列存在
if 'note' not in df.columns:
    df['note'] = ''

# 逐条处理
for index, row in df.iterrows():
    # 判断 note 是否为空
    if pd.isna(row['note']) or row['note'].strip() == '':
        print(f"正在处理第 {index + 1} 条记录（note为空，需要处理）...")
        evaluation = evaluate_answer(row['question'], row['expected_answer'], row['model_output'])
        
        # 去除评估结果中的换行符
        evaluation_clean = evaluation.replace('\n', ' ').replace('\r', ' ').strip()
        df.at[index, 'note'] = evaluation_clean

        # 每处理一条就写入文件
        try:
            df.to_csv(input_file, index=False)
            print(f"第 {index + 1} 条记录已写入文件")
        except Exception as e:
            print(f"写入文件失败: {e}")

        time.sleep(1)  # 控制请求频率
    else:
        print(f"第 {index + 1} 条记录的 note 字段已有内容，跳过处理。")

print(f"评估完成，结果已成功写入原文件：{input_file}")