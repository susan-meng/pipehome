#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体 C：用例筛选与执行智能体 (Agent C - Case Selector & Executor)

功能：
1. 根据测试维度和变更范围，智能筛选要执行的用例
2. 生成执行批次（优先级排序）
3. 输出执行计划供下游执行器使用

执行优先级：
1. 第一优先级：新增功能相关用例（与 commit 直接相关）
2. 第二优先级：回归相关用例（受影响模块）
3. 第三优先级：按维度评估的用例（边界/性能等）

作者: OpenClaw Assistant
日期: 2026-03-04
"""

import os
import sys
import json
import yaml
from typing import List, Dict, Any, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.func import get_cases, load_case_from_yaml


class AgentC_CaseSelector:
    """用例筛选与执行智能体"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.all_cases = []
    
    def load_all_cases(self):
        """加载所有用例"""
        try:
            self.all_cases = load_case_from_yaml(self.base_dir)
            print(f"📚 已加载 {len(self.all_cases)} 条用例")
        except Exception as e:
            print(f"⚠️ 无法加载用例: {e}")
            self.all_cases = []
    
    def create_execution_plan(self, 
                            listener_output: Dict, 
                            dimension_analysis: Dict) -> Dict[str, Any]:
        """
        创建执行计划
        
        返回:
        {
            "mode": "case_names" | "filter",
            "batches": [
                {
                    "priority": 1,
                    "label": "新增功能相关",
                    "case_names": [...],
                    "filter": {...}
                }
            ],
            "total_cases": 10,
            "execution_summary": "执行摘要"
        }
        """
        batches = []
        affected_apis = listener_output.get("affected_api_names", [])
        scopes = listener_output.get("scopes", [])
        dimensions = dimension_analysis.get("dimensions", ["functional"])
        
        # 批次1: 新增功能相关用例（按 affected_apis 筛选）
        if affected_apis:
            batch1_cases = self._select_by_apis(affected_apis)
            if batch1_cases:
                batches.append({
                    "priority": 1,
                    "label": "新增功能相关",
                    "case_names": [c["name"] for c in batch1_cases],
                    "count": len(batch1_cases),
                    "description": f"与变更直接相关的 {len(affected_apis)} 个 API"
                })
        
        # 批次2: 回归相关用例（按 scope + regression tags）
        if scopes:
            batch2_cases = self._select_by_scope_regression(scopes, batches)
            if batch2_cases:
                batches.append({
                    "priority": 2,
                    "label": "回归测试",
                    "case_names": [c["name"] for c in batch2_cases],
                    "count": len(batch2_cases),
                    "description": f"受影响 scope 的回归用例"
                })
        
        # 批次3: 按维度筛选（边界/性能等）
        dimension_batches = self._select_by_dimensions(dimensions, scopes, batches)
        batches.extend(dimension_batches)
        
        # 计算总数
        total_cases = sum(b["count"] for b in batches)
        
        return {
            "mode": "case_names",
            "batches": batches,
            "total_cases": total_cases,
            "execution_summary": f"共 {len(batches)} 个批次，{total_cases} 条用例"
        }
    
    def _select_by_apis(self, api_names: List[str]) -> List[Dict]:
        """根据 API 名称筛选用例"""
        selected = []
        
        for case in self.all_cases:
            case_url = case.get("url", "")
            # 匹配 API 名称（用例的 url 字段对应 apis.yaml 的 name）
            if case_url in api_names:
                selected.append(case)
        
        return selected
    
    def _select_by_scope_regression(self, scopes: List[str], existing_batches: List[Dict]) -> List[Dict]:
        """根据 scope 筛选回归用例"""
        selected = []
        
        # 已选中的用例名（去重）
        selected_names = set()
        for batch in existing_batches:
            selected_names.update(batch.get("case_names", []))
        
        # 筛选 regression tag 的用例
        for case in self.all_cases:
            if case["name"] in selected_names:
                continue  # 跳过已选中的
            
            tags = case.get("tags", [])
            if "regression" in tags:
                selected.append(case)
        
        return selected
    
    def _select_by_dimensions(self, dimensions: List[str], scopes: List[str], 
                             existing_batches: List[Dict]) -> List[Dict]:
        """根据测试维度筛选用例"""
        batches = []
        
        # 已选中的用例名
        selected_names = set()
        for batch in existing_batches:
            selected_names.update(batch.get("case_names", []))
        
        # 维度到 tags 的映射
        dimension_tags = {
            "contract": ["contract"],
            "boundary": ["boundary"],
            "stress": ["stress"],
            "performance": ["performance"]
        }
        
        dimension_labels = {
            "contract": "契约测试",
            "boundary": "边界测试",
            "stress": "压力测试",
            "performance": "性能测试"
        }
        
        for dim in dimensions:
            if dim in ["functional"]:
                continue  # functional 已在批次1/2覆盖
            
            tags = dimension_tags.get(dim, [])
            if not tags:
                continue
            
            selected = []
            for case in self.all_cases:
                if case["name"] in selected_names:
                    continue
                
                case_tags = case.get("tags", [])
                if any(t in case_tags for t in tags):
                    selected.append(case)
            
            if selected:
                batches.append({
                    "priority": 3 + len(batches),
                    "label": dimension_labels.get(dim, dim),
                    "case_names": [c["name"] for c in selected],
                    "count": len(selected),
                    "description": f"{dim} 维度测试"
                })
        
        return batches
    
    def run(self, listener_output_path: str, dimension_path: str, output_path: str):
        """运行智能体 C"""
        print("="*60)
        print("🤖 智能体 C: 用例筛选与执行智能体")
        print("="*60)
        
        # 1. 加载输入
        with open(listener_output_path, "r", encoding="utf-8") as f:
            listener_output = json.load(f)
        
        with open(dimension_path, "r", encoding="utf-8") as f:
            dimension_analysis = json.load(f)
        
        # 2. 加载所有用例
        print("\n📊 加载用例池...")
        self.load_all_cases()
        
        # 3. 创建执行计划
        print("\n📝 创建执行计划...")
        plan = self.create_execution_plan(listener_output, dimension_analysis)
        
        # 4. 输出结果
        print(f"\n🎯 执行计划:")
        print(f"  总批次: {len(plan['batches'])}")
        print(f"  总用例: {plan['total_cases']}")
        print(f"\n  批次详情:")
        for batch in plan["batches"]:
            print(f"    批次 {batch['priority']}: {batch['label']} - {batch['count']} 条用例")
            print(f"      ({batch['description']})")
        
        # 5. 保存
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 执行计划已保存到: {output_path}")
        
        return plan


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="Agent C: 用例筛选与执行智能体")
    parser.add_argument("--listener-output", required=True, help="listener_output.json 路径")
    parser.add_argument("--dimension-analysis", required=True, help="dimension_analysis.json 路径")
    parser.add_argument("--base-dir", default="testcase/vega", help="测试用例基础目录")
    parser.add_argument("--output", default="execution_plan.json", help="输出文件路径")
    args = parser.parse_args()
    
    # 运行智能体 C
    agent = AgentC_CaseSelector(args.base_dir)
    result = agent.run(args.listener_output, args.dimension_analysis, args.output)
    
    print("\n" + "="*60)
    print(f"✨ 智能体 C 执行完成: 创建了 {len(result['batches'])} 个执行批次")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
