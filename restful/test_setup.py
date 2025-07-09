#!/usr/bin/env python3
"""
测试路径配置和数据文件访问
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 添加restful目录到系统路径
restful_dir = Path(__file__).parent
sys.path.insert(0, str(restful_dir))

def test_path_config():
    """测试路径配置"""
    print("=== 路径配置测试 ===")
    
    try:
        from path_config import verify_data_files, get_project_root
        
        print(f"项目根目录: {get_project_root()}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"脚本目录: {Path(__file__).parent}")
        
        # 验证数据文件
        index_path, metadata_path = verify_data_files()
        print(f"✅ FAISS索引文件: {index_path}")
        print(f"✅ 元数据文件: {metadata_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 路径配置测试失败: {e}")
        return False

def test_agent_initialization():
    """测试Agent初始化"""
    print("\n=== Agent初始化测试 ===")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY 未配置")
            return False
        
        print(f"✅ API Key已配置: {api_key[:10]}...")
        
        from agent import LegalConsultationSystem
        
        # 尝试初始化咨询系统
        system = LegalConsultationSystem(api_key)
        print("✅ 咨询系统初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return False

def test_fastapi_imports():
    """测试FastAPI导入"""
    print("\n=== FastAPI导入测试 ===")
    
    try:
        import fastapi
        import uvicorn
        import pydantic
        
        print(f"✅ FastAPI版本: {fastapi.__version__}")
        print(f"✅ Uvicorn版本: {uvicorn.__version__}")
        print(f"✅ Pydantic版本: {pydantic.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ FastAPI导入失败: {e}")
        print("请运行: pip install fastapi uvicorn pydantic")
        return False

def test_main_imports():
    """测试main.py导入"""
    print("\n=== main.py导入测试 ===")
    
    try:
        # 更改到restful目录
        os.chdir(restful_dir)
        
        from main import app, get_consultation_system
        print("✅ main.py导入成功")
        
        # 尝试获取咨询系统
        system = get_consultation_system()
        print("✅ 咨询系统获取成功")
        
        return True
        
    except Exception as e:
        print(f"❌ main.py导入失败: {e}")
        return False

def main():
    """主函数"""
    print("法律咨询API - 系统检查")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_path_config,
        test_agent_initialization,
        test_fastapi_imports,
        test_main_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ 所有测试通过 ({passed}/{total})")
        print("系统准备就绪，可以启动API服务！")
        print("\n启动命令:")
        print("cd restful && python main.py")
        print("或者:")
        print("cd restful && uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print(f"❌ 测试失败 ({passed}/{total})")
        print("请解决上述问题后再次运行测试")

if __name__ == "__main__":
    main()
