#!/bin/bash
# 本地 CI/CD 测试环境配置脚本
# 用途：在本地模拟 GitHub Actions 环境，测试 Stage 3 工作流

echo "=========================================="
echo "🚀 本地 CI/CD 测试环境配置"
echo "=========================================="

# 设置基础目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"  # 进入项目根目录
echo "项目目录: $PROJECT_DIR"

echo ""
echo "[1/5] 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ 未找到 Python，请先安装 Python 3"
    exit 1
fi
echo "✅ Python: $($PYTHON --version)"

echo ""
echo "[2/5] 安装依赖..."
$PYTHON -m pip install pyyaml requests -q 2>/dev/null || pip install pyyaml requests -q 2>/dev/null
echo "✅ 依赖安装完成"

echo ""
echo "[3/5] 设置环境变量..."
export VEGA_TEST_HOST="${VEGA_TEST_HOST:-10.4.111.209}"
export VEGA_TEST_TOKEN="${VEGA_TEST_TOKEN:-test-token}"
export GITHUB_REPOSITORY="susan-meng/pipehome"
export GITHUB_REF_NAME="main"
export GITHUB_SHA="$(git rev-parse HEAD 2>/dev/null || echo 'local-test')"

echo "  VEGA_TEST_HOST=$VEGA_TEST_HOST"
echo "  VEGA_TEST_TOKEN=$VEGA_TEST_TOKEN"
echo "  GITHUB_SHA=$GITHUB_SHA"

echo ""
echo "[4/5] 运行本地 CI 测试..."
cd "$PROJECT_DIR/at-framework"

echo ""
echo "  → Step 1: 提交监听"
$PYTHON scripts/commit_listener.py \
  --repo-path .. \
  --mapping testcase/vega/_config/path_scope_mapping.yaml \
  --apis testcase/vega/_config/apis.yaml \
  --output /tmp/local_listener_output.json

if [ $? -ne 0 ]; then
    echo "❌ 提交监听失败"
    exit 1
fi
echo "✅ 提交监听完成"

echo ""
echo "  → Step 2: 智能体 B - 维度分析"
$PYTHON scripts/agent_b_dimension.py \
  --listener-output /tmp/local_listener_output.json \
  --mapping testcase/vega/_config/path_scope_mapping.yaml \
  --output /tmp/local_dimension_analysis.json

if [ $? -ne 0 ]; then
    echo "❌ 维度分析失败"
    exit 1
fi
echo "✅ 维度分析完成"

echo ""
echo "  → Step 3: 智能体 C - 用例筛选"
$PYTHON scripts/agent_c_local.py \
  --listener-output /tmp/local_listener_output.json \
  --dimension-analysis /tmp/local_dimension_analysis.json \
  --base-dir testcase/vega \
  --output /tmp/local_execution_plan.json

if [ $? -ne 0 ]; then
    echo "❌ 用例筛选失败"
    exit 1
fi
echo "✅ 用例筛选完成"

echo ""
echo "[5/5] 生成测试报告..."
$PYTHON scripts/ci_diagnose.py

echo ""
echo "=========================================="
echo "📊 本地测试完成"
echo "=========================================="
echo ""
echo "输出文件:"
echo "  - /tmp/local_listener_output.json     (提交监听输出)"
echo "  - /tmp/local_dimension_analysis.json  (维度分析)"
echo "  - /tmp/local_execution_plan.json      (执行计划)"
echo ""
echo "查看执行计划:"
echo "  cat /tmp/local_execution_plan.json | $PYTHON -m json.tool"
echo ""
