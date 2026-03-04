# Dify 智能体 A 快速配置清单

按照以下步骤快速配置智能体 A（用例维护）。

---

## ✅ 配置步骤

### 1. 创建 Agent

- [ ] 在 Dify 中创建新的 Agent
- [ ] 命名为：**智能体A-用例维护** 或 **Agent A - Case Maintenance**
- [ ] 选择类型：**Agent（编排模式）**

---

### 2. 配置 Prompt（提示词）

- [ ] 打开 "Orchestration"（编排）页面
- [ ] 在 Prompt 文本框中，复制粘贴 `docs/Dify智能体A_Prompt模板.txt` 中的内容
- [ ] 点击右上角 "Generate" 按钮（可选，用于生成优化版本）

---

### 3. 配置 Variables（变量）

点击 "Variables" 部分的 "+ Add" 按钮，添加以下变量：

#### 变量 1：listener_output（必填）

- [ ] **变量名**：`listener_output`
- [ ] **类型**：String
- [ ] **描述**：提交监听服务的输出（JSON 字符串）
- [ ] **是否必填**：是

#### 变量 2：base_dir（必填）

- [ ] **变量名**：`base_dir`
- [ ] **类型**：String
- [ ] **描述**：测试模块的基础目录（相对于项目根目录的路径）
- [ ] **默认值**：`testcase/vega`
- [ ] **是否必填**：是
- [ ] **说明**：
  - `base_dir` 指向一个测试模块的根目录
  - 该目录下应包含 `_config/` 和 `suites/` 子目录
  - 当前项目中的模块：`testcase/vega`（VEGA 模块）
  - 如果有其他模块，填写对应的路径，如：`testcase/其他模块名`
  - 路径格式：相对于项目根目录，如 `testcase/vega`（不要以 `./` 开头）

#### 变量 3：commit_sha（可选）

- [ ] **变量名**：`commit_sha`
- [ ] **类型**：String
- [ ] **描述**：当前 commit 的 SHA
- [ ] **是否必填**：否

---

### 4. 配置 Knowledge Base（知识库）

#### 4.1 创建知识库

- [ ] 在 Dify 中创建新知识库
- [ ] 命名为：**测试框架规范** 或 **Test Framework Specs**

#### 4.2 导入文件

将以下文件导入到知识库中：

- [ ] `testcase/_config/spec/case_schema.yaml`（用例规范）
- [ ] `testcase/_config/spec/suite_schema.yaml`（套件规范）
- [ ] `testcase/vega/_config/apis.yaml`（接口定义）
- [ ] `testcase/vega/_config/global_manifest.yaml`（全局变量清单）
- [ ] `testcase/vega/_config/path_scope_mapping.yaml`（可选，路径映射）

#### 4.3 关联知识库到 Agent

- [ ] 在 Agent 配置的 "Knowledge Base" 部分，点击 "+ Add"
- [ ] 选择刚才创建的知识库
- [ ] 设置检索模式：**混合检索（Hybrid）**（推荐）

---

### 5. 配置 Tools（工具）

**注意**：如果 Dify 不支持文件操作工具，可以跳过此步骤，采用"输出 JSON + 外部脚本执行"的方案。

- [ ] 检查 Dify 是否支持文件读写工具
- [ ] 如果支持，配置文件读取工具
- [ ] 如果支持，配置文件写入工具

---

### 6. 设置 LLM Provider

- [ ] 点击右上角警告中的 "去设置" 按钮
- [ ] 配置 LLM Provider（如 OpenAI、Claude 等）
- [ ] 设置 API Key
- [ ] 选择模型（推荐：GPT-4 或 Claude 3.5）

---

### 7. 测试配置

#### 7.1 准备测试输入

创建测试用的 `listener_output`：

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

#### 7.2 运行测试

- [ ] 在 Dify 的调试界面中，输入测试数据
- [ ] 检查输出 JSON 是否符合格式要求
- [ ] 验证用例是否符合 `case_schema.yaml` 规范

---

### 8. 获取 API 信息

- [ ] 在 Dify 中打开 "Access API"（访问 API）页面
- [ ] 复制 **App ID**（用于 CI 集成）
- [ ] 复制 **API Key**（用于 CI 集成）
- [ ] 保存到 GitHub Secrets：
  - `DIFY_API_KEY`
  - `DIFY_AGENT_A_APP_ID`

---

## 📋 配置检查清单

完成配置后，检查以下项目：

- [ ] Prompt 已正确配置
- [ ] Variables（listener_output、base_dir）已添加
- [ ] Knowledge Base 已创建并关联
- [ ] 规范文件已导入到知识库
- [ ] LLM Provider 已设置
- [ ] 测试运行成功
- [ ] 输出 JSON 格式正确
- [ ] API 信息已保存

---

## 🔗 相关文档

- **详细配置指南**：`docs/Dify智能体A配置指南.md`
- **Prompt 模板**：`docs/Dify智能体A_Prompt模板.txt`
- **多智能体实施指南**：`docs/多智能体协作实施指南.md`

---

## ⚠️ 常见问题

### Q1: 知识库文件如何导入？

A: 在 Dify 的知识库页面，点击 "导入" 或 "Upload"，选择本地文件上传。

### Q2: 智能体输出的 JSON 格式不正确？

A: 检查 Prompt 中的输出格式说明，确保明确要求输出 JSON。如果仍有问题，可以在 Prompt 中添加 JSON Schema 验证要求。

### Q3: 如何测试智能体？

A: 在 Dify 的调试界面中，输入测试数据，查看输出结果。建议先测试简单的场景（如 `need_add_cases=false`）。

---

配置完成后，就可以在 CI/Workflow 中调用智能体 A 了！
