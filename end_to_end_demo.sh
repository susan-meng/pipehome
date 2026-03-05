#!/bin/bash
# ========================================
# 🎬 端到端演示脚本：代码修改 → 智能体运行 → 用例更新
# ========================================
# 使用方法: bash end_to_end_demo.sh

set -e  # 遇到错误立即退出

echo "========================================"
echo "🎬 端到端演示：智能体驱动的测试用例生成"
echo "========================================"
echo ""
echo "📋 流程概览："
echo "  1. 修改代码（新增 API Controller）"
echo "  2. 提交代码到 GitHub"
echo "  3. 触发 GitHub Actions（多智能体协作）"
echo "  4. Agent A 自动生成测试用例"
echo "  5. 下载并合并用例到本地套件"
echo "  6. 验证更新结果"
echo ""
echo "========================================"
echo ""

# 步骤 1: 创建新代码
echo "📝 步骤 1: 创建新的 API Controller..."
cat > vega/data-connection/dc-gateway/src/main/java/com/eisoo/dc/gateway/controller/DemoController.java << 'EOF'
package com.eisoo.dc.gateway.controller;

import org.springframework.web.bind.annotation.*;
import com.eisoo.dc.gateway.domain.vo.HttpResInfo;

/**
 * Demo Controller for end-to-end testing
 */
@RestController
@RequestMapping("/api/data-connection/v1/demo")
public class DemoController {

    @PostMapping("/test")
    public HttpResInfo demoTest(@RequestBody DemoRequest request) {
        return HttpResInfo.success();
    }
}

class DemoRequest {
    private String name;
    private String type;
    // getters and setters
}
EOF
echo "✅ 创建完成: DemoController.java"
echo ""

# 步骤 2: 提交代码
echo "📝 步骤 2: 提交代码到 GitHub..."
git add vega/data-connection/dc-gateway/src/main/java/com/eisoo/dc/gateway/controller/DemoController.java
git commit -m "feat: add DemoController for end-to-end testing

- Add demoTest API for testing purposes
- Support name and type parameters"
git push origin main
echo "✅ 代码已推送到 GitHub"
echo ""

# 步骤 3: 等待并监控 GitHub Actions
echo "📝 步骤 3: 监控 GitHub Actions 运行..."
echo "⏳ 等待 10 秒让 Actions 启动..."
sleep 10

# 获取最新的 run ID
echo "🔍 获取最新的 Workflow Run ID..."
RUN_ID=$(gh run list --repo susan-meng/pipehome --limit 1 --json databaseId --jq '.[0].databaseId')
echo "✅ Run ID: $RUN_ID"
echo ""

# 监控运行状态
echo "⏳ 监控 Workflow 运行状态（约需 1-2 分钟）..."
echo "   你可以打开以下链接查看实时进度:"
echo "   https://github.com/susan-meng/pipehome/actions/runs/$RUN_ID"
echo ""

# 轮询等待完成
MAX_WAIT=180  # 最多等待 3 分钟
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    STATUS=$(gh run view $RUN_ID --repo susan-meng/pipehome --json status --jq '.status' 2>/dev/null || echo "unknown")
    
    if [ "$STATUS" = "completed" ]; then
        echo "✅ Workflow 运行完成！"
        break
    fi
    
    echo "   ⏳ 状态: $STATUS (已等待 ${WAITED}s)"
    sleep 15
    WAITED=$((WAITED + 15))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo "⚠️  等待超时，请手动检查: https://github.com/susan-meng/pipehome/actions/runs/$RUN_ID"
    exit 1
fi

echo ""

# 步骤 4: 查看运行结果
echo "📝 步骤 4: 查看运行结果..."
gh run view $RUN_ID --repo susan-meng/pipehome --json jobs --jq '.jobs[] | select(.name | contains("agent-a")) | {name: .name, status: .status, conclusion: .conclusion}'
echo ""

