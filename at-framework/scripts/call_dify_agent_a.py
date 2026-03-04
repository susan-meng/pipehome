#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调用 Dify 智能体 A 进行用例维护

用法:
    python call_dify_agent_a.py <listener_output.json> <base_dir> [commit_sha]

环境变量:
    DIFY_AGENT_A_API_KEY: Dify API Key
    DIFY_AGENT_A_ENDPOINT: Dify API Endpoint (如 https://api.dify.ai/v1)
    DIFY_AGENT_A_ID: Dify Agent ID (可选)
"""
import os
import sys
import json
import re
import yaml
import requests
from pathlib import Path

# Dify Agent A 配置
DIFY_API_KEY = os.getenv("DIFY_AGENT_A_API_KEY", "")
DIFY_API_ENDPOINT = os.getenv("DIFY_AGENT_A_ENDPOINT", "")
DIFY_AGENT_ID = os.getenv("DIFY_AGENT_A_ID", "")


def extract_json_from_answer(answer):
    """
    从智能体的回答中提取 JSON
    
    Args:
        answer: 智能体返回的原始答案
    
    Returns:
        dict: 解析后的 JSON 对象
    """
    # 尝试直接解析
    try:
        return json.loads(answer)
    except json.JSONDecodeError:
        pass
    
    # 尝试提取 Markdown 代码块中的 JSON
    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'\{.*\}',  # 直接匹配 JSON 对象
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, answer, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # 如果都失败，返回错误
    raise ValueError(f"无法从答案中提取 JSON: {answer[:200]}")


def call_dify_agent_a(listener_output, base_dir, commit_sha=None, existing_suites=None):
    """
    调用 Dify 智能体 A
    
    Args:
        listener_output: 提交监听服务的输出（JSON 格式或字典）
        base_dir: 测试模块的基础目录
        commit_sha: 提交 SHA（可选）
        existing_suites: 现有套件内容（可选，用于 Mock）
    
    Returns:
        dict: 智能体返回的 JSON 结果
    """
    if not DIFY_API_KEY or not DIFY_API_ENDPOINT:
        raise ValueError(
            "请设置环境变量: DIFY_AGENT_A_API_KEY, DIFY_AGENT_A_ENDPOINT\n"
            "示例:\n"
            "  export DIFY_AGENT_A_API_KEY='your_api_key'\n"
            "  export DIFY_AGENT_A_ENDPOINT='https://api.dify.ai/v1'"
        )
    
    # 构建请求参数
    if isinstance(listener_output, dict):
        listener_output_str = json.dumps(listener_output, ensure_ascii=False)
    else:
        listener_output_str = listener_output
    
    payload = {
        "inputs": {
            "listener_output": listener_output_str,
            "base_dir": base_dir,
        },
        "query": "请根据输入信息维护测试用例",  # 触发智能体的提示
        "response_mode": "blocking",  # 阻塞模式，等待完整响应
        "user": "ci-system",  # 用户标识
    }
    
    if commit_sha:
        payload["inputs"]["commit_sha"] = commit_sha
    
    if existing_suites:
        payload["inputs"]["existing_suites"] = existing_suites
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构建 API URL
    # Dify API 格式通常是: {endpoint}/chat-messages 或 {endpoint}/agents/{agent_id}/chat
    if DIFY_AGENT_ID:
        api_url = f"{DIFY_API_ENDPOINT}/agents/{DIFY_AGENT_ID}/chat"
    else:
        # 如果没有 agent_id，使用通用的 chat-messages endpoint
        api_url = f"{DIFY_API_ENDPOINT}/chat-messages"
    
    print(f"🔄 调用 Dify API: {api_url}")
    print(f"📝 输入参数:")
    print(f"  - base_dir: {base_dir}")
    print(f"  - commit_sha: {commit_sha or 'N/A'}")
    print(f"  - listener_output keys: {list(listener_output.keys()) if isinstance(listener_output, dict) else 'N/A'}")
    
    # 调用 API
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=300  # 5 分钟超时
        )
        response.raise_for_status()
        result = response.json()
        
        # 提取智能体的输出
        answer = result.get("answer", "") or result.get("message", "") or result.get("data", {}).get("answer", "")
        
        if not answer:
            print(f"⚠️  警告：API 返回结果中没有找到答案字段")
            print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return {"status": "error", "message": "API 返回格式异常", "raw_response": result}
        
        # 解析 JSON
        try:
            return extract_json_from_answer(answer)
        except ValueError as e:
            print(f"⚠️  警告：{e}")
            print(f"原始答案:\n{answer}")
            return {"status": "error", "message": str(e), "raw_answer": answer}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API 调用失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
        raise


def apply_yaml_changes(yaml_changes, base_dir):
    """
    应用智能体返回的 YAML 变更
    
    Args:
        yaml_changes: 智能体返回的 yaml_changes 字典
        base_dir: 测试模块的基础目录
    """
    for file_path, changes in yaml_changes.items():
        # 确保路径是绝对路径
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        
        # 读取现有文件
        if not os.path.exists(file_path):
            print(f"⚠️  警告：文件不存在，将创建：{file_path}")
            # 创建目录
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # 创建新文件（需要根据 suite_schema 生成基础结构）
            # 从文件路径推断 story 名称
            story_name = os.path.basename(file_path).replace(".yaml", "")
            content = {
                "feature": "接口参数校验",
                "story": story_name,
                "switch": "y",
                "tags": ["regression"],
                "cases": []
            }
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) or {}
                if "cases" not in content:
                    content["cases"] = []
        
        # 应用变更
        cases_dict = {case.get("name"): i for i, case in enumerate(content.get("cases", []))}
        
        if "added_cases" in changes:
            for new_case in changes["added_cases"]:
                case_name = new_case.get("name")
                if case_name in cases_dict:
                    print(f"⚠️  警告：用例 '{case_name}' 已存在，将更新")
                    # 更新现有用例
                    content["cases"][cases_dict[case_name]].update(new_case)
                else:
                    # 添加新用例
                    content["cases"].append(new_case)
                    cases_dict[case_name] = len(content["cases"]) - 1
        
        if "modified_cases" in changes:
            for modified_case in changes["modified_cases"]:
                case_name = modified_case.get("name")
                if case_name in cases_dict:
                    # 更新用例
                    content["cases"][cases_dict[case_name]].update(modified_case)
                else:
                    print(f"⚠️  警告：用例 '{case_name}' 不存在，无法修改")
        
        if "deleted_cases" in changes:
            deleted_names = {case.get("name") for case in changes["deleted_cases"]}
            content["cases"] = [
                case for case in content.get("cases", [])
                if case.get("name") not in deleted_names
            ]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"✅ 已更新：{file_path}")


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python call_dify_agent_a.py <listener_output.json> <base_dir> [commit_sha]")
        print("\n环境变量:")
        print("  DIFY_AGENT_A_API_KEY: Dify API Key")
        print("  DIFY_AGENT_A_ENDPOINT: Dify API Endpoint")
        print("  DIFY_AGENT_A_ID: Dify Agent ID (可选)")
        sys.exit(1)
    
    # 读取 listener_output
    listener_output_path = sys.argv[1]
    if not os.path.exists(listener_output_path):
        print(f"❌ 错误：文件不存在: {listener_output_path}")
        sys.exit(1)
    
    with open(listener_output_path, 'r', encoding='utf-8') as f:
        listener_output = json.load(f)
    
    base_dir = sys.argv[2]
    commit_sha = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 调用智能体
    print("=" * 80)
    print("🚀 开始调用 Dify 智能体 A")
    print("=" * 80)
    
    try:
        result = call_dify_agent_a(listener_output, base_dir, commit_sha)
        
        # 输出结果
        print("\n" + "=" * 80)
        print("📊 智能体返回结果：")
        print("=" * 80)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 应用变更
        if result.get("status") == "success" and "yaml_changes" in result:
            print("\n" + "=" * 80)
            print("📝 应用 YAML 变更...")
            print("=" * 80)
            apply_yaml_changes(result["yaml_changes"], base_dir)
            print("\n✅ 完成！")
        else:
            print(f"\n⚠️  状态：{result.get('status')}，跳过文件更新")
            if result.get("status") == "error":
                sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
