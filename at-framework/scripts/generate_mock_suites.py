#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 existing_suites 变量内容，用于 Dify Mock 调试
用法: python generate_mock_suites.py [suite_name]
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_existing_suites(base_dir="testcase/vega", suite_name="测试数据源"):
    """生成 suite 文件的 YAML 内容"""
    suite_path = os.path.join(base_dir, "suites", f"{suite_name}.yaml")
    
    if not os.path.exists(suite_path):
        print(f"❌ 错误：文件不存在: {suite_path}")
        return None
    
    with open(suite_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=" * 80)
    print(f"📄 Suite 文件: {suite_path}")
    print("=" * 80)
    print("\n✅ 以下是 existing_suites 变量的内容，可以直接复制到 Dify 中：\n")
    print("-" * 80)
    print(content)
    print("-" * 80)
    print(f"\n📊 文件大小: {len(content)} 字符")
    print(f"📝 行数: {len(content.splitlines())} 行")
    
    return content

if __name__ == "__main__":
    suite_name = sys.argv[1] if len(sys.argv) > 1 else "测试数据源"
    base_dir = sys.argv[2] if len(sys.argv) > 2 else "testcase/vega"
    
    generate_existing_suites(base_dir, suite_name)
