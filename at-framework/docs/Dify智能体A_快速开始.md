# Dify 智能体 A 快速开始

## 一、前提条件

✅ **已完成**：
- Dify 智能体 A 配置完成
- Mock 调试通过
- 知识库已导入规范文件

---

## 二、获取 API 信息

### 步骤 1：在 Dify 中获取 API Key

1. 进入智能体配置页面
2. 点击 "访问 API" 标签
3. 复制以下信息：
   - **API Key**
   - **API Endpoint**（通常是 `https://api.dify.ai/v1` 或你的 Dify 实例地址）
   - **Agent ID**（如果有）

### 步骤 2：设置环境变量

```bash
# Linux/Mac
export DIFY_AGENT_A_API_KEY="your_api_key_here"
export DIFY_AGENT_A_ENDPOINT="https://api.dify.ai/v1"
export DIFY_AGENT_A_ID="your_agent_id_here"  # 可选

# Windows PowerShell
$env:DIFY_AGENT_A_API_KEY="your_api_key_here"
$env:DIFY_AGENT_A_ENDPOINT="https://api.dify.ai/v1"
$env:DIFY_AGENT_A_ID="your_agent_id_here"  # 可选
```

---

## 三、本地测试

### 步骤 1：准备测试数据

创建 `test_listener_output.json`：

```json
{
  "scope_tags": ["regression"],
  "suggested_suites": ["测试数据源"],
  "affected_api_names": ["测试数据源连接"],
  "affected_api_paths": ["/api/data-connection/v1/datasource/test"],
  "need_add_cases": true,
  "diffs": []
}
```

### 步骤 2：调用智能体

```bash
python scripts/call_dify_agent_a.py test_listener_output.json testcase/vega
```

### 步骤 3：检查结果

```bash
# 查看变更
git diff testcase/vega/suites/

# 查看智能体输出
cat agent_output.json  # 如果有保存的话
```

---

## 四、集成到 CI/CD

### GitHub Actions

在 `.github/workflows/test-case-maintenance.yml` 中添加：

```yaml
jobs:
  agent-a:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Call Dify Agent A
        env:
          DIFY_AGENT_A_API_KEY: ${{ secrets.DIFY_AGENT_A_API_KEY }}
          DIFY_AGENT_A_ENDPOINT: ${{ secrets.DIFY_AGENT_A_ENDPOINT }}
        run: |
          python scripts/call_dify_agent_a.py \
            listener_output.json \
            testcase/vega \
            ${{ github.sha }}
```

### GitLab CI

在 `.gitlab-ci.yml` 中添加：

```yaml
agent-a:
  script:
    - |
      python scripts/call_dify_agent_a.py \
        listener_output.json \
        testcase/vega \
        $CI_COMMIT_SHA
  variables:
    DIFY_AGENT_A_API_KEY: $DIFY_AGENT_A_API_KEY
    DIFY_AGENT_A_ENDPOINT: $DIFY_AGENT_A_ENDPOINT
```

---

## 五、常见问题

### Q1: API 调用失败？

**检查清单**：
1. ✅ API Key 是否正确
2. ✅ API Endpoint 是否正确（注意末尾不要有 `/`）
3. ✅ 网络连接是否正常
4. ✅ 查看 Dify 的 API 文档，确认调用格式

### Q2: 智能体返回格式不正确？

**解决方案**：
1. 检查 Prompt 中是否明确要求输出 JSON
2. 在 Prompt 中添加 JSON Schema 示例
3. 脚本会自动尝试从 Markdown 代码块中提取 JSON

### Q3: 文件更新失败？

**检查清单**：
1. ✅ 文件路径是否正确
2. ✅ 文件权限是否足够
3. ✅ YAML 格式是否正确
4. ✅ 用例是否符合 `case_schema.yaml` 规范

---

## 六、下一步

1. ✅ **本地测试**：使用测试数据验证脚本功能
2. ✅ **集成 CI/CD**：将脚本集成到 GitHub Actions 或 GitLab CI
3. ✅ **监控和优化**：监控智能体的调用情况，优化 Prompt 和参数
4. ✅ **扩展功能**：集成智能体 B、C、D 完成完整流程

---

## 七、参考文档

- [Dify 智能体 A 配置指南](./Dify智能体A配置指南.md)
- [Dify 智能体 A 打通生产环境指南](./Dify智能体A_打通生产环境指南.md)
- [Dify 智能体 A 最小测试参数](./Dify智能体A_最小测试参数.md)
