#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提交监听脚本 - Stage 2
功能：
1. 分析 git diff 获取变更文件
2. 根据 path_scope_mapping.yaml 匹配 scope 和 suggested_suites
3. 提取 affected_api_names（基于变更路径推断）
4. 生成 listener_output.json 供下游使用

作者: OpenClaw Assistant
日期: 2026-03-04
"""

import os
import sys
import json
import yaml
import fnmatch
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path


def run_git_command(cmd: List[str], cwd: str = None) -> str:
    """运行 git 命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return ""


def get_changed_files(repo_path: str, base_ref: str = "HEAD^", head_ref: str = "HEAD") -> List[Dict[str, str]]:
    """
    获取变更文件列表
    返回: [{"path": "...", "status": "added|modified|removed"}, ...]
    """
    # 使用 git diff --name-status 获取变更文件和状态
    output = run_git_command(
        ["git", "diff", "--name-status", base_ref, head_ref],
        cwd=repo_path
    )
    
    changed_files = []
    status_map = {
        "A": "added",
        "M": "modified",
        "D": "removed",
        "R": "modified",  # 重命名视为修改
        "C": "added",     # 复制视为新增
    }
    
    for line in output.split("\n"):
        if not line.strip():
            continue
        
        parts = line.split("\t")
        if len(parts) >= 2:
            status_code = parts[0][0]  # 取第一个字符（忽略分数如 R100）
            file_path = parts[-1]      # 最后一个元素是文件路径
            
            status = status_map.get(status_code, "modified")
            changed_files.append({
                "path": file_path,
                "status": status
            })
    
    return changed_files


