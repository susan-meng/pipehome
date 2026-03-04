#!/usr/bin/env python3
"""
本地测试版智能体 C - 不依赖外部库
"""

import os
import sys
import json
import yaml
from typing import List, Dict, Any


class AgentC_Local:
    """本地测试用例筛选器"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.all_cases = []
    
    def load_all_cases(self):
        """加载所有用例"""
        self.all_cases = []
        suites_dir = os.path.join(self.base_dir, "suites")
        
        if not os.path.exists(suites_dir):
            print(f"⚠️ 套件目录不存在: {suites_dir}")
            return
        
        for filename in os.listdir(suites_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(suites_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        suite = yaml.safe_load(f)
                        if suite and "cases" in suite:
                            for case in suite["cases"]:
                                case["_suite"] = filename
                                self.all_cases.append(case)
                except Exception as e:
                    print(f"⚠️ 无法加载 {filename}: {e}")
        
        print(f"📚 已加载 {len(self.all_cases)} 条用例")
    
    def create_execution_plan(self, listener_output: Dict, dimension_analysis: Dict) -> Dict:
        """创建执行计划"""
        batches = []
        affected_apis = listener_output.get("affected_api_names", [])
        scopes = listener_output.get("scopes", [])
        dimensions = dimension_analysis.get("dimensions", ["functional"])
        
        # 批次1: 新增功能相关
        if affected_apis:
            batch1_cases = self._select_by_apis(affected_apis)
            if batch1_cases:
                batches.append({
                    "priority": 1,
                    "label": "新增功能相关",
                    "case_names": [c["name"] for c in batch1_cases],
                    "count": len(batch1_cases)
                })
        
        # 批次2: 回归相关
        if scopes or not affected_apis:
            batch2_cases = self._select_by_tags(["regression"], batches)
            if batch2_cases:
                batches.append({
                    "priority": 2,
                    "label": "回归测试",
                    "case_names": [c["name"] for c in batch2_cases],
                    "count": len(batch2_cases)
                })
        
        # 批次3+: 按维度
        for dim in dimensions:
            if dim == "functional":
                continue
            cases = self._select_by_tags([dim], batches)
            if cases:
                batches.append({
                    "priority": 3 + len(batches),
                    "label": f"{dim}测试",
                    "case_names": [c["name"] for c in cases],
                    "count": len(cases)
                })
        
        total = sum(b["count"] for b in batches)
        
        return {
            "mode": "case_names",
            "batches": batches,
            "total_cases": total,
            "execution_summary": f"共 {len(batches)} 个批次，{total} 条用例"
        }
    
    def _select_by_apis(self, api_names: List[str]) -> List[Dict]:
        """按 API 筛选"""
        selected = []
        for case in self.all_cases:
            if case.get("url") in api_names:
                selected.append(case)
        return selected
    
    def _select_by_tags(self, tags: List[str], exclude_batches: List[Dict]) -> List[Dict]:
        """按标签筛选（排除已选）"""
        selected_names = set()
        for batch in exclude_batches:
            selected_names.update(batch.get("case_names", []))
        
        selected = []
        for case in self.all_cases:
            if case["name"] in selected_names:
                continue
            case_tags = case.get("tags", [])
            if any(t in case_tags for t in tags):
                selected.append(case)
        return selected
    
    def run(self, listener_output_path: str, dimension_path: str, output_path: str):
        """运行"""
        print("="*60)
        print("🤖 智能体 C: 用例筛选与执行智能体 (本地版)")
        print("="*60)
        
        with open(listener_output_path, "r") as f:
            listener_output = json.load(f)
        
        with open(dimension_path, "r") as f:
            dimension_analysis = json.load(f)
        
        print("\n📊 加载用例池...")
        self.load_all_cases()
        
        print("\n📝 创建执行计划...")
        plan = self.create_execution_plan(listener_output, dimension_analysis)
        
        print(f"\n🎯 执行计划:")
        print(f"  总批次: {len(plan['batches'])}")
        print(f"  总用例: {plan['total_cases']}")
        for batch in plan["batches"]:
            print(f"  批次 {batch['priority']}: {batch['label']} - {batch['count']} 条")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 执行计划已保存到: {output_path}")
        return plan


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--listener-output", required=True)
    parser.add_argument("--dimension-analysis", required=True)
    parser.add_argument("--base-dir", default="testcase/vega")
    parser.add_argument("--output", default="/tmp/local_execution_plan.json")
    args = parser.parse_args()
    
    agent = AgentC_Local(args.base_dir)
    agent.run(args.listener_output, args.dimension_analysis, args.output)
    print("\n✨ 智能体 C 执行完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
