#!/usr/bin/env python3
"""
简化的法律问题批量查询脚本
直接处理law_qa_samples_100.csv文件
"""

import csv
import json
import time
import requests
import re
from datetime import datetime
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_api_health(api_url="http://localhost:8000"):
    """检查API服务是否正常运行"""
    try:
        response = requests.get(f"{api_url}/health", timeout=15)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"API健康检查失败: {e}")
        return False

def query_question(question, api_url="http://localhost:8000"):
    """查询单个问题"""
    try:
        payload = {
            "question": question,
            "show_results": False
        }
        
        response = requests.post(
            f"{api_url}/query",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('answer', '无回答')
        else:
            logger.error(f"API请求失败: {response.status_code} - {response.text}")
            return f"API请求失败: {response.status_code}"
            
    except requests.exceptions.Timeout:
        logger.error(f"查询超时: {question}")
        return "查询超时"
    except Exception as e:
        logger.error(f"查询异常: {e}")
        return f"查询异常: {str(e)}"

def main():
    """主函数"""
    csv_file = "law_qa_samples_100.csv"
    api_url = "http://localhost:8000"
    
    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件不存在: {csv_file}")
        return
    
    # 检查API服务状态
    print("🔍 检查API服务状态...")
    if not check_api_health(api_url):
        print("❌ API服务不可用，请确保FastAPI服务正在运行")
        print("   请运行: python restful/main.py")
        return
    
    print("✅ API服务正常")
    
    # 读取CSV数据
    print(f"📖 读取CSV文件: {csv_file}")
    data = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        print(f"✅ 成功加载 {len(data)} 条数据")
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {e}")
        return
    
    # 确保有model_output列
    if data and 'model_output' not in data[0]:
        for row in data:
            row['model_output'] = ''
    
    # 统计需要处理的数据（包括查询超时的记录）
    need_process = []
    for row in data:
        current_output = row.get('model_output', '').strip()
        if not current_output or current_output == "查询超时":
            need_process.append(row)
    
    print(f"📊 需要处理 {len(need_process)} 条数据")
    if len(need_process) == 0:
        print("✅ 所有数据都已有有效输出，无需处理")
        return
    
    # 统计重试的记录数量
    retry_count = sum(1 for row in data if row.get('model_output', '').strip() == "查询超时")
    if retry_count > 0:
        print(f"🔄 其中 {retry_count} 条为查询超时，将重新尝试")
    
    # 开始处理
    print("🚀 开始批量查询...")
    start_time = datetime.now()
    
    processed = 0
    for i, row in enumerate(data):
        question = row.get('question', '').strip()
        
        if not question:
            print(f"⚠️  第 {i+1} 行没有问题，跳过")
            continue
        
        # 检查是否已经有输出，但排除"查询超时"的情况
        current_output = row.get('model_output', '').strip()
        if current_output and current_output != "查询超时":
            continue
        
        # 如果是查询超时，记录重试信息
        if current_output == "查询超时":
            print(f"🔄 检测到查询超时，重新尝试第 {i+1} 条")
        
        processed += 1
        print(f"📝 处理第 {processed}/{len(need_process)} 条: {question[:50]}...")
        
        # 查询API
        answer = query_question(question, api_url)
        # 清理答案中的换行符和多余空格，避免影响CSV格式
        cleaned_answer = answer.replace('\n', ' ').replace('\r', ' ').strip()
        # 将多个连续空格替换为单个空格
        cleaned_answer = re.sub(r'\s+', ' ', cleaned_answer)
        row['model_output'] = cleaned_answer
        
        # 立即保存结果到文件
        try:
            fieldnames = data[0].keys()
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            print(f"✅ 查询完成并已保存")
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            # 即使保存失败，也继续处理下一条
        
        # 延迟以避免过于频繁的请求
        if processed < len(need_process):
            time.sleep(1.0)
    
    # 处理完成
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"✅ 批量处理完成！")
    print(f"📄 输出文件: {csv_file}")
    print(f"📊 处理数据: {processed} 条")
    print(f"⏱️  耗时: {duration}")

if __name__ == "__main__":
    main()
