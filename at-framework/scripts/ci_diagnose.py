#!/usr/bin/env python3
"""
CI/CD 诊断工具
用于排查 GitHub Actions 运行问题
"""

import os
import sys
import yaml


def check_secrets():
    """检查必需的 Secrets 配置"""
    print("="*60)
    print("🔍 检查 GitHub Secrets 配置")
    print("="*60)
    
    # 本地环境变量检查（模拟）
    host = os.environ.get("VEGA_TEST_HOST", "")
    token = os.environ.get("VEGA_TEST_TOKEN", "")
    
    issues = []
    
    if not host:
        issues.append("❌ VEGA_TEST_HOST 未设置")
        print("❌ VEGA_TEST_HOST: 未配置")
        print("   请设置: export VEGA_TEST_HOST=your-test-host")
    else:
        print(f"✅ VEGA_TEST_HOST: {host}")
    
    if not token:
        issues.append("❌ VEGA_TEST_TOKEN 未设置")
        print("❌ VEGA_TEST_TOKEN: 未配置")
        print("   请设置: export VEGA_TEST_TOKEN=your-token")
    else:
        masked = token[:10] + "..." if len(token) > 10 else "***"
        print(f"✅ VEGA_TEST_TOKEN: {masked}")
    
    if issues:
        print("\n⚠️ 在 GitHub 上配置 Secrets:")
        print("   https://github.com/susan-meng/pipehome/settings/secrets/actions")
        return False
    
    print("\n✅ 所有 Secrets 已配置")
    return True


def check_file_structure():
    """检查文件结构"""
    print("\n" + "="*60)
    print("🔍 检查文件结构")
    print("="*60)
    
    required_files = [
        ".github/workflows/vega-ci-stage3.yml",
        "at-framework/scripts/agent_a_maintenance.py",
        "at-framework/scripts/agent_b_dimension.py",
        "at-framework/scripts/agent_c_selector.py",
        "at-framework/scripts/agent_d_report.py",
        "at-framework/scripts/commit_listener.py",
        "at-framework/testcase/vega/_config/path_scope_mapping.yaml",
        "at-framework/testcase/vega/_config/apis.yaml",
        "at-framework/requirement.txt",
    ]
    
    base_dir = "/Users/xiaomengmeng/Downloads/pipehomedemo"
    missing = []
    
    for file in required_files:
        full_path = os.path.join(base_dir, file)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} - 缺失")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️ 缺失 {len(missing)} 个文件")
        return False
    
    print("\n✅ 所有必需文件存在")
    return True


def check_apis_config():
    """检查 API 配置"""
    print("\n" + "="*60)
    print("🔍 检查 API 配置")
    print("="*60)
    
    apis_path = "/Users/xiaomengmeng/Downloads/pipehomedemo/at-framework/testcase/vega/_config/apis.yaml"
    
    try:
        with open(apis_path, "r") as f:
            apis = yaml.safe_load(f) or []
        
        print(f"✅ 加载了 {len(apis)} 个 API")
        
        # 检查必填字段
        issues = []
        for i, api in enumerate(apis):
            if not api.get("name"):
                issues.append(f"API #{i}: 缺少 name")
            if not api.get("url"):
                issues.append(f"API #{i}: 缺少 url")
            if not api.get("method"):
                issues.append(f"API #{i}: 缺少 method")
        
        if issues:
            for issue in issues[:5]:
                print(f"⚠️ {issue}")
            return False
        
        print("✅ API 配置格式正确")
        return True
        
    except Exception as e:
        print(f"❌ 无法加载 API 配置: {e}")
        return False


def check_path_mapping():
    """检查路径映射配置"""
    print("\n" + "="*60)
    print("🔍 检查 Path Scope Mapping")
    print("="*60)
    
    mapping_path = "/Users/xiaomengmeng/Downloads/pipehomedemo/at-framework/testcase/vega/_config/path_scope_mapping.yaml"
    
    try:
        with open(mapping_path, "r") as f:
            mapping = yaml.safe_load(f) or {}
        
        subsystems = mapping.get("subsystems", [])
        print(f"✅ 加载了 {len(subsystems)} 个子系统")
        
        for sub in subsystems:
            sid = sub.get("id", "unknown")
            patterns = sub.get("path_patterns", [])
            print(f"   - {sid}: {len(patterns)} 个路径模式")
        
        if not subsystems:
            print("⚠️ 没有配置子系统")
            return False
        
        print("✅ Path Scope Mapping 配置正确")
        return True
        
    except Exception as e:
        print(f"❌ 无法加载配置: {e}")
        return False


def generate_fix_script():
    """生成修复脚本"""
    print("\n" + "="*60)
    print("🛠️ 生成修复建议")
    print("="*60)
    
    script = '''#!/bin/bash
# CI/CD 环境修复脚本

echo "=== 修复 CI/CD 配置 ==="

# 1. 检查 Python 依赖
echo "[1/3] 检查 Python 依赖..."
pip install pyyaml requests 2>/dev/null || pip3 install pyyaml requests

# 2. 设置环境变量（本地测试用）
echo "[2/3] 设置环境变量..."
export VEGA_TEST_HOST="${VEGA_TEST_HOST:-10.4.111.209}"
export VEGA_TEST_TOKEN="${VEGA_TEST_TOKEN:-your-test-token}"

# 3. 验证配置
echo "[3/3] 验证配置..."
cd at-framework
python3 -c "import yaml; yaml.safe_load(open('testcase/vega/_config/apis.yaml'))" && echo "✅ API 配置有效"
python3 -c "import yaml; yaml.safe_load(open('testcase/vega/_config/path_scope_mapping.yaml'))" && echo "✅ Path Mapping 有效"

echo ""
echo "=== 修复完成 ==="
echo "请确保在 GitHub Secrets 中配置:"
echo "  - VEGA_TEST_HOST"
echo "  - VEGA_TEST_TOKEN"
'''
    
    script_path = "/tmp/fix_ci_env.sh"
    with open(script_path, "w") as f:
        f.write(script)
    os.chmod(script_path, 0o755)
    
    print(f"✅ 修复脚本已生成: {script_path}")
    print("运行: bash /tmp/fix_ci_env.sh")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 CI/CD 诊断工具")
    print("="*60)
    
    results = []
    
    results.append(("Secrets 配置", check_secrets()))
    results.append(("文件结构", check_file_structure()))
    results.append(("API 配置", check_apis_config()))
    results.append(("Path Mapping", check_path_mapping()))
    
    generate_fix_script()
    
    # 汇总
    print("\n" + "="*60)
    print("📊 诊断汇总")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查通过！可以正常部署运行。")
    else:
        print("\n⚠️ 有检查项失败，请参考上面的修复建议。")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
