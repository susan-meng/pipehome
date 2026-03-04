# Dify 智能体 A 打通生产环境指南

## 一、当前状态

✅ **已完成**：
- Dify 智能体 A 配置完成
- Mock 调试通过，能够正确输出 JSON 格式的用例变更

🎯 **下一步**：
- 获取 Dify Agent API 信息
- 创建调用脚本
- 集成到 CI/CD 流程
- 处理智能体输出并写回文件

---

## 二、获取 Dify Agent API 信息

### 步骤 1：获取 API Key

1. 在 Dify 中，进入智能体配置页面
2. 点击右上角 "访问 API" 或 "API" 标签
3. 复制以下信息：
   - **API Key**：用于身份验证
   - **API Endpoint**：API 调用地址
   - **Agent ID**：智能体的唯一标识

### 步骤 2：测试 API 调用

在 Dify 的 "访问 API" 页面，通常会有：
- **cURL 示例**
- **Python 示例**
- **JavaScript 示例**

复制这些示例，用于后续集成。

---

## 三、创建调用脚本

### 方案 1：Python 脚本（推荐）

创建 `scripts/call_dify_agent_a.py`：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调用 Dify 智能体 A 进行用例维护
"""
import os
import sys
import json
import requests
from pathlib import Path

# Dify Agent A 配置
DIFY_API_KEY = os.getenv("DIFY_AGENT_A_API_KEY", "")
DIFY_API_ENDPOINT = os.getenv("DIFY_AGENT_A_ENDPOINT", "")
DIFY_AGENT_ID = os.getenv("DIFY_AGENT_A_ID", "")

def call_dify_agent_a(listener_output, base_dir, commit_sha=None, existing_suites=None):
    """
    调用 Dify 智能体 A
    
    Args:
        listener_output: 提交监听服务的输出（JSON 格式）
        base_dir: 测试模块的基础目录
        commit_sha: 提交 SHA（可选）
        existing_suites: 现有套件内容（可选，用于 Mock）
    
    Returns:
        dict: 智能体返回的 JSON 结果
    """
    if not DIFY_API_KEY or not DIFY_API_ENDPOINT:
        raise ValueError("请设置环境变量: DIFY_AGENT_A_API_KEY, DIFY_AGENT_A_ENDPOINT")
    
    # 构建请求参数
    payload = {
        "inputs": {
            "listener_output": json.dumps(listener_output) if isinstance(listener_output, dict) else listener_output,
            "base_dir": base_dir,
        }
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
    
    # 调用 API
    response = requests.post(
        f"{DIFY_API_ENDPOINT}/v1/chat-messages",
        headers=headers,
        json=payload,
        timeout=300  # 5 分钟超时
    )
    
    response.raise_for_status()
    result = response.json()
    
    # 提取智能体的输出（通常是 answer 字段）
    answer = result.get("answer", "")
    
    # 尝试解析 JSON
    try:
        # 智能体可能返回 Markdown 代码块，需要提取 JSON
        if "```json" in answer:
            json_start = answer.find("```json") + 7
            json_end = answer.find("```", json_start)
            answer = answer[json_start:json_end].strip()
        elif "```" in answer:
            json_start = answer.find("```") + 3
            json_end = answer.find("```", json_start)
            answer = answer[json_start:json_end].strip()
        
        return json.loads(answer)
    except json.JSONDecodeError:
        # 如果解析失败，返回原始答案
        print(f"⚠️  警告：无法解析 JSON，返回原始答案：\n{answer}")
        return {"status": "error", "message": answer}

def apply_yaml_changes(yaml_changes, base_dir):
    """
    应用智能体返回的 YAML 变更
    
    Args:
        yaml_changes: 智能体返回的 yaml_changes 字典
        base_dir: 测试模块的基础目录
    """
    for file_path, changes in yaml_changes.items():
        # 读取现有文件
        if not os.path.exists(file_path):
            print(f"⚠️  警告：文件不存在，将创建：{file_path}")
            # 创建目录
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # 创建新文件（需要根据 suite_schema 生成基础结构）
            # 这里简化处理，实际应该读取 suite_schema
            content = {
                "feature": "接口参数校验",
                "story": os.path.basename(file_path).replace(".yaml", ""),
                "switch": "y",
                "tags": ["regression"],
                "cases": []
            }
        else:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) or {}
        
        # 应用变更
        if "added_cases" in changes:
            if "cases" not in content:
                content["cases"] = []
            content["cases"].extend(changes["added_cases"])
        
        if "modified_cases" in changes:
            # 根据 name 找到并更新用例
            for modified_case in changes["modified_cases"]:
                case_name = modified_case.get("name")
                for i, case in enumerate(content.get("cases", [])):
                    if case.get("name") == case_name:
                        content["cases"][i].update(modified_case)
                        break
        
        if "deleted_cases" in changes:
            deleted_names = {case.get("name") for case in changes["deleted_cases"]}
            content["cases"] = [
                case for case in content.get("cases", [])
                if case.get("name") not in deleted_names
            ]
        
        # 写回文件
        import yaml
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"✅ 已更新：{file_path}")

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python call_dify_agent_a.py <listener_output.json> <base_dir> [commit_sha]")
        sys.exit(1)
    
    # 读取 listener_output
    listener_output_path = sys.argv[1]
    with open(listener_output_path, 'r', encoding='utf-8') as f:
        listener_output = json.load(f)
    
    base_dir = sys.argv[2]
    commit_sha = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 调用智能体
    print("🔄 调用 Dify 智能体 A...")
    result = call_dify_agent_a(listener_output, base_dir, commit_sha)
    
    # 输出结果
    print("\n📊 智能体返回结果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 应用变更
    if result.get("status") == "success" and "yaml_changes" in result:
        print("\n📝 应用 YAML 变更...")
        apply_yaml_changes(result["yaml_changes"], base_dir)
        print("✅ 完成！")
    else:
        print(f"\n⚠️  状态：{result.get('status')}，跳过文件更新")

if __name__ == "__main__":
    main()
```

### 方案 2：使用 Dify SDK（如果可用）

如果 Dify 提供了 Python SDK，可以使用 SDK 简化调用：

```python
from dify_client import DifyClient

client = DifyClient(api_key=DIFY_API_KEY, base_url=DIFY_API_ENDPOINT)
result = client.chat_messages.create(
    inputs={
        "listener_output": json.dumps(listener_output),
        "base_dir": base_dir,
    }
)
```

---

## 四、集成到 CI/CD

### GitHub Actions 示例

创建 `.github/workflows/test-case-maintenance.yml`：

```yaml
name: Test Case Maintenance

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  collect-changes:
    runs-on: ubuntu-latest
    outputs:
      listener_output: ${{ steps.collect.outputs.listener_output }}
      need_add_cases: ${{ steps.collect.outputs.need_add_cases }}
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 2
      
      - name: Collect Changes
        id: collect
        run: |
          # 这里调用提交监听服务
          # 输出 listener_output.json
          python scripts/commit_listener.py > listener_output.json
          
          # 提取 need_add_cases
          NEED_ADD_CASES=$(jq -r '.need_add_cases' listener_output.json)
          echo "need_add_cases=$NEED_ADD_CASES" >> $GITHUB_OUTPUT
      
      - name: Upload Artifact
        uses: actions/upload-artifact@v3
        with:
          name: listener-output
          path: listener_output.json

  agent-a:
    needs: collect-changes
    if: needs.collect-changes.outputs.need_add_cases == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download Artifact
        uses: actions/download-artifact@v3
        with:
          name: listener-output
      
      - name: Call Dify Agent A
        env:
          DIFY_AGENT_A_API_KEY: ${{ secrets.DIFY_AGENT_A_API_KEY }}
          DIFY_AGENT_A_ENDPOINT: ${{ secrets.DIFY_AGENT_A_ENDPOINT }}
          DIFY_AGENT_A_ID: ${{ secrets.DIFY_AGENT_A_ID }}
        run: |
          python scripts/call_dify_agent_a.py \
            listener_output.json \
            testcase/vega \
            ${{ github.sha }}
      
      - name: Create Pull Request
        if: success()
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "chore: auto-update test cases by Agent A"
          title: "Auto-update test cases"
          body: |
            This PR was automatically created by Dify Agent A.
            
            Changes:
            - See commit message for details
          branch: auto-update-test-cases
```

### GitLab CI 示例

创建 `.gitlab-ci.yml`：

```yaml
stages:
  - collect
  - agent-a
  - test

collect-changes:
  stage: collect
  script:
    - python scripts/commit_listener.py > listener_output.json
  artifacts:
    paths:
      - listener_output.json
    expire_in: 1 hour

agent-a:
  stage: agent-a
  dependencies:
    - collect-changes
  only:
    variables:
      - $NEED_ADD_CASES == "true"
  script:
    - |
      python scripts/call_dify_agent_a.py \
        listener_output.json \
        testcase/vega \
        $CI_COMMIT_SHA
  artifacts:
    paths:
      - testcase/vega/suites/*.yaml
    expire_in: 1 day
```

---

## 五、环境变量配置

### 本地开发

创建 `.env` 文件：

```bash
DIFY_AGENT_A_API_KEY=your_api_key_here
DIFY_AGENT_A_ENDPOINT=https://api.dify.ai/v1
DIFY_AGENT_A_ID=your_agent_id_here
```

### CI/CD 环境

在 GitHub/GitLab 的 Secrets 中配置：
- `DIFY_AGENT_A_API_KEY`
- `DIFY_AGENT_A_ENDPOINT`
- `DIFY_AGENT_A_ID`

---

## 六、处理智能体输出

### 6.1 解析 JSON 输出

智能体返回的 JSON 格式：

```json
{
  "status": "success",
  "action": "add",
  "modified_files": ["testcase/vega/suites/测试数据源.yaml"],
  "cases_added": 1,
  "cases_modified": 0,
  "cases_deleted": 0,
  "summary": "新增 1 个用例",
  "yaml_changes": {
    "testcase/vega/suites/测试数据源.yaml": {
      "added_cases": [...],
      "modified_cases": [...],
      "deleted_cases": [...]
    }
  }
}
```

### 6.2 应用变更到文件

使用 `apply_yaml_changes` 函数（见上面的脚本）将变更应用到实际的 YAML 文件。

### 6.3 验证变更

在应用变更后，应该：
1. 验证 YAML 格式正确性
2. 验证用例是否符合 `case_schema.yaml`
3. 验证 API 名称是否在 `apis.yaml` 中存在
4. 运行基本的语法检查

---

## 七、测试流程

### 7.1 本地测试

```bash
# 1. 准备测试数据
echo '{
  "scope_tags": ["regression"],
  "suggested_suites": ["测试数据源"],
  "affected_api_names": ["测试数据源连接"],
  "affected_api_paths": ["/api/data-connection/v1/datasource/test"],
  "need_add_cases": true,
  "diffs": []
}' > test_listener_output.json

# 2. 调用智能体
export DIFY_AGENT_A_API_KEY="your_key"
export DIFY_AGENT_A_ENDPOINT="https://api.dify.ai/v1"
python scripts/call_dify_agent_a.py test_listener_output.json testcase/vega

# 3. 检查输出
git diff testcase/vega/suites/
```

### 7.2 CI/CD 测试

1. 创建一个测试分支
2. 提交一个测试变更
3. 触发 CI/CD 流程
4. 检查智能体是否被正确调用
5. 检查生成的 PR 或提交

---

## 八、常见问题

### Q1: API 调用失败？

**A:** 
1. 检查 API Key 是否正确
2. 检查 API Endpoint 是否正确
3. 检查网络连接
4. 查看 Dify 的 API 文档，确认调用格式

### Q2: 智能体返回的 JSON 格式不正确？

**A:**
1. 检查 Prompt 中是否明确要求输出 JSON
2. 在 Prompt 中添加 JSON Schema 示例
3. 在脚本中添加 JSON 解析的容错处理

### Q3: 文件更新失败？

**A:**
1. 检查文件路径是否正确
2. 检查文件权限
3. 检查 YAML 格式是否正确
4. 验证用例是否符合规范

---

## 九、下一步

1. ✅ **获取 API 信息**：在 Dify 中获取 API Key 和 Endpoint
2. ✅ **创建调用脚本**：使用上面的 Python 脚本模板
3. ✅ **本地测试**：使用测试数据验证脚本功能
4. ✅ **集成 CI/CD**：将脚本集成到 GitHub Actions 或 GitLab CI
5. ✅ **监控和优化**：监控智能体的调用情况，优化 Prompt 和参数

---

## 十、参考文档

- [Dify 智能体 A 配置指南](./Dify智能体A配置指南.md)
- [Dify 智能体 A 最小测试参数](./Dify智能体A_最小测试参数.md)
- [测试架构设计_基于Commit与多智能体](./测试架构设计_基于Commit与多智能体.md)
