# Vega CI/CD - Stage 2 使用指南

## 🎯 Stage 2 新特性

相比 Stage 1（固定跑冒烟测试），Stage 2 实现了：

| 特性 | Stage 1 | Stage 2 |
|------|---------|---------|
| 触发方式 | Push/PR 触发 | ✅ 智能分析变更内容 |
| 用例筛选 | 固定 `TAGS=smoke` | ✅ 按变更范围动态筛选 |
| 测试策略 | 全量冒烟 | ✅ 精准执行相关用例 |
| 覆盖分析 | 无 | ✅ 自动识别受影响 API |
| 报告 | Allure 原生 | ✅ 增强版执行摘要 |

---

## 🚀 快速开始

### 1. 确保配置 Secrets

在 GitHub 仓库 **Settings → Secrets and variables → Actions**：

| Secret | 说明 |
|--------|------|
| `VEGA_TEST_HOST` | 测试环境主机 |
| `VEGA_TEST_TOKEN` | API 认证 Token |

### 2. 触发 Stage 2 CI

```bash
# 方式1: 推送代码（自动触发）
git push origin main

# 方式2: 手动触发
# GitHub → Actions → "Vega CI - Stage 2 (Smart Selection)" → Run workflow
```

### 3. 查看智能分析结果

在 workflow run 页面可以看到：
- **提交监听输出**: `listener_output.json`
- **用例筛选结果**: 选中了哪些用例
- **测试报告**: Allure HTML + 执行摘要

---

## 🧠 智能筛选策略

Stage 2 采用三层筛选策略：

```
Layer 1: 提交监听
  └── 分析 git diff → 识别变更文件
  └── 匹配 path_scope_mapping.yaml → 得到 scopes + affected_apis

Layer 2: 用例筛选
  └── 策略A: 有 affected_apis → 按 API 名称精确筛选
  └── 策略B: 有 scopes → 按 scope 范围筛选（regression tags）
  └── 策略C: 兜底 → 冒烟测试

Layer 3: 执行
  └── 设置 CASE_NAMES 或 TAGS 环境变量
  └── pytest 只跑选中的用例
```

### 筛选示例

| 变更内容 | 识别结果 | 执行用例 |
|----------|----------|----------|
| `vega/data-connection/DatasourceController.java` | Scope: `vega-data-connection`<br>APIs: `新增数据源`, `查询数据源` | 只跑数据源相关的 10 条用例 |
| `vega/gateway/RouteConfig.java` | Scope: `vega-gateway` | 跑网关相关的 regression 用例 |
| 未匹配到任何 scope | - | 兜底跑冒烟测试 |

---

## 📁 文件结构

```
pipehome/
├── .github/workflows/
│   ├── vega-ci-demo.yml          # Stage 1: 简化版（保留）
│   └── vega-ci-stage2.yml        # Stage 2: 智能筛选版 ⭐
├── at-framework/
│   ├── scripts/
│   │   ├── commit_listener.py    # ⭐ 提交监听脚本
│   │   └── extract_cases.py      # 用例提取工具
│   ├── testcase/
│   │   └── vega/
│   │       └── _config/
│   │           ├── apis.yaml                 # API 定义
│   │           └── path_scope_mapping.yaml   # ⭐ 路径映射配置
│   └── ...
└── docs/
    └── STAGE2_GUIDE.md           # 本指南
```

---

## ⚙️ 核心配置文件

### path_scope_mapping.yaml

定义**提交路径**与**测试范围**的映射关系：

```yaml
subsystems:
  - id: vega-data-connection      # scope 标识
    name: VEGA数据连接
    path_patterns:                # 路径匹配规则
      - "vega/data-connection/**"
      - "vega/vega-backend/**/data-connection*"
    scope_tags: [regression, data-connection]
    suggested_suites:             # 建议测试的套件
      - 测试数据源
      - 新增数据源
      - 查询数据源
```

**匹配规则**：
- `**` 匹配任意层级目录
- `*` 匹配任意字符
- 示例：`vega/data-connection/**` 匹配所有数据连接相关的变更

