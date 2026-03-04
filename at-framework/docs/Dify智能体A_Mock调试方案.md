# Dify 智能体 A Mock 调试方案

## 问题

智能体在 Dify 中无法直接访问文件系统，需要将 `base_dir` 下的文件内容通过变量或知识库传递给智能体。

## 解决方案

### 方案 1：将 Suite 文件内容作为变量传入（推荐用于 Mock 调试）

#### 步骤 1：添加新变量 `existing_suites`

在 Dify 智能体配置中，添加一个新变量：

- **变量名**：`existing_suites`
- **类型**：String（或 Paragraph，如果内容很长）
- **描述**：现有测试套件文件内容（YAML 格式）
- **是否必填**：否（用于 Mock 调试）

#### 步骤 2：准备 Suite 文件内容

将 `testcase/vega/suites/测试数据源.yaml` 的内容作为字符串传入：

```yaml
feature: 接口参数校验
story: 测试数据源
switch: y
tags: [regression, data-connection]
cases:
- name: 查询数据源类型清单
  url: 查询所有支持数据源
  prev_case: ''
  path_params: ''
  query_params: ''
  body_params: ''
  form_params: ''
  resp_values: ''
  code_check: '200'
  resp_schema: ''
  resp_check: "{\n \"$.connectors[18].olk_connector_name\": \"opensearch\"\n}"
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
  prev_case: ''
  path_params: ''
  query_params: ''
  body_params: "{\n    \"type\": \"\",\n    \"bin_data\": ${bin_data_template_mysql}\n}"
  form_params: ''
  resp_values: ''
  code_check: '400'
  resp_schema: ''
  resp_check: ''
```

#### 步骤 3：修改 Prompt

在 Prompt 中添加说明，如果提供了 `existing_suites` 变量，则使用该变量内容，否则从知识库或文件系统读取。

---

## 方案 2：将 Suite 文件内容放入知识库（推荐用于生产）

### 步骤 1：将 Suite 文件导入知识库

1. 进入知识库 "测试框架规范"
2. 导入 `testcase/vega/suites/测试数据源.yaml`
3. 等待索引完成

### 步骤 2：在 Prompt 中明确说明

在 Prompt 中添加：
```
如果提供了 existing_suites 变量，使用该变量的内容作为现有用例。
否则，从知识库中检索 suite 文件内容，或根据 base_dir 和 suggested_suites 查找对应的 suite 文件。
```

---

## 方案 3：在 Prompt 中提供示例（最简单）

在 Prompt 中添加一个示例，说明 suite 文件的结构：

```markdown
## 现有 Suite 文件示例

`testcase/vega/suites/测试数据源.yaml` 的结构示例：

```yaml
feature: 接口参数校验
story: 测试数据源
switch: y
tags: [regression, data-connection]
cases:
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
  body_params: "{\"type\": \"\", \"bin_data\": ${bin_data_template_mysql}}"
  code_check: '400'
  tags: ["api:测试数据源连接", "regression"]
```

**注意**：实际调试时，请从知识库检索完整的 suite 文件内容。
```

---

## 完整 Mock 调试参数

### 变量配置

#### 变量 1：listener_output（必填）

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

#### 变量 2：base_dir（必填）

```
testcase/vega
```

#### 变量 3：existing_suites（可选，用于 Mock）

```yaml
feature: 接口参数校验
story: 测试数据源
switch: y
tags: [regression, data-connection]
cases:
- name: 查询数据源类型清单
  url: 查询所有支持数据源
  prev_case: ''
  path_params: ''
  query_params: ''
  body_params: ''
  form_params: ''
  resp_values: ''
  code_check: '200'
  resp_schema: ''
  resp_check: "{\n \"$.connectors[18].olk_connector_name\": \"opensearch\"\n}"
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
  prev_case: ''
  path_params: ''
  query_params: ''
  body_params: "{\n    \"type\": \"\",\n    \"bin_data\": ${bin_data_template_mysql}\n}"
  form_params: ''
  resp_values: ''
  code_check: '400'
  resp_schema: ''
  resp_check: ''
```

---

## 修改 Prompt 模板

在 Prompt 的 "输入信息" 部分添加：

```markdown
- **existing_suites**（可选）：现有测试套件文件内容（YAML 格式）。如果提供，直接使用该内容；否则从知识库检索或根据 base_dir 查找。
```

在 "工作流程" 部分修改：

```markdown
1. 读取输入：解析 `listener_output` 和 `base_dir`
2. 读取现有用例：
   - 如果提供了 `existing_suites` 变量，使用该变量的内容
   - 否则，从知识库检索 `{base_dir}/suites/{suggested_suites[0]}.yaml` 的内容
   - 或根据 `base_dir` 和 `suggested_suites` 查找对应的 suite 文件
3. 读取规范：从知识库读取 `case_schema.yaml`、`suite_schema.yaml`、`apis.yaml`、`global_manifest.yaml`
4. 分析变更：根据 `commit_message`、`affected_api_names`、`diffs` 判断需要执行的操作
5. 生成变更：按照规范生成新增/修改/删除的用例
6. 输出结果：输出 JSON 格式的变更信息
```

---

## 快速配置步骤

### 步骤 1：添加 existing_suites 变量

1. 在 Dify 智能体配置页面，点击 "变量" 部分的 "+ 添加"
2. 填写：
   - **变量名**：`existing_suites`
   - **类型**：Paragraph（因为内容较长）
   - **描述**：现有测试套件文件内容（用于 Mock 调试）
   - **是否必填**：否

### 步骤 2：准备 Suite 文件内容

读取 `testcase/vega/suites/测试数据源.yaml` 的完整内容，复制到 `existing_suites` 变量中。

### 步骤 3：修改 Prompt

在 Prompt 中添加对 `existing_suites` 变量的说明和使用逻辑。

### 步骤 4：测试

使用最小测试参数，在 `existing_suites` 中填入实际的 suite 文件内容，运行测试。

---

## 自动化脚本（可选）

如果需要频繁更新 `existing_suites` 的内容，可以创建一个脚本：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 existing_suites 变量内容，用于 Dify Mock 调试
"""
import yaml
import json

def generate_existing_suites(base_dir="testcase/vega", suite_name="测试数据源"):
    """生成 suite 文件的 YAML 内容"""
    suite_path = f"{base_dir}/suites/{suite_name}.yaml"
    
    with open(suite_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== existing_suites 变量内容 ===")
    print(content)
    print("\n=== 可以直接复制到 Dify 变量中 ===")

if __name__ == "__main__":
    generate_existing_suites()
```

---

## 总结

**推荐方案**：
1. ✅ **Mock 调试**：添加 `existing_suites` 变量，直接传入 suite 文件内容
2. ✅ **生产环境**：将 suite 文件导入知识库，智能体从知识库检索

**最小 Mock 调试参数**：
- `listener_output`：包含必需字段的 JSON
- `base_dir`：`testcase/vega`
- `existing_suites`：实际的 suite 文件 YAML 内容（可选但推荐）

按照上述方案配置即可！
