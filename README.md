# 小红书自动化发布工具 - 本地化版本

完全本地化的小红书内容生成、图片创建、预览确认和发布工具，无需依赖 n8n。

## 特性

- ✅ **智能内容生成** - 二极管标题法、结构化正文、智能标签
- ✅ **AI 图片生成** - 火山引擎 Doubao-Seedream 生成高质量封面和内容图
- ✅ **交互式预览** - 浏览器实时预览、图片轮播、定时选择
- ✅ **命令行工具** - 简洁的 CLI 界面，支持交互式和参数化调用
- ✅ **灵活发布** - 支持立即发布、定时发布、快速发布
- ✅ **历史记录** - 自动保存发布记录，支持查询
- ✅ **完全本地化** - 无需 n8n，直接在本地运行

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/vinwang/xiaohongshu-automation.git
cd xiaohongshu-automation
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key 和 Cookie
```

或使用 CLI 命令配置：

```bash
npm run dev config
```

## 使用方法

### 方式 1: 交互式发布

```bash
npm run dev publish
```

按照提示输入主题、账号、字数等信息。

### 方式 2: 命令行参数

```bash
# 基本发布
npm run dev publish -t "AI写作工具"

# 完整参数
npm run dev publish -t "AI写作工具" -a "张三,李四" -w 500 -c "介绍AI写作的优势"

# 快速发布（跳过预览）
npm run dev publish -t "AI写作工具" -q

# 只生成内容，不发布
npm run dev publish -t "AI写作工具" -g
```

### 查看历史记录

```bash
npm run dev history
```

### 配置环境变量

```bash
npm run dev config
```

## 工作流程

1. **输入解析** - 接收主题、账号、字数、背景等信息
2. **内容生成** - 使用二极管标题法生成标题，创建结构化正文
3. **图片生成** - 根据内容生成封面图和内容图
4. **预览确认** - 在浏览器中预览生成的笔记
5. **发布** - 立即发布或定时发布到小红书

## 配置说明

### 火山引擎配置

- `DOUBAO_API_KEY` - 火山引擎 API Key
- `DOUBAO_MODEL` - 豆包模型名称（默认: doubao-seed-1-8-251228）
- `DOUBAO_BASE_URL` - API 基础 URL

### 小红书配置

- `XHS_COOKIE` - 小红书登录 Cookie
- `MCP_URL` - MCP 服务端 URL（可选）

### 输出目录

- `OUTPUT_DIR` - 输出目录（默认: ./output）
- `PREVIEW_DIR` - 预览目录（默认: ./preview）

## 获取 API Key

### 火山引擎 API Key

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 创建应用并获取 API Key
3. 开通豆包大模型和图片生成服务

### 小红书 Cookie

1. 在浏览器中登录小红书
2. 打开开发者工具（F12）
3. 在 Network 标签中查看任意请求的 Cookie
4. 复制完整的 Cookie 字符串

## 项目结构

```
xiaohongshu-automation/
├── src/
│   ├── modules/
│   │   ├── contentGenerator.ts  # 内容生成模块
│   │   ├── imageGenerator.ts    # 图片生成模块
│   │   ├── previewManager.ts    # 预览管理模块
│   │   └── publisher.ts         # 发布模块
│   ├── __tests__/               # 单元测试
│   ├── types.ts                 # 类型定义
│   ├── config.ts                # 配置管理
│   ├── index.ts                 # 主入口
│   └── cli.ts                   # CLI 入口
├── output/                      # 输出目录
├── preview/                     # 预览目录
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

## 开发

### 构建项目

```bash
npm run build
```

### 运行测试

```bash
npm test
```

### 监听模式

```bash
npm run dev
```

## 注意事项

- ⚠️ Cookie 包含登录凭证，请勿泄露或提交到版本控制
- ⚠️ 小红书 Cookie 会过期，需定期更新
- ⚠️ 避免频繁发布，以免触发平台限制
- ⚠️ 图片生成需要消耗 API 配额

## 许可证

MIT License

## 相关资源

- [Auto-Redbook-Skills](https://github.com/comeonzhj/Auto-Redbook-Skills)
- [火山引擎 API 文档](https://www.volcengine.com/docs)
- [豆包大模型](https://www.volcengine.com/product/ark)