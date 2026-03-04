# Dify 智能体 A 精简 Mock 参数

## 问题

Dify 平台对输入变量有长度限制（约 48 字符），但完整的 suite 文件内容太长，无法直接传入。

## 解决方案：使用精简版 existing_suites

### 精简版 existing_suites（用于 Mock 调试）

只包含必要的结构信息和 1-2 个示例用例，确保智能体能够理解文件格式：

```yaml
feature: 接口参数校验
story: 测试数据源
switch: y
tags: [regression, data-connection]
cases:
- name: 查询数据源类型清单
  url: 查询所有支持数据源
  code_check: '200'
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
  body_params: "{\"type\": \"\", \"bin_data\": ${bin_data_template_mysql}}"
  code_check: '400'
```

**字符数**：约 200 字符，远低于限制。

---

## 完整 Mock 调试参数

### 变量 1：listener_output（paragraph，必填）

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

### 变量 2：base_dir（string，必填）

```
testcase/vega
```

### 变量 3：existing_suites（paragraph，精简版）

```yaml
feature: 接口参数校验
story: 测试数据源
switch: y
tags: [regression, data-connection]
cases:
- name: 查询数据源类型清单
  url: 查询所有支持数据源
  code_check: '200'
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
  body_params: "{\"type\": \"\", \"bin_data\": ${bin_data_template_mysql}}"
  code_check: '400'
```

---

## 更精简版本（如果还是超限）

如果上面的内容还是超过限制，可以使用这个更精简的版本：

```yaml
story: 测试数据源
cases:
- name: 查询数据源类型清单
  url: 查询所有支持数据源
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
```

**字符数**：约 100 字符。

---

## 说明

### 为什么精简版可以工作？

1. **智能体主要需要的信息**：
   - `story` 字段：确认 suite 名称匹配
   - `cases` 数组：了解现有用例结构
   - 示例用例：理解用例格式

2. **不需要的字段**：
   - 完整的用例字段（`prev_case`、`path_params` 等）
   - 所有用例（只需要 1-2 个示例）

3. **规范文件会提供**：
   - `case_schema.yaml`：完整的用例字段规范
   - `suite_schema.yaml`：完整的套件字段规范
   - `apis.yaml`：API 定义
   - `global_manifest.yaml`：全局变量

### 智能体如何工作？

1. 从 `existing_suites` 了解现有用例的基本结构
2. 从知识库的 `case_schema.yaml` 获取完整的字段规范
3. 从知识库的 `apis.yaml` 获取 API 定义
4. 根据规范生成符合要求的用例

---

## 使用建议

1. **首次调试**：使用最精简版本（约 100 字符）
2. **功能验证**：使用精简版本（约 200 字符）
3. **生产环境**：不提供 `existing_suites`，让智能体从知识库检索完整内容

---

## 超精简版本（48 字符限制）

如果 Dify 有严格的 48 字符限制，使用这个版本：

```yaml
story:测试数据源
```

**字符数**：约 15 字符，远低于限制。

**说明**：只提供 `story` 字段，让智能体确认套件名称。完整的用例结构和规范会从知识库获取。

## 如果还是失败

如果精简版还是超过限制，可以：

1. **不提供 existing_suites**：让智能体完全依赖知识库
2. **使用超精简版本**：只提供 `story:测试数据源`（约 15 字符）
3. **在 Prompt 中说明**：在 Prompt 中添加示例，说明 suite 文件的结构

---

## 总结

**根据 Dify 限制选择版本**：

### 版本 1：超精简版（推荐，48 字符限制）

```yaml
story:测试数据源
```

**字符数**：约 15 字符 ✅

### 版本 2：精简版（如果限制较宽松）

```yaml
story: 测试数据源
cases:
- name: 查询数据源类型清单
  url: 查询所有支持数据源
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
```

**字符数**：约 100 字符

### 版本 3：完整精简版（如果限制很宽松）

```yaml
feature: 接口参数校验
story: 测试数据源
switch: y
tags: [regression, data-connection]
cases:
- name: 查询数据源类型清单
  url: 查询所有支持数据源
  code_check: '200'
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
  body_params: "{\"type\": \"\", \"bin_data\": ${bin_data_template_mysql}}"
  code_check: '400'
```

**字符数**：约 200 字符

**建议**：优先使用版本 1（超精简版），智能体会从知识库获取完整的规范信息。