### apis.yaml

定义 API 信息，用于推断变更影响的接口：

```yaml
- name: 新增数据源
  url: /api/data-connection/v1/datasource
  method: POST
```

---

## 🔧 本地测试提交监听

```bash
cd /Users/xiaomengmeng/Downloads/pipehomedemo/at-framework

# 安装依赖
pip install pyyaml

# 运行提交监听（分析最近一次提交）
python scripts/commit_listener.py \
  --repo-path .. \
  --mapping testcase/vega/_config/path_scope_mapping.yaml \
  --apis testcase/vega/_config/apis.yaml \
  --output listener_output.json

# 查看输出
cat listener_output.json | python -m json.tool
```

**输出示例**：
```json
{
  "repo": "susan-meng/pipehome",
  "branch": "main",
  "commit_sha": "abc123...",
  "changed_files": [
    {"path": "vega/data-connection/DatasourceController.java", "status": "modified"}
  ],
  "scopes": ["vega-data-connection"],
  "scope_tags": ["regression", "data-connection"],
  "suggested_suites": ["测试数据源", "新增数据源"],
  "affected_api_names": ["新增数据源", "查询数据源列表"],
  "need_add_cases": false
}
```

---

## 📊 扩展能力

### 1. 添加新的路径映射

编辑 `testcase/vega/_config/path_scope_mapping.yaml`：

```yaml
subsystems:
  - id: my-new-module
    name: 我的新模块
    path_patterns:
      - "vega/my-module/**"
    scope_tags: [regression, my-module]
    suggested_suites:
      - 我的测试套件
```

### 2. 扩展 API 关键词映射

编辑 `scripts/commit_listener.py` 中的 `infer_affected_apis` 函数：

```python
keyword_mapping = {
    "my-feature": ["API名称1", "API名称2"],
    # ... 添加更多
}
```

### 3. 自定义筛选策略

在 `select-cases` job 中添加新的策略分支：

```yaml
- name: Custom Selection
  run: |
    # 根据 commit message 中的关键词筛选
    if echo "$COMMIT_MSG" | grep -q "performance"; then
      export TAGS=performance
    fi
```

---

## 🎓 Stage 2 vs Stage 1 对比

| 场景 | Stage 1 执行 | Stage 2 执行 | 节省 |
|------|-------------|-------------|------|
| 改了网关代码 | 跑 20 条冒烟用例 | 跑 5 条网关用例 | 75% ⬇️ |
| 改了数据源代码 | 跑 20 条冒烟用例 | 跑 10 条数据源用例 | 50% ⬇️ |
| 改了无关文档 | 跑 20 条冒烟用例 | 跑 0 条（可配置跳过） | 100% ⬇️ |
| 首次运行 | 跑 20 条冒烟用例 | 跑 20 条冒烟用例 | 持平 |

---

## 🚀 升级到 Stage 3（完整智能体）

Stage 2 已经实现了核心的**提交监听 + 智能筛选**能力。

Stage 3 将引入 LLM 智能体：
- **智能体A**: 根据 diff 自动维护用例（增删改）
- **智能体B**: 分析测试维度（功能/契约/边界/性能）
- **智能体C**: 智能排序执行批次
- **智能体D**: 生成自然语言测试报告

准备好进入 Stage 3 时，参考 `docs/测试架构设计_基于Commit与多智能体.md`

---

## ❓ 常见问题

### Q: 变更没有匹配到任何 scope？
A: 检查 `path_scope_mapping.yaml` 中的 `path_patterns` 是否覆盖你的变更路径。

### Q: 如何跳过无关变更的测试？
A: 在 `commit_listener.py` 中添加逻辑：如果 `scopes` 为空，设置 `skip_tests=true`，在 workflow 中使用 `if` 条件跳过。

### Q: 可以支持多个模块吗？
A: 可以！为每个模块创建独立的 `path_scope_mapping.yaml`，在提交监听时遍历所有模块配置。

---

**当前状态**: ✅ Stage 2 已就绪，开始享受智能筛选带来的效率提升吧！
