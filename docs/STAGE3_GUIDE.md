# Stage 3 智能体接入方案

## 🎯 概述

Stage 3 实现了完整的 **多智能体协作测试架构**，包含四个智能体：

| 智能体 | 名称 | 职责 | 输入 | 输出 |
|--------|------|------|------|------|
| **Agent A** | 用例维护智能体 | 分析变更，自动生成/修改用例 | listener_output.json | auto_generated_cases.yaml |
| **Agent B** | 维度分析智能体 | 分析测试维度（功能/契约/边界/性能） | listener_output.json | dimension_analysis.json |
| **Agent C** | 用例筛选智能体 | 智能排序，创建执行批次 | listener_output + dimension_analysis | execution_plan.json |
| **Agent D** | 报告生成智能体 | 解析结果，生成自然语言报告 | JUnit + execution_plan | final_report.md |

---

## 🏗️ 架构流程

```
研发提交
    │
    ▼
┌─────────────────┐
│ 提交监听        │ 分析 git diff，识别 scopes + affected_apis
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Agent A│ │ Agent B│ 并行执行
│ 用例维护│ │ 维度分析│
└───┬────┘ └───┬────┘
    │          │
    └────┬─────┘
         ▼
    ┌────────┐
    │ Agent C│ 聚合 A、B 结果，创建执行计划
    │ 用例筛选│
    └───┬────┘
        ▼
   ┌──────────┐
   │ 执行测试  │ pytest 执行筛选出的用例
   └────┬─────┘
        ▼
   ┌────────┐
   │ Agent D│ 生成最终报告
   │ 报告生成│
   └────────┘
```

---

## 📁 文件结构

```
pipehome/
├── .github/workflows/
│   ├── vega-ci-demo.yml      # Stage 1: 简化版
│   ├── vega-ci-stage2.yml    # Stage 2: 智能筛选
│   └── vega-ci-stage3.yml    # Stage 3: 智能体版 ⭐
├── at-framework/scripts/
│   ├── commit_listener.py      # 提交监听（Stage 2/3 共用）
│   ├── agent_a_maintenance.py  # ⭐ 智能体 A: 用例维护
│   ├── agent_b_dimension.py    # ⭐ 智能体 B: 维度分析
│   ├── agent_c_selector.py     # ⭐ 智能体 C: 用例筛选
│   ├── agent_d_report.py       # ⭐ 智能体 D: 报告生成
│   └── extract_cases.py        # 用例提取工具
└── docs/
    ├── STAGE2_GUIDE.md       # Stage 2 指南
    └── STAGE3_GUIDE.md       # 本指南
```

---

## 🚀 快速开始

### 1. 确保配置 Secrets

在 GitHub 仓库 **Settings → Secrets and variables → Actions**：

| Secret | 说明 |
|--------|------|
| `VEGA_TEST_HOST` | 测试环境主机 |
| `VEGA_TEST_TOKEN` | API 认证 Token |

### 2. 触发 Stage 3 CI

```bash
# 推送代码（自动触发）
git push origin main

# 或手动触发
# GitHub → Actions → "Vega CI - Stage 3 (AI Agents)" → Run workflow
```

### 3. 查看执行结果

在 workflow run 页面：
- 查看每个智能体的执行状态
- 下载 artifacts（用例、维度分析、执行计划、报告）
- PR 会自动收到 Agent D 生成的测试报告

---

## 🤖 智能体详解

### Agent A: 用例维护智能体

**功能**：根据代码变更自动生成测试用例

**触发条件**：`need_add_cases = true`（有新增文件且命中 scope）

**生成策略**：

| 变更类型 | 生成用例 |
|---------|---------|
| API 新增 | 基础功能用例 + 参数缺失用例 |
| 参数校验变更 | 边界值测试用例（长度/范围） |
| 字段变更 | 字段完整性用例 |
| 其他修改 | 回归用例 |

**使用**：
```bash
python scripts/agent_a_maintenance.py \
  --listener-output listener_output.json \
  --output auto_generated_cases.yaml
```

---

### Agent B: 测试维度分析智能体

**功能**：分析变更，确定需要执行的测试维度

**识别维度**：

| 维度 | 识别依据 | 对应 Tags |
|------|---------|----------|
| functional | 默认执行 | regression, smoke |
| contract | DTO/Model/字段变更 | contract |
| boundary | Validator/约束/长度 | boundary |
| stress | 并发/异步/限流 | stress |
| performance | 缓存/优化/批处理 | performance |

