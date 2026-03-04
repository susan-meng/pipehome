# Dify 智能体 A 最小测试参数

## 说明

本文档提供基于当前项目的最小但完整的测试参数，确保智能体能够正确输出预期结果。

---

## 一、最小测试参数（推荐用于首次测试）

### 场景：新增用例（need_add_cases=true）

**listener_output**（在 Dify 调试界面中填写，类型：paragraph）：

```json
{
  "repo": "test/repo",
  "branch": "main",
  "commit_sha": "test123",
  "commit_message": "feat: add datasource test API",
  "changed_files": [
    {
      "path": "vega/data-connection/src/controller/DatasourceController.java",
      "status": "modified"
    }
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

**base_dir**（类型：string）：
```
testcase/vega
```

**existing_suites**（类型：paragraph，可选，用于 Mock 调试）：
> **⚠️ 注意**：Dify 对输入有长度限制（约 48 字符），请使用精简版内容：
> 
> ```yaml
> story: 测试数据源
> cases:
> - name: 查询数据源类型清单
>   url: 查询所有支持数据源
> - name: 测试数据源_参数校验_type缺省_请求失败
>   url: 测试数据源连接
> ```
> 
> **说明**：精简版只包含核心结构信息，完整的字段规范会从知识库获取。如果不提供，智能体会尝试从知识库检索。

**commit_sha**（类型：string，可选）：
```
test123
```

---

## 二、预期输出

智能体应该输出类似以下的 JSON：

```json
{
  "status": "success",
  "action": "add",
  "modified_files": ["testcase/vega/suites/测试数据源.yaml"],
  "cases_added": 1,
  "cases_modified": 0,
  "cases_deleted": 0,
  "summary": "新增 1 个用例：测试数据源连接_正常场景_请求成功",
  "yaml_changes": {
    "testcase/vega/suites/测试数据源.yaml": {
      "added_cases": [
        {
          "name": "测试数据源连接_正常场景_请求成功",
          "url": "测试数据源连接",
          "prev_case": "",
          "path_params": "",
          "query_params": "",
          "body_params": "{\"type\": \"mysql\", \"bin_data\": ${bin_data_template_mysql}}",
          "code_check": "200",
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

---

## 三、简化测试参数（用于快速验证）

如果上面的参数仍然有问题，可以使用更简化的版本：

### 场景：跳过用例维护（need_add_cases=false）

**listener_output**：

```json
{
  "scope_tags": ["regression"],
  "suggested_suites": ["测试数据源"],
  "affected_api_names": ["测试数据源连接"],
  "affected_api_paths": ["/api/data-connection/v1/datasource/test"],
  "need_add_cases": false,
  "diffs": []
}
```
**base_dir**：
```
testcase/vega
```

**预期输出**：

```json
{
  "status": "skipped",
  "action": "none",
  "modified_files": [],
  "cases_added": 0,
  "cases_modified": 0,
  "cases_deleted": 0,
  "summary": "无需新增用例，且未检测到需要修改的用例",
  "yaml_changes": {}
}
```

---

## 四、完整测试参数（用于完整功能测试）

### 场景：新增多个用例

**listener_output**：

```json
{
  "repo": "test/repo",
  "branch": "main",
  "commit_sha": "abc123def456",
  "commit_message": "feat: add multiple datasource test APIs",
  "changed_files": [
    {
      "path": "vega/data-connection/src/controller/DatasourceController.java",
      "status": "modified"
    },
    {
      "path": "vega/data-connection/src/service/DatasourceService.java",
      "status": "modified"
    }
  ],
  "scopes": ["vega-data-connection"],
  "scope_tags": ["regression", "data-connection"],
  "suggested_suites": ["测试数据源", "新增数据源"],
  "affected_api_names": ["测试数据源连接", "新增数据源"],
  "affected_api_paths": [
    "/api/data-connection/v1/datasource/test",
    "/api/data-connection/v1/datasource"
  ],
  "need_add_cases": true,
  "diffs": [
    {
      "file": "vega/data-connection/src/controller/DatasourceController.java",
      "changes": "+ @PostMapping(\"/test\")"
    }
  ]
}
```

**base_dir**：
```
testcase/vega
```

**commit_sha**：
```
abc123def456
```

---

## 五、验证要点

### 5.1 检查输出格式

确保输出包含以下字段：
- ✅ `status`: "success" | "skipped" | "error"
- ✅ `action`: "add" | "modify" | "delete" | "none"
- ✅ `modified_files`: 数组
- ✅ `cases_added`: 数字
- ✅ `cases_modified`: 数字
- ✅ `cases_deleted`: 数字
- ✅ `summary`: 字符串
- ✅ `yaml_changes`: 对象

### 5.2 检查用例格式

如果 `status` 为 "success" 且 `action` 为 "add"，检查 `yaml_changes` 中的用例：
- ✅ `name`: 唯一且符合命名规范
- ✅ `url`: 必须与 `apis.yaml` 中的 `name` 完全一致
- ✅ `body_params`: 有效的 JSON 字符串（引号已转义）
- ✅ `tags`: 包含 `api:{api_name}` 和 `regression`
- ✅ 变量引用：使用 `${变量名}` 格式，变量必须在 `global_manifest.yaml` 中

### 5.3 检查知识库

确保知识库中已导入：
- ✅ `case_schema.yaml`
- ✅ `suite_schema.yaml`
- ✅ `apis.yaml`
- ✅ `global_manifest.yaml`

---

## 六、常见问题

### Q1: 输出不是 JSON 格式？

**A:** 
1. 检查 Prompt 中是否明确要求输出 JSON
2. 在 Prompt 中添加 JSON Schema 示例
3. 在 Prompt 末尾强调："请只输出 JSON，不要包含其他文字"

### Q2: 用例格式不符合规范？

**A:**
1. 确保知识库中的 `case_schema.yaml` 已正确导入
2. 在 Prompt 中明确要求遵循 `case_schema.yaml` 规范
3. 检查 `url` 字段是否与 `apis.yaml` 中的 `name` 完全一致

### Q3: 智能体找不到 suite 文件？

**A:**
1. 检查 `suggested_suites` 中的名称是否与实际的 suite 文件 `story` 字段匹配
2. 确认 `base_dir` 路径正确
3. 在 Prompt 中明确说明 suite 文件的查找规则

---

## 七、使用建议

1. **首次测试**：使用"简化测试参数"（need_add_cases=false），验证基本功能
2. **功能验证**：使用"最小测试参数"（need_add_cases=true），验证新增用例功能
3. **完整测试**：使用"完整测试参数"，验证所有功能

---

## 八、在 Dify 中填写

### 步骤 1：打开调试界面

在智能体配置页面，右侧 "调试与预览" 面板

### 步骤 2：填写变量

**listener_output**（选择 "paragraph" 类型）：
- 直接粘贴上面的 JSON（完整格式）

**base_dir**（选择 "string" 类型）：
- 填写：`testcase/vega`

**commit_sha**（可选，选择 "string" 类型）：
- 填写：`test123` 或留空

### 步骤 3：运行测试

点击 "运行" 或 "调试" 按钮，查看输出结果

---

## 总结

**最小但完整的测试参数**：

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

**base_dir**: `testcase/vega`

这个参数包含了智能体所需的最小信息，应该能够触发正确的输出。