# 步骤 5: 下载生成的用例
echo "📝 步骤 5: 下载 Agent A 生成的用例..."
rm -rf temp_generated
github actions download $RUN_ID --name agent-a-generated-$RUN_ID --dir temp_generated 2>/dev/null || echo "⚠️  下载失败，可能还没有生成用例"

if [ -f temp_generated/auto_generated_cases.yaml ]; then
    echo "✅ 用例下载成功！"
    echo ""
    echo "📄 生成的用例预览:"
    head -50 temp_generated/auto_generated_cases.yaml
else
    echo "⚠️  没有找到生成的用例文件"
fi
echo ""

# 步骤 6: 合并用例到本地套件
echo "📝 步骤 6: 合并用例到现有测试套件..."
if [ -f temp_generated/auto_generated_cases.yaml ]; then
    python3 << 'PYTHON'
import yaml
import os

# 读取生成的用例
with open('temp_generated/auto_generated_cases.yaml', 'r', encoding='utf-8') as f:
    generated = yaml.safe_load(f)

# 映射 URL 到套件文件
url_to_suite = {
    '新增数据源': 'at-framework/testcase/vega/suites/新增数据源.yaml',
    '更新数据源': 'at-framework/testcase/vega/suites/更新数据源.yaml',
    '删除数据源': 'at-framework/testcase/vega/suites/删除数据源.yaml',
    '测试数据源连接': 'at-framework/testcase/vega/suites/测试数据源.yaml',
    '获取数据源列表': 'at-framework/testcase/vega/suites/查询数据源.yaml',
    '查询数据源列表': 'at-framework/testcase/vega/suites/查询数据源.yaml',
    '查询数据源详情': 'at-framework/testcase/vega/suites/查询数据源.yaml',
}

added_count = 0
for case in generated.get('cases', []):
    url = case.get('url')
    if url in url_to_suite:
        suite_file = url_to_suite[url]
        
        if not os.path.exists(suite_file):
            print(f"⚠️  套件文件不存在: {suite_file}")
            continue
        
        # 读取现有套件
        with open(suite_file, 'r', encoding='utf-8') as f:
            suite = yaml.safe_load(f)
        
        # 检查是否已存在
        existing_names = {c.get('name') for c in suite.get('cases', [])}
        if case['name'] in existing_names:
            print(f"⏭️  跳过已存在用例: {case['name']}")
            continue
        
        # 添加新用例
        if 'cases' not in suite:
            suite['cases'] = []
        suite['cases'].append(case)
        added_count += 1
        
        # 写回文件
        with open(suite_file, 'w', encoding='utf-8') as f:
            yaml.dump(suite, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"✅ 已添加: {case['name']} → {suite_file}")

print(f"\n🎉 合并完成！共添加 {added_count} 条用例")
PYTHON
else
    echo "⚠️  跳过合并步骤（没有可合并的用例）"
fi
echo ""

# 步骤 7: 提交合并的用例
echo "📝 步骤 7: 提交合并的用例到仓库..."
git add at-framework/testcase/vega/suites/
if git diff --cached --quiet; then
    echo "ℹ️  没有需要提交的更改"
else
    git commit -m "test: merge Agent A generated cases from run $RUN_ID

- Auto-generated by Agent A based on code changes
- Run: https://github.com/susan-meng/pipehome/actions/runs/$RUN_ID"
    git push origin main
    echo "✅ 用例已提交到仓库"
fi
echo ""

# 总结
echo "========================================"
echo "🎉 端到端演示完成！"
echo "========================================"
echo ""
echo "📊 执行摘要:"
echo "  • Run ID: $RUN_ID"
echo "  • Actions URL: https://github.com/susan-meng/pipehome/actions/runs/$RUN_ID"
echo "  • 生成的用例: temp_generated/auto_generated_cases.yaml"
echo ""
echo "🔄 完整流程:"
echo "  代码修改 → Git Push → GitHub Actions → Agent A → 用例生成 → 本地合并 → Git Push"
echo ""
echo "========================================"
