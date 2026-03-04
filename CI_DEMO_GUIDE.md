# Vega 模块 CI/CD Demo 配置指南

## 快速开始

### 1. 配置 GitHub Secrets

在 GitHub 仓库 **Settings → Secrets and variables → Actions** 中添加：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `VEGA_TEST_HOST` | 测试环境主机地址 | `10.4.111.209` |
| `VEGA_TEST_TOKEN` | API 认证 Token | `Bearer xxx...` |

### 2. 触发测试

#### 方式一：自动触发
- 推送代码到 `main` 或 `develop` 分支
- 或创建 Pull Request 到 `main` 分支

#### 方式二：手动触发
1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Vega Module CI Demo**
4. 点击 **Run workflow**

### 3. 查看报告

测试完成后：
1. 进入 **Actions** → 选择 workflow run
2. 在 **Artifacts** 区域下载报告：
   - `allure-report-{run_id}` - Allure HTML 测试报告
   - `test-summary-{run_id}` - 测试摘要

## 本地运行测试

```bash
# 1. 进入框架目录
cd at-framework

# 2. 安装依赖
pip install -r requirement.txt

# 3. 配置环境（复制并修改模板）
cp config/config.ini.template config/config.ini
# 编辑 config.ini，填入你的 host 和 token

# 4. 运行所有测试
python main.py

# 5. 运行特定标签的测试
TAGS=smoke python main.py

# 6. 运行特定范围的测试
SCOPE=vega-data-connection python main.py

# 7. 查看报告
open report/html/index.html
```

## 高级配置

### 筛选用例

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `TAGS` | 按标签筛选 | `TAGS=smoke,regression` |
| `SCOPE` | 按 scope 筛选 | `SCOPE=vega-data-connection` |
| `API_NAME` | 按 API 名称筛选 | `API_NAME=新增数据源` |
| `CASE_NAMES` | 按用例名称筛选 | `CASE_NAMES=新增数据源_mysql_请求成功,删除数据源_请求成功` |

### 提取用例列表（不执行）

```bash
# 提取所有用例
python scripts/extract_cases.py --base-dir testcase/vega

# 按标签提取
python scripts/extract_cases.py --base-dir testcase/vega --tags smoke

# 按 scope 提取
python scripts/extract_cases.py --base-dir testcase/vega --scope vega-data-connection
```

## 项目结构

```
pipehome/
├── .github/
│   └── workflows/
│       └── vega-ci-demo.yml      # CI/CD 工作流配置
├── at-framework/                  # 测试框架主目录
│   ├── config/
│   │   ├── config.ini            # 运行配置（本地使用）
│   │   └── config.ini.template   # 配置模板
│   ├── testcase/
│   │   └── vega/                 # Vega 模块测试用例
│   │       ├── _config/          # 模块配置
│   │       │   ├── apis.yaml     # API 定义
│   │       │   ├── global.yaml   # 全局变量
│   │       │   └── path_scope_mapping.yaml  # 路径映射
│   │       └── suites/           # 测试套件
│   │           ├── 新增数据源.yaml
│   │           ├── 查询数据源.yaml
│   │           └── ...
│   ├── common/                   # 框架公共代码
│   ├── request/                  # HTTP 客户端
│   ├── scripts/                  # 工具脚本
│   ├── report/                   # 测试报告输出
│   ├── main.py                   # 主入口
│   └── conftest.py               # Pytest 配置
└── README.md
```

## 下一步：升级到完整方案

当前简化方案：
- ✅ 支持基本的 CI/CD 触发
- ✅ 生成 Allure 测试报告
- ✅ 手动配置测试范围

完整方案（待实现）：
- ⬜ 提交监听自动识别变更范围
- ⬜ 智能体 A 自动维护用例
- ⬜ 智能体 B 自动分析测试维度
- ⬜ 智能体 C 智能筛选用例
- ⬜ 智能体 D 自动生成报告摘要

参考文档：
- [测试框架架构文档](at-framework/docs/测试框架架构_全自动与智能体规范.md)
- [测试架构设计](at-framework/docs/测试架构设计_基于Commit与多智能体.md)
- [提交监听服务](at-framework/docs/提交监听服务_基于GitHub实现.md)
