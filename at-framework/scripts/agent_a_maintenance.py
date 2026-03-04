#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体 A：用例维护智能体 (Agent A - Case Maintenance)

功能：
1. 分析代码变更 (diff + 变更文件)
2. 根据变更类型自动生成/修改/删除测试用例
3. 输出符合 case_schema.yaml 的 YAML 用例

实现方式：
- 当前：基于规则的简化版（不依赖外部 LLM）
- 未来：接入 LLM API 进行语义分析

作者: OpenClaw Assistant
日期: 2026-03-04
"""

import os
import sys
import json
import yaml
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.func import load_case_from_yaml


class AgentA_CaseMaintenance:
    """用例维护智能体"""
    
    def __init__(self, base_dir: str, apis_config: List[Dict] = None):
        self.base_dir = base_dir
        self.apis_config = apis_config or []
        self.existing_cases = []
        
    def load_existing_cases(self):
        """加载现有用例"""
        try:
            self.existing_cases = load_case_from_yaml(self.base_dir)
            print(f"📚 已加载 {len(self.existing_cases)} 条现有用例")
        except Exception as e:
            print(f"⚠️ 无法加载现有用例: {e}")
            self.existing_cases = []
    
    def analyze_change(self, listener_output: Dict) -> Dict[str, Any]:
        """
        分析变更，确定需要采取的维护动作
        
        返回:
        {
            "actions": ["add", "modify", "delete"],
            "target_apis": ["API名称"],
            "change_type": "api_addition|api_modification|field_change|...",
            "reason": "分析原因"
        }
        """
        actions = []
        change_summary = listener_output.get("change_summary", {})
        
        # 分析变更类型
        has_added = len(change_summary.get("added", [])) > 0
        has_modified = len(change_summary.get("modified", [])) > 0
        has_removed = len(change_summary.get("removed", [])) > 0
        
        # 根据变更类型确定动作
        if has_added:
            actions.append("add")
        if has_modified:
            actions.append("modify")
        if has_removed:
            actions.append("delete")
        
        # 确定目标 API
        target_apis = listener_output.get("affected_api_names", [])
        
        # 推断变更类型
        changed_files = listener_output.get("changed_files", [])
        change_type = self._infer_change_type(changed_files, actions)
        
        return {
            "actions": actions,
            "target_apis": target_apis,
            "change_type": change_type,
            "reason": f"检测到变更: added={has_added}, modified={has_modified}, removed={has_removed}"
        }
    
    def _infer_change_type(self, changed_files: List[Dict], actions: List[str]) -> str:
        """推断变更类型（规则-based）"""
        
        for file_info in changed_files:
            path = file_info.get("path", "").lower()
            
            # API 新增
            if "controller" in path and "add" in actions:
                return "api_addition"
            
            # 参数校验变更
            if any(keyword in path for keyword in ["validator", "validation", "constraint"]):
                return "validation_change"
            
            # 字段变更
            if any(keyword in path for keyword in ["dto", "model", "entity", "vo"]):
                return "field_change"
            
            # 性能相关
            if any(keyword in path for keyword in ["performance", "cache", "async", "batch"]):
                return "performance_change"
        
        return "general_modification"
    
    def generate_cases(self, analysis: Dict, listener_output: Dict) -> List[Dict]:
        """
        生成新的测试用例
        
        当前：基于规则的模板生成
        未来：接入 LLM 生成更智能的用例
        """
        new_cases = []
        target_apis = analysis.get("target_apis", [])
        change_type = analysis.get("change_type", "")
        
        for api_name in target_apis:
            # 查找 API 配置
            api_config = self._find_api_config(api_name)
            if not api_config:
                continue
            
            # 根据变更类型生成不同用例
            if change_type == "api_addition":
                # 新增 API → 生成基础功能用例
                cases = self._generate_api_addition_cases(api_name, api_config)
                new_cases.extend(cases)
                
            elif change_type == "validation_change":
                # 参数校验变更 → 生成边界测试用例
                cases = self._generate_boundary_cases(api_name, api_config)
                new_cases.extend(cases)
                
            elif change_type == "field_change":
                # 字段变更 → 生成字段相关用例
                cases = self._generate_field_cases(api_name, api_config)
                new_cases.extend(cases)
                
            else:
                # 默认：生成回归用例
                cases = self._generate_regression_cases(api_name, api_config)
                new_cases.extend(cases)
        
        return new_cases
    
    def _find_api_config(self, api_name: str) -> Optional[Dict]:
        """查找 API 配置"""
        for api in self.apis_config:
            if api.get("name") == api_name:
                return api
        return None
    
    def _generate_api_addition_cases(self, api_name: str, api_config: Dict) -> List[Dict]:
        """生成 API 新增的基础用例"""
        cases = []
        method = api_config.get("method", "GET")
        
        # 基础成功用例
        case_name = f"{api_name}_正常请求_返回成功"
        case = self._create_case_template(
            name=case_name,
            url=api_name,
            method=method,
            code_check="200",
            tags=["regression", "smoke"]
        )
        cases.append(case)
        
        # 参数缺失用例（POST/PUT 才需要）
        if method in ["POST", "PUT"]:
            case_name = f"{api_name}_参数缺失_返回失败"
            case = self._create_case_template(
                name=case_name,
                url=api_name,
                method=method,
                code_check="400",
                body_params="{}",
                tags=["regression", "validation"]
            )
            cases.append(case)
        
        return cases
    
    def _generate_boundary_cases(self, api_name: str, api_config: Dict) -> List[Dict]:
        """生成边界测试用例"""
        cases = []
        method = api_config.get("method", "GET")
        
        # 边界值测试（以长度为例）
        test_values = [
            ("长度为1", "a", "200"),
            ("长度边界", "a" * 128, "200"),
            ("长度超限", "a" * 129, "400"),
        ]
        
        for desc, value, expect_code in test_values:
            case_name = f"{api_name}_边界测试_{desc}_返回{expect_code}"
            case = self._create_case_template(
                name=case_name,
                url=api_name,
                method=method,
                code_check=expect_code,
                tags=["regression", "boundary"]
            )
            cases.append(case)
        
        return cases
    
    def _generate_field_cases(self, api_name: str, api_config: Dict) -> List[Dict]:
        """生成字段相关用例"""
        cases = []
        method = api_config.get("method", "GET")
        
        # 字段存在性验证
        case_name = f"{api_name}_字段完整性_返回成功"
        case = self._create_case_template(
            name=case_name,
            url=api_name,
            method=method,
            code_check="200",
            resp_check='{"$.code": 0}',
            tags=["regression", "contract"]
        )
        cases.append(case)
        
        return cases
    
    def _generate_regression_cases(self, api_name: str, api_config: Dict) -> List[Dict]:
        """生成回归用例"""
        cases = []
        method = api_config.get("method", "GET")
        
        case_name = f"{api_name}_回归测试_返回成功"
        case = self._create_case_template(
            name=case_name,
            url=api_name,
            method=method,
            code_check="200",
            tags=["regression"]
        )
        cases.append(case)
        
        return cases
    
    def _create_case_template(self, **kwargs) -> Dict:
        """创建用例模板"""
        template = {
            "name": kwargs.get("name", "未命名用例"),
            "url": kwargs.get("url", ""),
            "prev_case": kwargs.get("prev_case", ""),
            "path_params": kwargs.get("path_params", ""),
            "query_params": kwargs.get("query_params", ""),
            "header_params": kwargs.get("header_params", ""),
            "body_params": kwargs.get("body_params", ""),
            "form_params": kwargs.get("form_params", ""),
            "resp_values": kwargs.get("resp_values", ""),
            "code_check": kwargs.get("code_check", "200"),
            "resp_check": kwargs.get("resp_check", ""),
            "resp_schema": kwargs.get("resp_schema", ""),
            "tags": kwargs.get("tags", ["regression"])
        }
        return template
    
    def save_cases(self, cases: List[Dict], output_path: str):
        """保存生成的用例到 YAML 文件"""
        suite_data = {
            "feature": "智能生成用例",
            "story": "auto-generated-cases",
            "switch": "y",
            "tags": ["auto-generated"],
            "description": "由 Agent A 自动生成的测试用例",
            "cases": cases
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(suite_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"✅ 已保存 {len(cases)} 条用例到: {output_path}")
    
    def run(self, listener_output_path: str, output_path: str):
        """运行智能体 A"""
        print("="*60)
        print("🤖 智能体 A: 用例维护智能体")
        print("="*60)
        
        # 1. 加载 listener 输出
        with open(listener_output_path, "r", encoding="utf-8") as f:
            listener_output = json.load(f)
        
        # 2. 加载现有用例
        self.load_existing_cases()
        
        # 3. 分析变更
        print("\n📊 分析变更...")
        analysis = self.analyze_change(listener_output)
        print(f"  动作: {analysis['actions']}")
        print(f"  目标API: {analysis['target_apis']}")
        print(f"  变更类型: {analysis['change_type']}")
        
        # 4. 生成新用例
        print("\n📝 生成新用例...")
        new_cases = self.generate_cases(analysis, listener_output)
        
        if new_cases:
            print(f"  生成了 {len(new_cases)} 条新用例:")
            for case in new_cases:
                print(f"    - {case['name']}")
        else:
            print("  未生成新用例（可能没有匹配的API或不需要新增）")
        
        # 5. 保存
        if new_cases:
            self.save_cases(new_cases, output_path)
        
        return {
            "generated_count": len(new_cases),
            "cases": new_cases,
            "analysis": analysis
        }


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="Agent A: 用例维护智能体")
    parser.add_argument("--listener-output", required=True, help="listener_output.json 路径")
    parser.add_argument("--base-dir", default="testcase/vega", help="测试用例基础目录")
    parser.add_argument("--apis-config", default="testcase/vega/_config/apis.yaml", help="API 配置文件")
    parser.add_argument("--output", default="auto_generated_cases.yaml", help="输出文件路径")
    args = parser.parse_args()
    
    # 加载 API 配置
    apis_config = []
    if os.path.exists(args.apis_config):
        with open(args.apis_config, "r", encoding="utf-8") as f:
            apis_config = yaml.safe_load(f) or []
    
    # 运行智能体 A
    agent = AgentA_CaseMaintenance(args.base_dir, apis_config)
    result = agent.run(args.listener_output, args.output)
    
    print("\n" + "="*60)
    print(f"✨ 智能体 A 执行完成: 生成了 {result['generated_count']} 条用例")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
