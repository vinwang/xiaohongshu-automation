# 小红书自动化发布工具

完全本地化的小红书内容生成、图片创建、预览确认和发布工具，无需依赖 n8n。

## 使用方式

本项目提供两种使用方式：

### 方式 1: 内容创作规范（推荐用于学习）

使用 `SKILL.md` 作为内容创作规范的参考文档。这个文档包含了：

- ✅ **二极管标题法** - 快速生成吸引眼球的标题
- ✅ **内容结构规范** - 开篇钩子、核心内容、互动引导
- ✅ **标签策略** - 如何选择和使用标签
- ✅ **图片规范** - 封面图和内容图的设计要求
- ✅ **质量检查清单** - 确保内容质量
- ✅ **优化技巧** - 提升内容效果的方法

**适用场景**：
- 学习小红书内容创作规范
- 手动创作笔记时参考
- 理解高质量笔记的标准

### 方式 2: 自动化程序（推荐用于批量生成）

使用 Python 程序自动生成和发布小红书笔记：

- ✅ **智能内容生成** - 二极管标题法、结构化正文、智能标签
- ✅ **AI 图片生成** - 火山引擎 Doubao-Seedream 生成高质量封面和内容图
- ✅ **交互式预览** - 浏览器实时预览、图片轮播、定时选择
- ✅ **灵活发布** - 支持立即发布、定时发布、快速发布
- ✅ **历史记录** - 自动记录所有生成和发布的历史

**适用场景**：
- 批量生成小红书笔记
- 自动化发布流程
- 需要高效内容生产

**快速开始**：
```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env 文件，设置 XHS_API_KEY

# 运行程序
python run.py
```

---

## 特性

- ✅ **智能内容生成** - 二极管标题法、结构化正文、智能标签
- ✅ **AI 图片生成** - 火山引擎 Doubao-Seedream 生成高质量封面和内容图
- ✅ **交互式预览** - 浏览器实时预览、图片轮播、定时选择
- ✅ **单文件运行** - 单个 Python 文件，无需构建
- ✅ **简单配置** - 支持环境变量或交互式输入
- ✅ **灵活发布** - 支持立即发布、定时发布、快速发布

## 快速开始

如果您想使用自动化程序生成和发布小红书笔记，请按以下步骤操作：

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，设置火山引擎 API Key
```

**必需配置**：
```env
XHS_API_KEY=your_api_key_here
```

**可选配置**：
```env
XHS_API_ENDPOINT=https://ark.cn-beijing.volces.com/api/v3
XHS_MODEL=doubao-seed-1-8-251228
XHS_IMAGE_MODEL=doubao-seedream-4-5-251128
XHS_OUTPUT_DIR=./output
```

### 3. 运行

```bash
# 交互式模式
python run.py

# 命令行模式
python run.py -t "AI写作工具" -w 600

# 快速发布（跳过预览）
python run.py -t "效率工具" -q
```

**详细配置说明和参数选项，请查看下方的"使用方法"章节。**

如需了解内容创作规范，请查看 `SKILL.md` 文件。

## 使用方法

### 交互式模式

运行 `python run.py` 后，程序会提示你输入：

1. **主题/选题** - 你想写什么
2. **账号** - 发布到哪个账号
3. **字数** - 正文字数（默认 500）
4. **背景** - 相关背景信息（可选）

然后会自动：
- 生成标题、正文、标签
- 生成封面图和内容图
- 在浏览器中预览
- 等待你的确认
- 发布或定时发布

### 命令行参数

```bash
python run.py [选项]

选项:
  -t, --topic TEXT       主题/选题
  -a, --account TEXT     账号名称
  -w, --words INT        字数（默认：500）
  -c, --context TEXT     背景信息
  -q, --quick            快速发布（跳过预览）
  -g, --generate-only    只生成内容，不发布
  --dry-run             模拟运行，不实际发布
  --help                显示帮助信息
