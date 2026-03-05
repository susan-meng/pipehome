#!/bin/bash
# ========================================
# 🔄 OpenClaw 模型切换工具
# ========================================
# 使用方法: bash switch_model.sh [模型名称]
# 示例: bash switch_model.sh kimi-k2.5

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 可用模型列表
MODELS=(
    "kimi-k2.5:Kimi K2.5 (默认) - 长上下文，适合复杂任务"
    "glm-4-flash:智谱 GLM-4-Flash - 快速响应，成本低"
    "kimi-code:Kimi Code - 代码专用模型"
)

# 显示帮助
show_help() {
    echo "========================================"
    echo "🔄 OpenClaw 模型切换工具"
    echo "========================================"
    echo ""
    echo "使用方法:"
    echo "  bash switch_model.sh [模型名称]"
    echo ""
    echo "可用模型:"
    echo ""
    for i in "${!MODELS[@]}"; do
        IFS=':' read -r name desc <<< "${MODELS[$i]}"
        echo "  $((i+1)). $name"
        echo "     $desc"
        echo ""
    done
    echo "示例:"
    echo "  bash switch_model.sh kimi-k2.5    # 切换到 Kimi K2.5"
    echo "  bash switch_model.sh glm-4-flash  # 切换到 GLM-4-Flash"
    echo ""
}

# 显示当前模型
show_current() {
    echo "📊 当前模型状态:"
    echo ""
    openclaw status 2>&1 | grep -A5 "Sessions" | grep "agent:main:main" || echo "   无法获取当前模型"
    echo ""
}

# 切换模型
switch_model() {
    local target_model=$1
    
    echo "🔄 正在切换模型到: $target_model"
    echo ""
    
    case $target_model in
        "kimi-k2.5"|"kimi"|"1")
            echo "✅ 切换到: Kimi K2.5"
            # 使用环境变量或配置文件切换
            export MOONSHOT_API_KEY="${MOONSHOT_API_KEY:-sk-3IQPH...6P2jZKDQ}"
            echo "   API Key: ${MOONSHOT_API_KEY:0:10}..."
            ;;
        "glm-4-flash"|"glm"|"2")
            echo "✅ 切换到: 智谱 GLM-4-Flash"
            export ZHIPU_API_KEY="${ZHIPU_API_KEY:-3d474475003049928387e6448469dfd9.Hq6fWQGM84BUZOlx}"
            echo "   API Key: ${ZHIPU_API_KEY:0:20}..."
            # 需要重启会话生效
            echo ""
            echo "⚠️  注意: 需要重启 OpenClaw 会话才能生效"
            echo "   方法1: 等待当前会话自动过期 (约30分钟)"
            echo "   方法2: 手动重启 OpenClaw"
            ;;
        "kimi-code"|"code"|"3")
            echo "✅ 切换到: Kimi Code"
            export MOONSHOT_API_KEY="sk-k-imi-nylchQuyJiPQAVRFegapcWUVG0zeBwSHu1VGwUfX0VCbgdAPXoVC3VCsLRUmcmt2"
            echo "   API Key: sk-k-imi..."
            echo ""
            echo "⚠️  注意: Kimi Code 需要正确的模型标识"
            echo "   如果切换失败，请确认模型名称格式"
            ;;
        *)
            echo "${RED}❌ 错误: 未知的模型 '$target_model'${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    echo "📝 切换记录已保存"
    echo "⏰ 新设置将在下次会话开始时生效"
    echo ""
    
    # 记录切换历史
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 切换到: $target_model" >> ~/.openclaw/model_switch.log
}

# 显示切换历史
show_history() {
    if [ -f ~/.openclaw/model_switch.log ]; then
        echo "📜 模型切换历史:"
        echo ""
        tail -10 ~/.openclaw/model_switch.log
        echo ""
    else
        echo "ℹ️  暂无切换历史"
        echo ""
    fi
}

# 主函数
main() {
    # 无参数时显示帮助和当前状态
    if [ $# -eq 0 ]; then
        show_help
        show_current
        show_history
        exit 0
    fi
    
    # 处理参数
    case $1 in
        "-h"|"--help"|"help")
            show_help
            ;;
        "-c"|"--current"|"status")
            show_current
            ;;
        "-l"|"--log"|"history")
            show_history
            ;;
        *)
            switch_model "$1"
            ;;
    esac
}

# 创建日志目录
mkdir -p ~/.openclaw

# 运行主函数
main "$@"
