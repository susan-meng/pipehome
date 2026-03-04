#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体 D：报告生成智能体 (Agent D - Report Generator)

功能：
1. 解析 Allure/JUnit 测试结果
2. 生成自然语言测试报告摘要
3. 提供结论和建议

作者: OpenClaw Assistant
日期: 2026-03-04
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from pathlib import Path


class AgentD_ReportGenerator:
    """报告生成智能体"""
    
    def __init__(self):
        self.test_results = {}
    
    def parse_junit_report(self, junit_path: str) -> Dict[str, Any]:
        """解析 JUnit XML 报告"""
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "pass_rate": 0.0,
            "duration": 0.0,
            "failed_cases": [],
            "test_suites": []
        }
        
        if not os.path.exists(junit_path):
            print(f"⚠️ JUnit 报告不存在: {junit_path}")
            return results
        
        try:
            tree = ET.parse(junit_path)
            root = tree.getroot()
            
            # 处理 testsuites 或 testsuite 根元素
            if root.tag == "testsuites":
                for suite in root.findall("testsuite"):
                    self._parse_test_suite(suite, results)
            elif root.tag == "testsuite":
                self._parse_test_suite(root, results)
            
            # 计算通过率
            if results["total"] > 0:
                results["pass_rate"] = round(results["passed"] / results["total"] * 100, 2)
            
        except Exception as e:
            print(f"⚠️ 解析 JUnit 报告失败: {e}")
        
        return results
    
    def _parse_test_suite(self, suite: ET.Element, results: Dict):
        """解析单个测试套件"""
        suite_name = suite.get("name", "Unknown")
        suite_tests = int(suite.get("tests", 0))
        suite_failures = int(suite.get("failures", 0))
        suite_errors = int(suite.get("errors", 0))
        suite_skipped = int(suite.get("skipped", 0))
        suite_time = float(suite.get("time", 0))
        
        results["total"] += suite_tests
        results["failed"] += suite_failures + suite_errors
        results["skipped"] += suite_skipped
        results["passed"] += suite_tests - suite_failures - suite_errors - suite_skipped
        results["duration"] += suite_time
        
        suite_info = {
            "name": suite_name,
            "tests": suite_tests,
            "passed": suite_tests - suite_failures - suite_errors - suite_skipped,
            "failed": suite_failures + suite_errors,
            "duration": suite_time
        }
        results["test_suites"].append(suite_info)
        
        # 解析失败的用例
        for case in suite.findall("testcase"):
            case_name = case.get("name", "Unknown")
            failure = case.find("failure")
            error = case.find("error")
            
            if failure is not None or error is not None:
                failure_info = {
                    "name": case_name,
                    "suite": suite_name,
                    "type": "failure" if failure is not None else "error",
                    "message": (failure.get("message", "") if failure is not None 
                               else error.get("message", "")),
                    "details": (failure.text if failure is not None 
                               else error.text)[:500]  # 截断详情
                }
                results["failed_cases"].append(failure_info)
    
    def generate_report(self, 
                       test_results: Dict, 
                       execution_plan: Dict = None,
                       dimension_analysis: Dict = None) -> str:
        """生成 Markdown 格式报告"""
        
        lines = []
        lines.append("# 🧪 智能测试报告")
        lines.append("")
        lines.append("## 📊 执行摘要")
        lines.append("")
        
        # 测试统计
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        lines.append(f"| 总用例数 | {test_results['total']} |")
        lines.append(f"| ✅ 通过 | {test_results['passed']} |")
        lines.append(f"| ❌ 失败 | {test_results['failed']} |")
        lines.append(f"| ⏭️ 跳过 | {test_results['skipped']} |")
        lines.append(f"| 📈 通过率 | {test_results['pass_rate']}% |")
        lines.append(f"| ⏱️ 总耗时 | {test_results['duration']:.2f}s |")
        lines.append("")
        
        # 执行维度（如果有）
        if dimension_analysis:
            lines.append("### 🎯 测试维度")
            lines.append("")
            dimensions = dimension_analysis.get("dimensions", [])
            lines.append(f"**执行的测试维度**: {', '.join(dimensions)}")
            lines.append("")
        
        # 执行批次（如果有）
        if execution_plan:
            lines.append("### 📋 执行批次")
            lines.append("")
            for batch in execution_plan.get("batches", []):
                lines.append(f"- **批次 {batch['priority']}: {batch['label']}** - {batch['count']} 条用例")
            lines.append("")
        
        # 失败详情
        if test_results["failed_cases"]:
            lines.append("## ❌ 失败用例详情")
            lines.append("")
            for i, case in enumerate(test_results["failed_cases"][:10], 1):  # 最多显示10个
                lines.append(f"### {i}. {case['name']}")
                lines.append(f"- **所属套件**: {case['suite']}")
                lines.append(f"- **错误类型**: {case['type']}")
                lines.append(f"- **错误信息**: {case['message']}")
                if case['details']:
                    lines.append(f"- **详情**: {case['details'][:200]}...")
                lines.append("")
            
            if len(test_results["failed_cases"]) > 10:
                lines.append(f"*还有 {len(test_results['failed_cases']) - 10} 个失败用例未显示*")
                lines.append("")
        
        # 结论和建议
        lines.append("## 💡 结论与建议")
        lines.append("")
        
        if test_results["pass_rate"] >= 95:
            lines.append("✅ **测试通过** - 通过率高于95%，代码质量良好，可以合并。")
        elif test_results["pass_rate"] >= 80:
            lines.append("⚠️ **测试通过（有警告）** - 通过率在80%-95%之间，建议检查失败用例。")
        elif test_results["pass_rate"] >= 60:
            lines.append("❌ **测试未通过** - 通过率低于80%，建议修复失败用例后重新测试。")
        else:
            lines.append("🚫 **测试严重失败** - 通过率低于60%，存在严重问题，不建议合并。")
        
        lines.append("")
        
        # 建议
        if test_results["failed"] > 0:
            lines.append("### 🔧 修复建议")
            lines.append("")
            lines.append("1. 优先修复影响核心功能的失败用例")
            lines.append("2. 检查失败的边界条件测试，确认是否是预期行为")
            lines.append("3. 如果测试用例本身需要更新，请联系测试团队")
            lines.append("")
        
        lines.append("---")
        lines.append("*本报告由智能体 D 自动生成*")
        
        return "\n".join(lines)
    
    def run(self, 
           junit_path: str, 
           execution_plan_path: str = None,
           dimension_analysis_path: str = None,
           output_path: str = None) -> str:
        """运行智能体 D"""
        print("="*60)
        print("🤖 智能体 D: 报告生成智能体")
        print("="*60)
        
        # 1. 解析测试结果
        print(f"\n📊 解析测试结果...")
        test_results = self.parse_junit_report(junit_path)
        print(f"  总用例: {test_results['total']}")
        print(f"  通过: {test_results['passed']}")
        print(f"  失败: {test_results['failed']}")
        print(f"  通过率: {test_results['pass_rate']}%")
        
        # 2. 加载执行计划（可选）
        execution_plan = None
        if execution_plan_path and os.path.exists(execution_plan_path):
            with open(execution_plan_path, "r", encoding="utf-8") as f:
                execution_plan = json.load(f)
            print(f"\n📋 加载执行计划: {execution_plan.get('execution_summary', '')}")
        
        # 3. 加载维度分析（可选）
        dimension_analysis = None
        if dimension_analysis_path and os.path.exists(dimension_analysis_path):
            with open(dimension_analysis_path, "r", encoding="utf-8") as f:
                dimension_analysis = json.load(f)
            print(f"\n🎯 测试维度: {', '.join(dimension_analysis.get('dimensions', []))}")
        
        # 4. 生成报告
        print(f"\n📝 生成报告...")
        report = self.generate_report(test_results, execution_plan, dimension_analysis)
        
        # 5. 保存报告
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n✅ 报告已保存到: {output_path}")
        
        # 6. 输出摘要到控制台
        print("\n" + "="*60)
        print("📄 报告摘要")
        print("="*60)
        print(report[:1000] + "..." if len(report) > 1000 else report)
        
        return report


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="Agent D: 报告生成智能体")
    parser.add_argument("--junit-report", required=True, help="JUnit XML 报告路径")
    parser.add_argument("--execution-plan", help="execution_plan.json 路径")
    parser.add_argument("--dimension-analysis", help="dimension_analysis.json 路径")
    parser.add_argument("--output", default="test_report.md", help="输出报告路径")
    args = parser.parse_args()
    
    # 运行智能体 D
    agent = AgentD_ReportGenerator()
    report = agent.run(
        args.junit_report,
        args.execution_plan,
        args.dimension_analysis,
        args.output
    )
    
    print("\n" + "="*60)
    print("✨ 智能体 D 执行完成: 报告已生成")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