```

### 配置方式

支持三种配置方式（优先级从高到低）：

1. **环境变量** - 最高优先级
2. **.env 文件** - 自动加载（推荐）
3. **交互式输入** - 运行时提示

**必需配置**：
- `XHS_API_KEY` - 火山引擎 API Key

**可选配置**：
- `XHS_API_ENDPOINT` - API 端点（默认：https://ark.cn-beijing.volces.com/api/v3）
- `XHS_MODEL` - 文本模型（默认：doubao-seed-1-8-251228）
- `XHS_IMAGE_MODEL` - 图片模型（默认：doubao-seedream-4-5-251128）
- `XHS_MCP_URL` - MCP 服务端地址
- `XHS_MCP_TOOL` - MCP 工具名称（默认：publish_content）
- `XHS_DEFAULT_ACCOUNT` - 默认账号
- `XHS_DEFAULT_WORD_COUNT` - 默认字数（默认：500）
- `XHS_OUTPUT_DIR` - 输出目录（默认：./output）

## 工作流程

1. **输入** - 提供主题、账号、字数、背景
2. **生成内容** - AI 生成标题、正文、标签（二极管标题法）
3. **生成图片** - AI 生成封面和内容图（火山引擎）
4. **预览确认** - 浏览器预览，确认发布
5. **发布** - 立即发布或定时发布

## 配置说明

### 必需配置

#### 火山引擎 API Key

用于调用豆包大模型生成内容和图片。

**配置方式**（任选一种）：

1. **.env 文件**（推荐）：
   ```env
   XHS_API_KEY=你的火山引擎 API Key
   ```

2. **环境变量**：
   ```bash
   export XHS_API_KEY="你的火山引擎 API Key"
   ```

3. **运行时输入**：
   运行程序时，会提示你输入 API Key

**获取方法**：
1. 访问 [火山引擎](https://console.volcengine.com/)
2. 创建应用并获取 API Key

### 可选配置

#### MCP 服务端

如果需要实际发布到小红书，需要配置 MCP 服务端。

**配置方式**：

1. **.env 文件**：
   ```env
   XHS_MCP_URL=http://your-mcp-server/mcp
   XHS_MCP_TOOL=publish_content
   ```

2. **环境变量**：
   ```bash
   export XHS_MCP_URL="http://your-mcp-server/mcp"
   export XHS_MCP_TOOL="publish_content"
   ```

## 输出

程序会在以下目录生成文件：

- `output/` - 生成的图片和内容
- `history.json` - 发布历史记录

## 示例

### 生成一篇关于 AI 的笔记

```bash
python run.py -t "AI写作工具" -a "张三" -w 600
```

### 快速发布

```bash
python run.py -t "效率工具推荐" -q
```

### 只生成不发布

```bash
python run.py -t "产品评测" -g
```

## 依赖

- Python 3.7+
- requests
- openai

## 故障排查

### 问题：API 调用失败

**解决**：检查 API Key 是否正确，网络连接是否正常。

### 问题：图片生成失败

**解决**：检查火山引擎 API 配置，确保有足够的配额。

### 问题：预览无法打开

**解决**：确保浏览器可用，或手动打开 `output/preview.html`。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- GitHub: https://github.com/vinwang/xiaohongshu-automation

---

## 两种使用方式对比

| 特性 | SKILL.md（内容规范） | Python 程序（自动化） |
|------|---------------------|---------------------|
| **用途** | 学习创作规范、手动创作参考 | 自动生成和发布 |
| **输出** | 规范和指导文档 | 实际的笔记内容和图片 |
| **自动化程度** | 手动 | 完全自动化 |
| **适用场景** | 学习小红书创作 | 批量生产内容 |
| **需要 API Key** | 否 | 是（火山引擎） |
| **内容质量** | 依赖人工 | 依赖 AI，但有质量检查 |
| **发布功能** | 无 | 有（模拟/MCP/浏览器） |
| **文件位置** | `SKILL.md` | `run.py` + `src/` |

**推荐使用流程**：

1. **新手入门**：先阅读 `SKILL.md` 了解小红书内容创作规范
2. **手动创作**：根据规范手动创作几篇笔记，熟悉规则
3. **自动化生成**：使用 Python 程序批量生成内容，提高效率
4. **质量把控**：对比手动创作和自动生成的效果，优化内容质量