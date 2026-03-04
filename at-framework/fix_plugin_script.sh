#!/bin/bash
# Dify 插件脚本自动修复工具

SCRIPT_FILE="plugin_repackaging.sh"
BACKUP_FILE="${SCRIPT_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

echo "=== Dify 插件脚本修复工具 ==="
echo ""

# 1. 检查脚本是否存在
if [ ! -f "$SCRIPT_FILE" ]; then
    echo "错误: 找不到脚本文件 $SCRIPT_FILE"
    exit 1
fi

# 2. 备份原脚本
echo "1. 备份原脚本..."
cp "$SCRIPT_FILE" "$BACKUP_FILE"
echo "   备份保存为: $BACKUP_FILE"
echo ""

# 3. 查找问题代码
echo "2. 查找问题代码..."
PROBLEM_LINES=$(grep -n "chmod.*dify-plugin-mingw64\|dify-plugin-mingw64_nt-10.0-19045-amd64" "$SCRIPT_FILE" | head -5)
if [ -z "$PROBLEM_LINES" ]; then
    echo "   未找到相关问题代码，可能已经修复"
    echo "   请查看脚本内容确认"
    exit 0
fi

echo "   找到以下问题代码:"
echo "$PROBLEM_LINES" | while IFS=: read -r line_num line_content; do
    echo "   行 $line_num: $line_content"
done
echo ""

# 4. 创建修复后的脚本
echo "3. 创建修复后的脚本..."
TMP_FILE=$(mktemp)
LINE_NUM=0

while IFS= read -r line; do
    LINE_NUM=$((LINE_NUM + 1))
    
    # 检查是否是 chmod 行
    if echo "$line" | grep -q "chmod.*dify-plugin-mingw64_nt-10.0-19045-amd64"; then
        echo "   修复行 $LINE_NUM: chmod 命令"
        # 添加修复后的代码
        cat >> "$TMP_FILE" << 'FIXED_CODE'
# Fixed: Added file existence and OS check for Windows compatibility
if [ -f "dify-plugin-mingw64_nt-10.0-19045-amd64" ]; then
    if [[ "$(uname -s)" != MINGW* ]] && [[ "$(uname -s)" != MSYS* ]] && [[ "$(uname -s)" != CYGWIN* ]]; then
FIXED_CODE
        # 保留原 chmod 命令，但添加缩进
        echo "        $line" >> "$TMP_FILE"
        echo "    fi" >> "$TMP_FILE"
        echo "else" >> "$TMP_FILE"
        echo "    echo \"Info: Plugin file not found, skipping chmod (this is normal on Windows)\"" >> "$TMP_FILE"
        echo "fi" >> "$TMP_FILE"
    # 检查是否是直接执行文件的行
    elif echo "$line" | grep -q "^\./dify-plugin-mingw64_nt-10.0-19045-amd64\|^[[:space:]]*\./dify-plugin-mingw64_nt-10.0-19045-amd64"; then
        echo "   修复行 $LINE_NUM: 文件执行"
        echo "if [ -f \"dify-plugin-mingw64_nt-10.0-19045-amd64\" ]; then" >> "$TMP_FILE"
        echo "    $line" >> "$TMP_FILE"
        echo "else" >> "$TMP_FILE"
        echo "    echo \"Warning: Plugin file not found, skipping execution\"" >> "$TMP_FILE"
        echo "fi" >> "$TMP_FILE"
    else
        # 保持原样
        echo "$line" >> "$TMP_FILE"
    fi
done < "$SCRIPT_FILE"

# 5. 替换原文件
mv "$TMP_FILE" "$SCRIPT_FILE"
chmod +x "$SCRIPT_FILE"

echo ""
echo "4. 修复完成！"
echo ""
echo "=== 修复摘要 ==="
echo "原脚本已备份为: $BACKUP_FILE"
echo "修复后的脚本: $SCRIPT_FILE"
echo ""
echo "=== 验证修复 ==="
echo "查看修复后的相关代码:"
grep -A 5 -B 2 "dify-plugin-mingw64" "$SCRIPT_FILE" | head -20
echo ""
echo "现在可以重新运行脚本: bash $SCRIPT_FILE"
