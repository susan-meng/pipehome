# Dify 智能体 A Mock 调试快速指南

## 问题

智能体在 Dify 中无法直接访问文件系统，需要将 `base_dir` 下的实际文件内容传递给智能体。

## 解决方案：添加 existing_suites 变量

### 步骤 1：在 Dify 中添加变量

1. 进入智能体配置页面
2. 在 "变量" 部分，点击 "+ 添加"
3. 填写：
   - **变量名**：`existing_suites`
   - **类型**：Paragraph（因为内容较长）
   - **描述**：现有测试套件文件内容（用于 Mock 调试）
   - **是否必填**：否

### 步骤 2：获取 Suite 文件内容

#### 方法 1：直接读取文件（推荐）

打开 `testcase/vega/suites/测试数据源.yaml`，复制全部内容。

#### 方法 2：使用脚本（如果文件很大）

运行：
```bash
# Windows PowerShell
Get-Content testcase/vega/suites/测试数据源.yaml -Raw

# Linux/Mac
cat testcase/vega/suites/测试数据源.yaml
```

### 步骤 3：在 Dify 中填写

1. 在调试界面的 `existing_suites` 变量中，粘贴步骤 2 获取的内容
2. 填写其他变量（`listener_output`、`base_dir` 等）
3. 运行调试

---

## 完整 Mock 调试参数示例

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

### 变量 3：existing_suites（paragraph，可选但推荐）

**⚠️ 注意**：Dify 对输入有长度限制（约 48 字符），请使用精简版内容：

```yaml
story: 测试数据源
cases:
- name: 查询数据源类型清单
  url: 查询所有支持数据源
- name: 测试数据源_参数校验_type缺省_请求失败
  url: 测试数据源连接
```

**字符数**：约 100 字符（如果还是超限，可以进一步精简为只有 `story: 测试数据源`）

**为什么精简版可以工作**：
- 智能体主要需要 `story` 字段确认套件名称
- 完整的字段规范会从知识库的 `case_schema.yaml` 获取
- 示例用例只需要展示基本结构即可

---

## 为什么需要 existing_suites？

1. **智能体无法访问文件系统**：Dify 中的智能体运行在容器中，无法直接读取本地文件
2. **知识库可能不完整**：虽然可以将文件导入知识库，但 Mock 调试时直接传入更快速
3. **确保准确性**：直接传入实际文件内容，避免知识库检索不准确的问题

---

## 预期效果

提供 `existing_suites` 后，智能体应该能够：
1. ✅ 正确解析现有用例
2. ✅ 判断是否需要新增用例
3. ✅ 生成符合规范的用例变更
4. ✅ 输出正确的 JSON 格式结果

---

## 注意事项

1. **文件内容要完整**：确保复制的是完整的 YAML 文件内容
2. **格式要正确**：YAML 格式必须正确，否则智能体无法解析
3. **变量引用**：确保文件中的变量引用（如 `${bin_data_template_mysql}`）在 `global_manifest.yaml` 中存在
4. **API 名称匹配**：确保用例中的 `url` 字段与 `apis.yaml` 中的 `name` 完全一致

---

## 如果还是失败

1. **检查 Prompt**：确保 Prompt 中已添加对 `existing_suites` 的说明
2. **检查知识库**：确保知识库中已导入 `case_schema.yaml`、`suite_schema.yaml`、`apis.yaml`、`global_manifest.yaml`
3. **检查 LLM Provider**：确保 LLM Provider 配置正确且可用
4. **查看详细日志**：在 Dify 中查看详细的错误日志

---

## 总结

**快速配置步骤**：
1. ✅ 添加 `existing_suites` 变量（类型：Paragraph）
2. ✅ 复制 `testcase/vega/suites/测试数据源.yaml` 的完整内容
3. ✅ 在调试界面粘贴到 `existing_suites` 变量
4. ✅ 填写其他变量并运行调试

按照上述步骤即可完成 Mock 调试！