def load_path_scope_mapping(mapping_path: str) -> Dict[str, Any]:
    """加载 path_scope_mapping.yaml"""
    try:
        with open(mapping_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Failed to load path_scope_mapping: {e}")
        return {"subsystems": []}


def match_path_to_scope(file_path: str, subsystems: List[Dict]) -> List[str]:
    """
    将文件路径匹配到 scope
    返回匹配的 subsystem ids 列表
    """
    matched_scopes = []
    
    for subsystem in subsystems:
        path_patterns = subsystem.get("path_patterns", [])
        
        # 空 path_patterns 表示仅作 scope 使用（如 performance）
        if not path_patterns:
            continue
        
        for pattern in path_patterns:
            # 使用 fnmatch 进行 glob 匹配
            if fnmatch.fnmatch(file_path, pattern):
                matched_scopes.append(subsystem["id"])
                break
    
    return matched_scopes


def infer_affected_apis(file_path: str, apis: List[Dict]) -> List[str]:
    """
    根据变更路径推断受影响的 API
    简化版：基于文件名关键词匹配
    """
    affected_apis = []
    path_lower = file_path.lower()
    
    # 关键词映射表（可以根据实际情况扩展）
    keyword_mapping = {
        "datasource": ["新增数据源", "更新数据源", "删除数据源", "查询数据源列表", 
                      "查询数据源详情", "测试数据源连接", "获取数据源列表"],
        "metadata": ["元数据扫描", "元数据批量扫描", "查询扫描任务列表"],
        "connector": ["查询所有支持数据源"],
    }
    
    for keyword, api_names in keyword_mapping.items():
        if keyword in path_lower:
            affected_apis.extend(api_names)
    
    # 去重
    return list(set(affected_apis))


def analyze_changes(
    changed_files: List[Dict[str, str]],
    mapping: Dict[str, Any],
    apis: List[Dict] = None
) -> Dict[str, Any]:
    """
    分析变更，生成 listener_output
    """
    subsystems = mapping.get("subsystems", [])
    
    # 收集匹配的 scopes 和相关信息
    all_scopes = set()
    all_scope_tags = set()
    all_suggested_suites = []
    all_affected_apis = []
    
    for file_info in changed_files:
        path = file_info["path"]
        
        # 匹配 scope
        scopes = match_path_to_scope(path, subsystems)
        all_scopes.update(scopes)
        
        # 收集 scope 相关信息
        for scope_id in scopes:
            for subsystem in subsystems:
                if subsystem["id"] == scope_id:
                    all_scope_tags.update(subsystem.get("scope_tags", []))
                    all_suggested_suites.extend(subsystem.get("suggested_suites", []))
                    break
        
        # 推断受影响的 API
        if apis:
            apis_found = infer_affected_apis(path, apis)
            all_affected_apis.extend(apis_found)
    
    # 判断是否需要新增用例
    # 规则：存在 added 文件且命中 scope
    has_added = any(f["status"] == "added" for f in changed_files)
    need_add_cases = has_added and len(all_scopes) > 0
    
    # 去重 suggested_suites
    all_suggested_suites = list(dict.fromkeys(all_suggested_suites))
    all_affected_apis = list(dict.fromkeys(all_affected_apis))
    
    # 生成输出
    output = {
        "repo": os.environ.get("GITHUB_REPOSITORY", "unknown/repo"),
        "branch": os.environ.get("GITHUB_REF_NAME", "unknown"),
        "commit_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "commit_message": get_commit_message(),
        "changed_files": changed_files,
        "change_summary": {
            "added": [f["path"] for f in changed_files if f["status"] == "added"],
            "modified": [f["path"] for f in changed_files if f["status"] == "modified"],
            "removed": [f["path"] for f in changed_files if f["status"] == "removed"],
        },
        "scopes": list(all_scopes),
        "scope_tags": list(all_scope_tags),
        "suggested_suites": all_suggested_suites,
        "affected_api_names": all_affected_apis,
        "affected_api_paths": [],  # 简化版暂不填充
        "need_add_cases": need_add_cases,
    }
    
    return output


def get_commit_message() -> str:
    """获取提交信息"""
    # 优先从环境变量获取（GitHub Actions）
    if "GITHUB_EVENT_HEAD_COMMIT_MESSAGE" in os.environ:
        return os.environ["GITHUB_EVENT_HEAD_COMMIT_MESSAGE"]
    
    # 本地获取
    msg = run_git_command(["git", "log", "-1", "--pretty=%B"])
    return msg or "No commit message"


def save_output(output: Dict[str, Any], output_path: str):
    """保存输出到 JSON 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Output saved to: {output_path}")


def print_summary(output: Dict[str, Any]):
    """打印分析摘要"""
    print("\n" + "="*60)
    print("📊 提交监听分析结果")
    print("="*60)
    print(f"仓库: {output['repo']}")
    print(f"分支: {output['branch']}")
    print(f"Commit: {output['commit_sha'][:8]}")
    print(f"\n提交信息: {output['commit_message'][:80]}...")
    
    print(f"\n📁 变更文件 ({len(output['changed_files'])}):")
    for f in output['changed_files'][:10]:  # 只显示前10个
        status_emoji = {"added": "➕", "modified": "📝", "removed": "🗑️"}
        emoji = status_emoji.get(f['status'], "❓")
        print(f"  {emoji} {f['path']} ({f['status']})")
    if len(output['changed_files']) > 10:
        print(f"  ... 还有 {len(output['changed_files']) - 10} 个文件")
    
    print(f"\n🎯 匹配到的 Scopes: {output['scopes']}")
    print(f"🏷️  Tags: {output['scope_tags']}")
    print(f"📋 建议的 Suites: {output['suggested_suites'][:5]}...")
    print(f"🔗 受影响的 APIs: {output['affected_api_names'][:5]}...")
    print(f"\n❓ 需要新增用例: {'是' if output['need_add_cases'] else '否'}")
    print("="*60)


def main():
    """主函数"""
    # 参数解析
    import argparse
    parser = argparse.ArgumentParser(description="提交监听脚本 - 分析变更并输出测试范围")
    parser.add_argument("--repo-path", default=".", help="代码仓库路径")
    parser.add_argument("--mapping", default="testcase/vega/_config/path_scope_mapping.yaml",
                       help="path_scope_mapping.yaml 路径")
    parser.add_argument("--apis", default="testcase/vega/_config/apis.yaml",
                       help="apis.yaml 路径")
    parser.add_argument("--base-ref", default="HEAD^", help="对比的基准 commit")
    parser.add_argument("--head-ref", default="HEAD", help="当前 commit")
    parser.add_argument("--output", default="listener_output.json", help="输出文件路径")
    args = parser.parse_args()
    
    print("🔍 开始分析提交变更...")
    
    # 1. 获取变更文件
    print(f"\n1️⃣ 获取变更文件 ({args.base_ref}...{args.head_ref})")
    changed_files = get_changed_files(args.repo_path, args.base_ref, args.head_ref)
    
    if not changed_files:
        print("⚠️ 未检测到变更文件")
        # 生成空输出
        output = {
            "repo": os.environ.get("GITHUB_REPOSITORY", "unknown/repo"),
            "branch": os.environ.get("GITHUB_REF_NAME", "unknown"),
            "commit_sha": os.environ.get("GITHUB_SHA", "unknown"),
            "commit_message": get_commit_message(),
            "changed_files": [],
            "change_summary": {"added": [], "modified": [], "removed": []},
            "scopes": [],
            "scope_tags": [],
            "suggested_suites": [],
            "affected_api_names": [],
            "affected_api_paths": [],
            "need_add_cases": False,
        }
    else:
        print(f"   发现 {len(changed_files)} 个变更文件")
        
        # 2. 加载配置
        print("\n2️⃣ 加载 path_scope_mapping")
        mapping_path = os.path.join(args.repo_path, args.mapping)
        mapping = load_path_scope_mapping(mapping_path)
        print(f"   加载了 {len(mapping.get('subsystems', []))} 个子系统")
        
        # 3. 加载 APIs（可选）
        apis = []
        apis_path = os.path.join(args.repo_path, args.apis)
        if os.path.exists(apis_path):
            print("\n3️⃣ 加载 APIs 配置")
            try:
                with open(apis_path, "r", encoding="utf-8") as f:
                    apis = yaml.safe_load(f) or []
                print(f"   加载了 {len(apis)} 个 API")
            except Exception as e:
                print(f"   警告: 无法加载 APIs: {e}")
        
        # 4. 分析变更
        print("\n4️⃣ 分析变更范围")
        output = analyze_changes(changed_files, mapping, apis)
    
    # 5. 保存输出
    output_path = os.path.join(args.repo_path, args.output)
    save_output(output, output_path)
    
    # 6. 打印摘要
    print_summary(output)
    
    # 7. 输出到 GitHub Actions（如果运行在 Actions 中）
    if "GITHUB_OUTPUT" in os.environ:
        github_output = os.environ["GITHUB_OUTPUT"]
        with open(github_output, "a") as f:
            f.write(f"scopes={','.join(output['scopes'])}\n")
            f.write(f"need_cases={'true' if output['need_add_cases'] else 'false'}\n")
            f.write(f"affected_apis={','.join(output['affected_api_names'])}\n")
            f.write(f"case_filter_mode={'api' if output['affected_api_names'] else 'scope'}\n")
        print(f"\n✅ GitHub Actions 输出已写入")
    
    print("\n✨ 分析完成!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
