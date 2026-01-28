# 如何使用 xiaohongshu-automation Skill

## 目录结构

```
xiaohongshu-automation/
├── src/                    # 源代码目录
│   ├── xhs_auto.py        # 主程序
│   └── config.py          # 配置管理模块
├── run.py                 # Python 启动脚本
├── run.bat                # Windows 启动脚本
├── run.sh                 # Linux/macOS 启动脚本
├── .env                   # 配置文件（包含敏感信息）
├── .env.example           # 配置文件示例
├── requirements.txt       # Python 依赖
├── README.md              # 项目说明
├── QUICKSTART.md          # 快速开始指南
└── SKILL.md               # Skill 文档
```

## 使用方式

### 方式 1: 作为独立程序运行

这是最直接的使用方式，将 xiaohongshu-automation 作为一个独立的 Python 程序运行。

#### Windows

```bash
# 双击运行
run.bat

# 或在命令行中运行
python run.py

# 或传递参数
python run.py -t "AI写作工具"
```

#### Linux/macOS

```bash
# 添加执行权限
chmod +x run.sh

# 运行
./run.sh

# 或使用 Python
python run.py
```

### 方式 2: 在 Claude Code 中作为 Skill 使用

xiaohongshu-automation 已经安装到全局的 Claude Code skills 目录中，可以在任何项目中自动使用。

#### 如何触发

在 Claude Code 对话中，你可以直接使用相关功能：

```
用户：帮我生成一篇关于 AI 的笔记

Claude：好的，我来帮你生成小红书笔记。

[自动调用 xiaohongshu-automation skill]

用户：标题：AI写作工具推荐
账号：张三
字数：600
背景：介绍 AI 写作工具的优势和使用方法

Claude：正在生成内容...
✅ 内容生成完成
✅ 图片生成完成
✅ 预览已生成
```

#### Skill 自动触发场景

1. **内容创作请求**
   - "帮我写一篇小红书笔记"
   - "生成一篇关于 XX 的笔记"
   - "创作小红书内容"

2. **图片生成请求**
   - "生成小红书封面图"
   - "为这篇笔记配图"

3. **发布相关请求**
   - "发布到小红书"
   - "定时发布小红书笔记"

### 方式 3: 作为 Python 模块导入

如果你想在其他 Python 项目中使用 xiaohongshu-automation 的功能：

```python
import sys
sys.path.append('path/to/xiaohongshu-automation/src')

from config import Config
from xhs_auto import ContentGenerator, ImageGenerator, Publisher

# 创建配置
config = Config()

# 使用功能
generator = ContentGenerator(config)
result = generator.generate_structure("AI写作工具", 600)
```

## Skill 工作原理

### 1. Skill 注册

xiaohongshu-automation 已经安装在全局 skills 目录：

```
~/.claude/skills/xiaohongshu-automation/
```

### 2. Skill 触发机制

Claude Code 通过以下方式识别和使用 Skill：

1. **关键词匹配** - 当对话中出现相关关键词时自动触发
2. **上下文理解** - Claude 理解需要小红书内容创作功能
3. **自动调用** - 无需显式调用，智能识别需求

### 3. Skill 执行流程

```
用户输入
    ↓
Claude Code 识别需求
    ↓
加载 xiaohongshu-automation skill
    ↓
执行相关功能
    ↓
返回结果
    ↓
展示给用户
```

## 配置说明

### 全局配置

Skill 使用全局配置文件（如果存在）：

```env
XHS_API_KEY=your_api_key
XHS_MODEL=doubao-seed-1-8-251228
...
```

### 项目配置

每个项目也可以有自己的配置文件，优先级高于全局配置。

## 使用示例

### 示例 1: 在 Claude Code 中使用

```
用户：帮我写一篇关于 Python 学习的小红书笔记

Claude：好的，我来帮你生成一篇关于 Python 学习的小红书笔记。

[后台自动调用 xiaohongshu-automation]

✅ 标题：Python入门只需这3步，小白也能秒变大神！
✅ 正文：...
✅ 标签：#Python #编程 #学习

用户：好的，帮我生成图片并预览

Claude：正在生成图片...
✅ 封面图已生成
✅ 内容图已生成
正在打开预览...
```

### 示例 2: 作为独立程序使用

```bash
# 交互式模式
python run.py

# 命令行模式
python run.py -t "Python学习" -a "张三" -w 600

# 快速发布
python run.py -t "Python学习" -q
```

### 示例 3: 批量生成

```bash
for topic in "AI写作工具" "Python教程" "效率提升"; do
    python run.py -t "$topic" -g
done
```

## 高级用法

### 自定义配置

```python
# 在代码中自定义配置
from config import Config

config = Config()
config.model = "doubao-pro-4k"
config.default_word_count = 800
```

### 集成到自动化脚本

```bash
# 每天自动生成笔记
0 9 * * * cd /path/to/xiaohongshu-automation && python run.py -t "每日推荐" -q
```

### API 调用

```python
import requests

# 调用 MCP 服务端
response = requests.post(
    'http://your-mcp-server/mcp',
    json={
        'tool': 'publish_content',
        'parameters': {
            'title': '标题',
            'content': '内容',
            'images': ['url1', 'url2'],
            'tags': ['#标签1', '#标签2']
        }
    }
)
```

## 常见问题

### Q: Skill 在 Claude Code 中没有自动触发？

A: 检查以下内容：
1. Skill 是否已安装在 `~/.claude/skills/` 目录
2. SKILL.md 文件是否正确配置
3. 关键词是否匹配

### Q: 如何查看 Skill 是否可用？

A: 在 Claude Code 中询问：
```
用户：我现在可以使用哪些小红书相关的功能？

Claude：你现在可以使用以下小红书功能：
- 智能内容生成
- AI 图片生成
- 交互式预览
- 自动发布
```

### Q: 可以禁用 Skill 吗？

A: 可以，在项目根目录创建 `.claude-ignore` 文件：
```
xiaohongshu-automation
```

## 总结

xiaohongshu-automation 提供了三种使用方式：

1. **独立程序** - 适合直接使用
2. **Claude Code Skill** - 适合在 AI 助手中使用
3. **Python 模块** - 适合集成到其他项目

选择最适合你需求的方式即可！