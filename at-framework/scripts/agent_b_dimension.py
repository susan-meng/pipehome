#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体 B：测试维度分析智能体 (Agent B - Test Dimension Analyzer)

功能：
1. 分析代码变更，确定需要执行的测试维度
2. 输出 dimensions: [functional, contract, boundary, stress, performance]

实现方式：
- 当前：基于规则的简化版
- 未来：接入 LLM 进行深度分析

作者: OpenClaw Assistant
日期: 2026-03-04
"""

import os
import sys
import json
import yaml
from typing import List, Dict, Any, Set


class AgentB_DimensionAnalyzer:
    """测试维度分析智能体"""
    
    # 测试维度定义
    DIMENSIONS = {
        "functional": {
            "name": "功能测试",
            "description": "API 基本功能和业务场景测试",
            "keywords": ["api", "controller", "service", "business", "logic"],
            "default": True  # 总是执行
        },
        "contract": {
            "name": "契约测试",
            "description": "接口结构、字段、响应格式验证",
            "keywords": ["dto", "model", "entity", "vo", "schema", "response", "json", "field"],
            "file_patterns": ["*DTO.java", "*Model.java", "*Entity.java", "*VO.java"]
        },
        "boundary": {
            "name": "边界测试",
            "description": "参数边界、长度、枚举、临界值测试",
            "keywords": ["validator", "validation", "constraint", "length", "size", "min", "max", "range", "limit"],
            "file_patterns": ["*Validator.java", "*Validation.java"]
        },
        "stress": {
            "name": "压力测试",
            "description": "并发、限流、熔断、高负载测试",
            "keywords": ["concurrent", "async", "thread", "pool", "rate", "limiter", "circuit", "breaker", "load", "stress"]
        },
        "performance": {
            "name": "性能测试",
            "description": "响应时间、吞吐量、资源占用测试",
            "keywords": ["performance", "cache", "redis", "memory", "cpu", "time", "timeout", "batch", "optimize"],
            "file_patterns": ["*Cache*.java", "*Performance*.java"]
        }
    }
    
    def __init__(self, mapping_path: str = None):
        self.mapping_path = mapping_path
        self.test_type_tags = {}
        
        if mapping_path and os.path.exists(mapping_path):
            with open(mapping_path, "r", encoding="utf-8") as f:
                mapping = yaml.safe_load(f)
                self.test_type_tags = mapping.get("test_type_tags", {})
    
    def analyze_dimensions(self, listener_output: Dict) -> Dict[str, Any]:
        """
        分析变更，确定测试维度
        
        返回:
        {
            "dimensions": ["functional", "contract", ...],
            "reason": "分析原因摘要",
            "dimension_details": {
                "functional": {"confidence": 1.0, "reason": "..."},
                "contract": {"confidence": 0.8, "reason": "..."},
                ...
            }
        }
        """
        changed_files = listener_output.get("changed_files", [])
        commit_message = listener_output.get("commit_message", "")
        
        detected_dimensions = set()
        dimension_details = {}
        reasons = []
        
        # 1. 功能测试 - 总是包含
        detected_dimensions.add("functional")
        dimension_details["functional"] = {
            "confidence": 1.0,
            "reason": "默认执行功能测试"
        }
        
        # 2. 分析每个变更文件
        for file_info in changed_files:
            path = file_info.get("path", "")
            status = file_info.get("status", "modified")
            
            for dim_id, dim_config in self.DIMENSIONS.items():
                if dim_id == "functional":
                    continue  # 已默认添加
                
                # 检查是否匹配该维度
                is_match, match_reason = self._check_dimension_match(path, commit_message, dim_config)
                
                if is_match:
                    detected_dimensions.add(dim_id)
                    dimension_details[dim_id] = {
                        "confidence": 0.8,
                        "reason": match_reason
                    }
                    reasons.append(f"{dim_config['name']}: {match_reason}")
        
        # 3. 分析 commit message
        msg_dimensions = self._analyze_commit_message(commit_message)
        for dim in msg_dimensions:
            if dim not in detected_dimensions:
                detected_dimensions.add(dim)
                dimension_details[dim] = {
                    "confidence": 0.7,
                    "reason": "从提交信息推断"
                }
        
        # 4. 构建输出
        dimensions_list = sorted(list(detected_dimensions), 
                                key=lambda x: self._get_dimension_priority(x))
        
        return {
            "dimensions": dimensions_list,
            "reason": "; ".join(reasons) if reasons else "基于代码变更类型分析",
            "dimension_details": dimension_details,
            "test_type_tags": self._get_tags_for_dimensions(dimensions_list)
        }
    
    def _check_dimension_match(self, file_path: str, commit_msg: str, dim_config: Dict) -> tuple:
        """检查文件是否匹配某个维度"""
        path_lower = file_path.lower()
        msg_lower = commit_msg.lower()
        
        # 检查关键词
        for keyword in dim_config.get("keywords", []):
            if keyword.lower() in path_lower:
                return True, f"文件路径包含关键词 '{keyword}'"
            if keyword.lower() in msg_lower:
                return True, f"提交信息包含关键词 '{keyword}'"
        
        # 检查文件模式
        import fnmatch
        for pattern in dim_config.get("file_patterns", []):
            if fnmatch.fnmatch(path_lower, pattern.lower()):
                return True, f"文件匹配模式 '{pattern}'"
        
        return False, ""
    
    def _analyze_commit_message(self, commit_message: str) -> Set[str]:
        """从 commit message 分析维度"""
        msg_lower = commit_message.lower()
        dimensions = set()
        
        # 关键词映射
        keyword_mapping = {
            "performance": ["perf", "性能", "optimize", "优化", "cache", "缓存"],
            "boundary": ["boundary", "边界", "validate", "校验", "limit", "限制"],
            "contract": ["contract", "契约", "schema", "dto", "field", "字段"],
            "stress": ["stress", "压力", "concurrent", "并发", "async", "异步"]
        }
        
        for dim, keywords in keyword_mapping.items():
            for keyword in keywords:
                if keyword in msg_lower:
                    dimensions.add(dim)
                    break
        
        return dimensions
    
    def _get_dimension_priority(self, dim_id: str) -> int:
        """获取维度优先级（用于排序）"""
        priorities = {
            "functional": 1,
            "contract": 2,
            "boundary": 3,
            "stress": 4,
            "performance": 5
        }
        return priorities.get(dim_id, 99)
    
    def _get_tags_for_dimensions(self, dimensions: List[str]) -> Dict[str, List[str]]:
        """根据维度获取对应的 tags"""
        result = {}
        for dim in dimensions:
            tags = self.test_type_tags.get(dim, [])
            if tags:
                result[dim] = tags
        return result
    
    def run(self, listener_output_path: str, output_path: str):
        """运行智能体 B"""
        print("="*60)
        print("🤖 智能体 B: 测试维度分析智能体")
        print("="*60)
        
        # 1. 加载 listener 输出
        with open(listener_output_path, "r", encoding="utf-8") as f:
            listener_output = json.load(f)
        
        # 2. 分析维度
        print("\n📊 分析测试维度...")
        result = self.analyze_dimensions(listener_output)
        
        # 3. 输出结果
        print(f"\n🎯 识别的测试维度:")
        for dim in result["dimensions"]:
            dim_config = self.DIMENSIONS.get(dim, {})
            print(f"  - {dim_config.get('name', dim)} ({dim})")
        
        print(f"\n💡 分析原因: {result['reason']}")
        
        # 4. 保存
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 分析结果已保存到: {output_path}")
        
        return result


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="Agent B: 测试维度分析智能体")
    parser.add_argument("--listener-output", required=True, help="listener_output.json 路径")
    parser.add_argument("--mapping", default="testcase/vega/_config/path_scope_mapping.yaml",
                       help="path_scope_mapping.yaml 路径")
    parser.add_argument("--output", default="dimension_analysis.json", help="输出文件路径")
    args = parser.parse_args()
    
    # 运行智能体 B
    agent = AgentB_DimensionAnalyzer(args.mapping)
    result = agent.run(args.listener_output, args.output)
    
    print("\n" + "="*60)
    print(f"✨ 智能体 B 执行完成: 识别了 {len(result['dimensions'])} 个测试维度")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
