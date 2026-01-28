# 小红书自动化发布工具 - 快速开始

## 🚀 极简使用（推荐）

### 1. 安装依赖（只需一次）

```bash
pip install requests openai
```

### 2. 运行

```bash
python xhs_auto.py
```

按照提示输入：
- 主题
- 字数
- 背景说明（可选）
- API Key（首次需要输入）

就这么简单！

---

## 📖 使用方式

### 方式 1: 交互式模式（最简单）

```bash
python xhs_auto.py
```

然后按照提示输入信息即可。

### 方式 2: 命令行参数

```bash
# 基本使用
python xhs_auto.py -t "AI写作工具"

# 完整参数
python xhs_auto.py -t "AI写作工具" -w 500 -c "介绍AI写作的优势"

# 快速发布（跳过预览）
python xhs_auto.py -t "AI写作工具" -q
```

### 方式 3: 使用环境变量

```bash
# Windows
set DOUBAO_API_KEY=your_api_key_here
python xhs_auto.py -t "AI写作工具"

# Linux/Mac
export DOUBAO_API_KEY=your_api_key_here
python xhs_auto.py -t "AI写作工具"
```

---

## ⚙️ 配置说明

### 环境变量（可选）

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DOUBAO_API_KEY` | 火山引擎 API Key | - |
| `DOUBAO_MODEL` | 豆包模型 | `doubao-seed-1-8-251228` |
| `DOUBAO_BASE_URL` | API 地址 | `https://ark.cn-beijing.volces.com/api/v3` |
| `DOUBAO_IMAGE_MODEL` | 图片模型 | `doubao-seedream-4-5-251128` |
| `XHS_COOKIE` | 小红书 Cookie | - |
| `MCP_URL` | MCP 服务端 | `http://47.109.91.65:18060/mcp` |
| `OUTPUT_DIR` | 输出目录 | `./output` |

### 获取 API Key

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 创建应用并获取 API Key
3. 开通豆包大模型和图片生成服务

---

## 📋 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--topic` | `-t` | 主题/选题 | - |
| `--word-count` | `-w` | 字数 | 600 |
| `--context` | `-c` | 背景说明 | - |
| `--quick` | `-q` | 快速发布（跳过预览） | False |

---

## 🎯 完整流程

1. **输入主题** - 告诉工具你想写什么
2. **生成内容** - AI 自动生成标题、正文、标签
3. **生成图片** - AI 自动生成封面和内容图
4. **预览确认** - 在浏览器中预览效果
5. **发布** - 确认后发布到小红书

---

## 💡 使用技巧

### 快速发布

如果不想预览，使用 `-q` 参数：

```bash
python xhs_auto.py -t "AI写作工具" -q
```

### 批量生成

可以创建一个批处理文件：

```bash
# batch.bat
python xhs_auto.py -t "AI写作工具"
python xhs_auto.py -t "效率提升"
python xhs_auto.py -t "时间管理"
```

### 定时发布

在预览时选择"定时发布"，输入时间即可。

---

## ❓ 常见问题

### Q: 提示缺少依赖怎么办？

```bash
pip install requests openai
```

### Q: API Key 从哪里获取？

访问火山引擎控制台，创建应用后获取。

### Q: 可以不配置 Cookie 吗？

可以，不配置会使用模拟发布模式。

### Q: 生成的图片在哪里？

图片的 URL 会直接用于预览和发布，不会下载到本地。

---

## 📝 示例

### 示例 1: 交互式发布

```bash
$ python xhs_auto.py

🚀 小红书自动化发布工具 - 简化版

请输入主题: AI写作工具
请输入字数 (默认600): 500
请输入背景说明 (可选): 介绍AI写作的优势
是否快速发布（跳过预览）？(y/n, 默认n): n

📝 正在生成内容结构...
📝 正在生成完整内容...
✅ 标题: AI写作，只需1秒，便可开挂！
✅ 标签: ['#AI写作', '#效率工具', '#生产力']

🎨 正在生成图片提示词...
🎨 正在生成图片...
   - 生成封面图...
   - 生成内容图 1...
   - 生成内容图 2...
✅ 图片生成完成，共 3 张

👀 预览已打开: ./output/preview_1234567890.html

确认发布吗？(y/n): y

📤 准备发布...
✅ 模拟发布成功

🎉 发布流程完成！
```

### 示例 2: 快速发布

```bash
$ python xhs_auto.py -t "时间管理技巧" -q

🚀 小红书自动化发布工具 - 简化版

📋 主题: 时间管理技巧
📋 字数: 600
📋 背景: 无

📝 正在生成内容结构...
✅ 标题: 时间管理，每天多出2小时！
✅ 标签: ['#时间管理', '#效率', '#生活技巧']

📝 正在生成完整内容...
🎨 正在生成图片提示词...
✅ 图片生成完成，共 3 张

📤 准备发布...
✅ 模拟发布成功

🎉 发布流程完成！
```

---

## 🎉 完成

现在你可以轻松使用这个工具发布小红书内容了！

只需要 3 步：
1. `pip install requests openai`
2. `python xhs_auto.py`
3. 输入主题，完成！