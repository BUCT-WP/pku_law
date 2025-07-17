#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV文件拆分脚本
将包含100条数据的CSV文件拆分为4个文件，每个文件包含25条数据
"""

import csv
import os

def split_csv_file(input_file, output_prefix="part", rows_per_file=25):
    """
    拆分CSV文件
    
    Args:
        input_file (str): 输入CSV文件路径
        output_prefix (str): 输出文件前缀
        rows_per_file (int): 每个文件包含的数据行数
    """
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 '{input_file}' 不存在")
        return
    
    try:
        # 读取原始CSV文件
        with open(input_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # 读取标题行
            header = next(reader)
            print(f"标题行：{header}")
            
            # 读取所有数据行
            data_rows = list(reader)
            total_rows = len(data_rows)
            print(f"总数据行数：{total_rows}")
            
            # 计算需要创建的文件数
            num_files = (total_rows + rows_per_file - 1) // rows_per_file
            print(f"将创建 {num_files} 个文件，每个文件包含最多 {rows_per_file} 行数据")
            
            # 获取输入文件的目录
            input_dir = os.path.dirname(input_file)
            
            # 拆分数据并写入文件
            for i in range(num_files):
                start_idx = i * rows_per_file
                end_idx = min((i + 1) * rows_per_file, total_rows)
                
                # 生成输出文件名
                output_file = os.path.join(input_dir, f"{output_prefix}_{i+1}.csv")
                
                # 写入文件
                with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                    writer = csv.writer(outfile)
                    
                    # 写入标题行
                    writer.writerow(header)
                    
                    # 写入数据行
                    for row in data_rows[start_idx:end_idx]:
                        writer.writerow(row)
                
                actual_rows = end_idx - start_idx
                print(f"已创建文件：{output_file} (包含 {actual_rows} 行数据)")
        
        print("\n拆分完成！")
        
    except Exception as e:
        print(f"处理文件时发生错误：{str(e)}")

def main():
    """主函数"""
    # 设置输入文件路径
    input_file = "/Users/wp/Documents/pku_law/law_qa_samples_100.csv"
    
    # 设置输出文件前缀
    output_prefix = "law_qa_samples_part"
    
    # 设置每个文件包含的行数
    rows_per_file = 25
    
    print("开始拆分CSV文件...")
    print(f"输入文件：{input_file}")
    print(f"输出文件前缀：{output_prefix}")
    print(f"每个文件包含：{rows_per_file} 行数据")
    print("-" * 50)
    
    # 执行拆分
    split_csv_file(input_file, output_prefix, rows_per_file)

if __name__ == "__main__":
    main()
