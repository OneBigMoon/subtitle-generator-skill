# Changelog

所有项目的显著变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 初始版本发布
- 基于 FastAPI 的 REST API 服务
- 支持字幕打轴（自动对齐时间戳）
- 支持多种 Whisper 模型（tiny/base/small/medium/large）
- 支持 JSON 和文件两种返回格式
- Docker 容器化部署
- OpenClaw (龙虾) Skill 支持
- 完整的 API 文档和示例

## [1.0.0] - 2025-03-28

### Added
- ✨ 核心功能：基于音频和口播稿生成 SRT 字幕文件
- ✨ 字幕打轴：自动对齐口播稿与音频时间戳
- ✨ REST API：提供标准 HTTP 接口
- ✨ 多模型支持：tiny, base, small, medium, large
- ✨ 双格式输出：JSON 响应或直接下载 SRT 文件
- 🐳 Docker 支持：一键部署，开箱即用
- 🤖 OpenClaw Skill：支持作为龙虾智能体技能使用
- 📚 完整文档：README、API 文档、使用示例
- 🧪 健康检查：/health 端点监控服务状态
- 📋 模型列表：/models 端点查看支持的模型

### Technical Details
- 使用 OpenAI Whisper 进行音频转录
- 使用 SequenceMatcher 进行文本对齐
- 智能中文分段（10-15字为一段）
- 字符级时间戳精确对齐
- 完全本地运行，无需外部 API Key

[Unreleased]: https://github.com/OneBigMoon/subtitle-generator-skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/OneBigMoon/subtitle-generator-skill/releases/tag/v1.0.0