**输出示例**：
```json
{
  "dimensions": ["functional", "contract", "boundary"],
  "reason": "文件路径包含关键词 'validator'，识别出边界测试",
  "test_type_tags": {
    "functional": ["regression", "smoke"],
    "contract": ["regression", "contract"],
    "boundary": ["boundary", "regression"]
  }
}
```

---

### Agent C: 用例筛选智能体

**功能**：根据维度分析创建分层执行计划

**执行批次**（按优先级）：

| 批次 | 优先级 | 内容 | 筛选条件 |
|------|--------|------|---------|
| 1 | 最高 | 新增功能相关 | `affected_apis` |
| 2 | 高 | 回归测试 | `scope + regression` tag |
| 3 | 中 | 契约测试 | `contract` tag |
| 4 | 中 | 边界测试 | `boundary` tag |
| 5+ | 低 | 其他维度 | dimension tags |

**输出示例**：
```json
{
  "mode": "case_names",
  "batches": [
    {
      "priority": 1,
      "label": "新增功能相关",
      "case_names": ["新增数据源_正常请求_返回成功", ...],
      "count": 5
    },
    {
      "priority": 2,
      "label": "回归测试",
      "case_names": ["查询数据源_参数缺省_请求成功", ...],
      "count": 10
    }
  ],
  "total_cases": 15
}
```

---

### Agent D: 报告生成智能体

**功能**：解析测试结果，生成自然语言报告

**输入**：
- JUnit XML 测试结果
- 执行计划（可选）
- 维度分析（可选）

**输出**：Markdown 格式报告

**报告内容**：
- 执行摘要（总用例/通过/失败/通过率）
- 测试维度说明
- 失败用例详情（前10个）
- 结论与建议（是否通过、修复建议）

**示例报告**：
```markdown
# 🧪 智能测试报告

## 📊 执行摘要
| 指标 | 数值 |
|------|------|
| 总用例数 | 15 |
| ✅ 通过 | 14 |
| ❌ 失败 | 1 |
| 📈 通过率 | 93.33% |

### 🎯 测试维度
**执行的测试维度**: functional, contract

### 📋 执行批次
- **批次 1: 新增功能相关** - 5 条用例
- **批次 2: 回归测试** - 10 条用例

## 💡 结论与建议
✅ **测试通过** - 通过率高于95%，代码质量良好，可以合并。
```

---

## 🔧 本地测试智能体

### Agent A
```bash
cd at-framework
python scripts/agent_a_maintenance.py \
  --listener-output listener_output.json \
  --base-dir testcase/vega \
  --apis-config testcase/vega/_config/apis.yaml
```

### Agent B
```bash
python scripts/agent_b_dimension.py \
  --listener-output listener_output.json \
  --mapping testcase/vega/_config/path_scope_mapping.yaml
```

### Agent C
```bash
python scripts/agent_c_selector.py \
  --listener-output listener_output.json \
  --dimension-analysis dimension_analysis.json \
  --base-dir testcase/vega
```

### Agent D
```bash
python scripts/agent_d_report.py \
  --junit-report report/junit_report.xml \
  --execution-plan execution_plan.json \
  --dimension-analysis dimension_analysis.json
```

---

## 📊 Stage 3 vs Stage 2 对比

| 特性 | Stage 2 | Stage 3 |
|------|---------|---------|
| 用例维护 | 人工 | ✅ Agent A 自动生成 |
| 维度分析 | 固定规则 | ✅ Agent B 智能识别 |
| 用例筛选 | 单层 | ✅ Agent C 分层优先级 |
| 报告生成 | Allure 原生 | ✅ Agent D 自然语言 |
| 自适应 | 弱 | ✅ 强 |

---

## 🔮 未来扩展（接入 LLM）

当前智能体是**基于规则的简化版**，未来可以无缝接入 LLM：

```python
# Agent A 接入 LLM 示例
def generate_cases_with_llm(diff_content, api_schema):
    prompt = f"""
    根据以下代码变更生成测试用例：
    Diff: {diff_content}
    API Schema: {api_schema}
    
    生成符合以下格式的 YAML 用例：
    ...
    """
    return call_llm_api(prompt)
```

**接入点**：
- Agent A: 用例生成逻辑
- Agent B: 变更影响分析
- Agent C: 用例优先级排序
- Agent D: 报告结论生成

---

## ✅ 总结

Stage 3 实现了完整的**多智能体协作测试流水线**：

1. **Agent A** - 自动维护用例，保持用例与代码同步
2. **Agent B** - 智能分析维度，确保测试覆盖全面
3. **Agent C** - 分层筛选执行，提高测试效率
4. **Agent D** - 自动生成报告，降低人工分析成本

**下一步**：根据实际运行情况调整智能体的规则参数，或接入 LLM 提升智能化水平。
