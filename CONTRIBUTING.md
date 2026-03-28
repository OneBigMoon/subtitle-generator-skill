# 贡献指南

感谢您对字幕生成器项目的关注！我们欢迎所有形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过 [GitHub Issues](https://github.com/OneBigMoon/subtitle-generator-skill/issues) 提交。

提交问题时，请包含：
- 问题的清晰描述
- 复现步骤
- 期望行为 vs 实际行为
- 环境信息（操作系统、Docker 版本等）
- 相关日志或截图

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/您的用户名/subtitle-generator-skill.git
   cd subtitle-generator-skill
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/您的功能名称
   # 或
   git checkout -b fix/修复的问题
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

4. **推送到您的 Fork**
   ```bash
   git push origin feature/您的功能名称
   ```

5. **创建 Pull Request**
   - 描述您做了什么更改
   - 说明为什么这些更改是必要的
   - 关联相关的 Issue（如果有）

### 代码规范

- 遵循 PEP 8 Python 代码风格
- 添加适当的注释和文档字符串
- 确保代码通过类型检查
- 添加测试（如果适用）

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>: <description>

[optional body]

[optional footer]
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat: 添加对 WAV 格式的支持

- 更新音频文件验证逻辑
- 添加 WAV 格式测试用例

Closes #123
```

## 开发环境设置

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/OneBigMoon/subtitle-generator-skill.git
cd subtitle-generator-skill

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python api_server.py
# 或
uvicorn api_server:app --reload
```

### Docker 开发

```bash
# 构建镜像
docker build -t subtitle-generator:dev .

# 运行容器
docker run -p 8000:8000 -v $(pwd):/app subtitle-generator:dev
```

## 测试

```bash
# 运行测试（待添加）
pytest

# 检查代码风格
flake8 .

# 类型检查
mypy .
```

## 文档

- 更新 README.md 如果更改了用户接口
- 更新 API 文档如果更改了端点
- 更新 CHANGELOG.md 记录重要变更

## 行为准则

- 尊重所有参与者
- 接受建设性的批评
- 关注对社区最有利的事情
- 展现同理心对待其他社区成员

## 获取帮助

- 查看 [README.md](README.md) 获取基本使用信息
- 查看 [API 文档](http://localhost:8000/docs) 了解接口详情
- 在 [GitHub Discussions](https://github.com/OneBigMoon/subtitle-generator-skill/discussions) 提问

再次感谢您的贡献！
