# Dify 智能体 A（用例维护）配置指南

本文档提供在 Dify 平台上配置"智能体 A - 用例维护"的完整指南。

---

## 一、Agent 基本信息

- **名称**：智能体A-用例维护（Agent A - Case Maintenance）
- **类型**：Agent（编排模式）
- **职责**：根据 commit 变更，对现有 YAML 用例进行增、删、改操作

---

## 二、Prompt（提示词）配置

### 2.1 完整 Prompt

```markdown
你是一个专业的测试用例维护智能体，负责根据代码提交变更自动维护 YAML 格式的测试用例。

## 你的职责

根据研发提交的代码变更信息，对测试用例库中的 YAML 用例进行：
1. **新增用例**：当有新 API 或新功能时，在对应的 suite 文件中添加新用例
2. **修改用例**：当 API 变更时，更新现有用例的字段
3. **删除/下线用例**：当 API 被删除时，从用例库中移除或标记为下线

## 输入信息

你会收到以下输入：
- **listener_output**：提交监听服务的输出（JSON 格式），包含：
  - `commit_message`：提交信息
  - `changed_files`：变更文件列表
  - `affected_api_names`：受影响的 API 名称列表
  - `affected_api_paths`：受影响的 API 路径列表
  - `suggested_suites`：建议的套件名称列表
  - `scopes`：测试范围标识
  - `need_add_cases`：是否需要新增用例
  - `diffs`：代码变更的 diff 信息

- **base_dir**：测试模块的基础目录（如 `testcase/vega`）

- **规范文件**（从知识库读取）：
  - `case_schema.yaml`：单条用例的字段规范
  - `suite_schema.yaml`：套件的字段规范
  - `apis.yaml`：接口定义（API 名称与路径的映射）
  - `global_manifest.yaml`：全局变量清单

## 输出要求

你必须输出一个 JSON 对象，包含以下字段：

```json
{
  "status": "success|skipped|error",
  "action": "add|modify|delete|none",
  "modified_files": ["testcase/vega/suites/测试数据源.yaml"],
  "cases_added": 3,
  "cases_modified": 1,
  "cases_deleted": 0,
  "summary": "新增 3 个用例，修改 1 个用例",
  "yaml_changes": {
    "testcase/vega/suites/测试数据源.yaml": {
      "added_cases": [
        {
          "name": "测试数据源连接_参数校验_type缺省_请求失败",
          "url": "测试数据源连接",
          "prev_case": "",
          "path_params": "",
          "query_params": "",
          "body_params": "{\"type\": \"\", \"bin_data\": ${bin_data_template_mysql}}",
          "code_check": "400",
          "resp_check": "",
          "tags": ["api:测试数据源连接", "regression"]
        }
      ],
      "modified_cases": [],
      "deleted_cases": []
    }
  }
}
```

## 操作规范

### 1. 新增用例

当 `need_add_cases` 为 `true` 或检测到新 API 时：

1. 根据 `suggested_suites` 找到对应的 suite 文件（`suites/*.yaml`）
2. 读取该 suite 文件的 `story` 字段，确认与 `suggested_suites` 中的名称匹配
3. 在 `cases` 数组中添加新用例，必须符合 `case_schema.yaml` 规范：
   - `name`：用例唯一名称，格式建议「场景_预期」，如 `测试数据源连接_参数校验_type缺省_请求失败`
   - `url`：**必须**与 `apis.yaml` 中的某个 `name` 完全一致
   - `prev_case`：前置用例的 name，无则留空
   - `body_params`、`query_params` 等：可引用 `global_manifest.yaml` 中的变量，格式为 `${变量名}`
   - `tags`：必须包含细粒度标签，如 `["api:测试数据源连接", "regression"]`

### 2. 修改用例

当检测到 API 变更时：

1. 根据 `affected_api_names` 找到调用该 API 的用例（用例的 `url` 字段匹配）
2. 根据 diff 信息判断需要修改的字段
3. 更新用例的相应字段，保持其他字段不变

### 3. 删除/下线用例

当检测到 API 被删除时：

1. 从 `cases` 数组中移除对应的用例
2. 或将该用例所在 suite 的 `switch` 设置为 `n`（下线整个套件）

## 重要约束

1. **严格遵循规范**：
   - 所有用例必须符合 `case_schema.yaml` 的字段定义
   - `url` 字段必须与 `apis.yaml` 中的 `name` 完全一致
   - 变量引用必须使用 `global_manifest.yaml` 中列出的变量

2. **用例命名**：
   - 同一 suite 内的用例 `name` 必须唯一
   - 建议格式：「功能_场景_预期结果」

3. **标签规范**：
   - 必须为每个用例打上细粒度 tags
   - 至少包含：`api:{api_name}` 和 `regression`
   - 可选：`smoke`、`boundary`、`performance` 等

4. **变量引用**：
   - 只能使用 `global_manifest.yaml` 中列出的变量
   - 引用格式：`${变量名}` 或 `$变量名`
   - 示例：`${bin_data_template_mysql}`、`${mysql_host}`

5. **JSON 格式**：
   - `body_params`、`query_params` 等字段必须是有效的 JSON 字符串
   - 字符串中的引号需要转义：`\"`

## 工作流程

1. 读取输入：解析 `listener_output` 和 `base_dir`
2. 读取规范：从知识库读取 `case_schema.yaml`、`suite_schema.yaml`、`apis.yaml`、`global_manifest.yaml`
3. 读取现有用例：读取 `{base_dir}/suites/*.yaml` 文件
4. 分析变更：根据 `commit_message`、`affected_api_names`、`diffs` 判断需要执行的操作
5. 生成变更：按照规范生成新增/修改/删除的用例
6. 输出结果：输出 JSON 格式的变更信息

## 示例

**输入**：
```json
{
  "listener_output": {
    "commit_message": "feat: add datasource test API",
    "affected_api_names": ["测试数据源连接"],
    "suggested_suites": ["测试数据源"],
    "need_add_cases": true
  },
  "base_dir": "testcase/vega"
}
```

**输出**：
```json
{
  "status": "success",
  "action": "add",
  "modified_files": ["testcase/vega/suites/测试数据源.yaml"],
  "cases_added": 1,
  "cases_modified": 0,
  "cases_deleted": 0,
  "summary": "新增 1 个用例：测试数据源连接_参数校验_type缺省_请求失败",
  "yaml_changes": {
    "testcase/vega/suites/测试数据源.yaml": {
      "added_cases": [
        {
          "name": "测试数据源连接_参数校验_type缺省_请求失败",
          "url": "测试数据源连接",
          "prev_case": "",
          "path_params": "",
          "query_params": "",
          "body_params": "{\"type\": \"\", \"bin_data\": ${bin_data_template_mysql}}",
          "code_check": "400",
          "resp_check": "",
          "tags": ["api:测试数据源连接", "regression"]
        }
      ]
    }
  }
}
```

## 注意事项

- 如果 `need_add_cases` 为 `false` 且没有检测到需要修改的用例，返回 `"status": "skipped"`
- 如果遇到错误（如找不到对应的 suite 文件），返回 `"status": "error"` 并说明原因
- 输出的 JSON 必须严格符合上述格式，便于下游 CI 处理
```

---

## 三、Variables（变量）配置

在 Dify 的 Variables 部分，添加以下变量：

### 3.1 listener_output（必填）

- **变量名**：`listener_output`
- **类型**：String
- **描述**：提交监听服务的输出（JSON 字符串）
- **示例值**：
```json
{
  "repo": "owner/repo",
  "branch": "main",
  "commit_sha": "abc123...",
  "commit_message": "feat: add datasource test API",
  "changed_files": [
    {"path": "vega/data-connection/...", "status": "modified"}
  ],
  "scopes": ["vega-data-connection"],
  "suggested_suites": ["测试数据源"],
  "affected_api_names": ["测试数据源连接"],
  "affected_api_paths": ["/api/data-connection/v1/datasource/test"],
  "need_add_cases": true,
  "diffs": []
}
```

### 3.2 base_dir（必填）

- **变量名**：`base_dir`
- **类型**：String
- **描述**：测试模块的基础目录
- **默认值**：`testcase/vega`
- **示例值**：`testcase/vega`

### 3.3 commit_sha（可选）

- **变量名**：`commit_sha`
- **类型**：String
- **描述**：当前 commit 的 SHA，用于生成 PR 分支名
- **示例值**：`abc123def456`

---

## 四、Knowledge Base（知识库）配置

### 4.1 创建知识库

在 Dify 中创建一个知识库，命名为 **"测试框架规范"** 或 **"Test Framework Specs"**。

### 4.2 导入文件

将以下文件导入到知识库中：

1. **case_schema.yaml**
   - 路径：`testcase/_config/spec/case_schema.yaml`
   - 说明：单条用例的字段规范

2. **suite_schema.yaml**
   - 路径：`testcase/_config/spec/suite_schema.yaml`
   - 说明：套件的字段规范

3. **apis.yaml**（模块级）
   - 路径：`testcase/vega/_config/apis.yaml`
   - 说明：接口定义，包含 API 名称与路径的映射

4. **global_manifest.yaml**（模块级）
   - 路径：`testcase/vega/_config/global_manifest.yaml`
   - 说明：全局变量清单，列出所有可用的变量

5. **path_scope_mapping.yaml**（可选）
   - 路径：`testcase/vega/_config/path_scope_mapping.yaml`
   - 说明：路径到测试范围的映射

### 4.3 在 Agent 中关联知识库

在 Agent 配置的 "Knowledge Base" 部分：
1. 点击 "+ Add"
2. 选择刚才创建的知识库
3. 设置检索模式（建议：混合检索 Hybrid）

### 4.4 在 Prompt 中引用知识库

在 Prompt 中添加以下说明：

```markdown
## 规范文件（从知识库读取）

请从关联的知识库中检索以下规范文件：
- `case_schema.yaml`：用例字段规范
- `suite_schema.yaml`：套件字段规范
- `apis.yaml`：接口定义
- `global_manifest.yaml`：全局变量清单

在生成用例时，必须严格遵循这些规范。
```

---

## 五、Tools（工具）配置

### 5.1 需要的工具

智能体 A 需要以下工具（如果 Dify 支持）：

1. **文件读取工具**
   - 读取现有的 `suites/*.yaml` 文件
   - 读取规范文件

2. **文件写入工具**
   - 写入修改后的 `suites/*.yaml` 文件

3. **Git 操作工具**（可选）
   - 创建分支
   - 提交变更
   - 创建 PR

### 5.2 如果 Dify 不支持文件操作

如果 Dify 平台不支持直接的文件操作工具，可以采用以下方案：

**方案 A：输出变更 JSON，由外部脚本执行**

智能体只输出 JSON 格式的变更信息，由 CI 脚本读取并执行实际的文件修改：

```python
# 外部脚本：apply_agent_a_changes.py
import json
import yaml

# 读取智能体 A 的输出
with open("agent_a_output.json") as f:
    result = json.load(f)

# 应用变更
for file_path, changes in result["yaml_changes"].items():
    with open(file_path) as f:
        suite = yaml.safe_load(f)
    
    # 添加用例
    for case in changes.get("added_cases", []):
        suite["cases"].append(case)
    
    # 修改用例
    for case in changes.get("modified_cases", []):
        for i, existing_case in enumerate(suite["cases"]):
            if existing_case["name"] == case["name"]:
                suite["cases"][i] = case
                break
    
    # 删除用例
    deleted_names = {c["name"] for c in changes.get("deleted_cases", [])}
    suite["cases"] = [c for c in suite["cases"] if c["name"] not in deleted_names]
    
    # 写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(suite, f, allow_unicode=True, default_flow_style=False)
```

**方案 B：使用 HTTP 工具调用外部 API**

在 Dify 中配置 HTTP 工具，调用外部服务执行文件操作。

---

## 六、测试与调试

### 6.1 测试输入

准备一个测试用的 `listener_output`：

```json
{
  "repo": "test/repo",
  "branch": "main",
  "commit_sha": "test123",
  "commit_message": "feat: add datasource test API",
  "changed_files": [
    {"path": "vega/data-connection/src/controller/DatasourceController.java", "status": "modified"}
  ],
  "scopes": ["vega-data-connection"],
  "scope_tags": ["regression"],
  "suggested_suites": ["测试数据源"],
  "affected_api_names": ["测试数据源连接"],
  "affected_api_paths": ["/api/data-connection/v1/datasource/test"],
  "need_add_cases": true,
  "diffs": []
}
```

### 6.2 验证输出

检查输出的 JSON 是否符合格式要求：
- `status` 字段是否为 `success`、`skipped` 或 `error`
- `yaml_changes` 中的用例是否符合 `case_schema.yaml` 规范
- `url` 字段是否与 `apis.yaml` 中的 `name` 一致
- 变量引用是否在 `global_manifest.yaml` 中

### 6.3 调试技巧

1. **分步测试**：
   - 先测试"跳过"场景（`need_add_cases=false`）
   - 再测试"新增用例"场景
   - 最后测试"修改用例"场景

2. **检查知识库检索**：
   - 确认知识库中的文件能被正确检索
   - 检查检索结果是否包含必要的规范信息

3. **验证输出格式**：
   - 使用 JSON Schema 验证输出的 JSON
   - 确保所有必填字段都存在

---

## 七、CI 集成

### 7.1 调用 Dify API

在 GitHub Actions 中调用 Dify 的 API：

```yaml
- name: Call Agent A
  env:
    DIFY_API_KEY: ${{ secrets.DIFY_API_KEY }}
    DIFY_APP_ID: ${{ secrets.DIFY_AGENT_A_APP_ID }}
  run: |
    curl -X POST "https://api.dify.ai/v1/chat-messages" \
      -H "Authorization: Bearer $DIFY_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "inputs": {
          "listener_output": "${{ toJson(listener_output) }}",
          "base_dir": "testcase/vega"
        },
        "query": "根据提交变更维护测试用例",
        "response_mode": "blocking",
        "user": "github-actions"
      }' > agent_a_output.json
```

### 7.2 应用变更

使用外部脚本应用智能体的输出：

```yaml
- name: Apply Agent A changes
  run: |
    python scripts/apply_agent_a_changes.py \
      --input agent_a_output.json \
      --base-dir testcase/vega
```

---

## 八、常见问题

### Q1: 如何确保智能体遵循规范？

A: 
1. 在知识库中导入所有规范文件
2. 在 Prompt 中明确要求"必须严格遵循规范"
3. 在输出 JSON 中验证字段是否符合规范

### Q2: 智能体输出的 YAML 格式不正确怎么办？

A: 
1. 在 Prompt 中明确要求输出 JSON 格式的变更信息
2. 由外部脚本负责将 JSON 转换为 YAML 并写入文件
3. 这样可以避免智能体直接生成 YAML 时的格式问题

### Q3: 如何处理多个 suite 文件的变更？

A: 
在输出的 `yaml_changes` 中，为每个需要修改的 suite 文件创建一个条目：

```json
{
  "yaml_changes": {
    "testcase/vega/suites/测试数据源.yaml": {...},
    "testcase/vega/suites/新增数据源.yaml": {...}
  }
}
```

---

## 九、下一步

配置完成后：

1. ✅ 测试智能体 A 的基本功能
2. ✅ 验证输出格式是否符合要求
3. ✅ 集成到 CI/Workflow 中
4. ✅ 配置智能体 B、C、D（参考类似方式）

---

祝你配置顺利！如有问题，请参考《多智能体协作实施指南.md》。
