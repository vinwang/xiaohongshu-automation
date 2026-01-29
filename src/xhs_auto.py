#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动化发布工具 - 简化版
单文件版本，无需复杂配置，开箱即用
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import webbrowser
import subprocess

try:
    import requests
    from openai import OpenAI
except ImportError:
    print("❌ 缺少依赖，请安装:")
    print("   pip install requests openai")
    sys.exit(1)

from config import Config


class ContentGenerator:
    """内容生成器"""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    def generate_structure(self, topic: str, word_count: int = 600, context: str = '') -> Dict:
        """生成内容结构"""
        print(f"📝 正在生成内容结构...")

        prompt = f"""你是一位资深的小红书内容创作专家。

【你的任务】
根据用户的内容需求，**严格填充下面的 JSON 结构**，不得输出任何多余文字。

====================
【输入信息】
主题：{topic}
字数：{word_count}
背景：{context}

====================
【标题创作技巧】：
1. 采用二极管标题法：
   - 正面刺激：产品+只需1秒+便可开挂
   - 负面刺激：你不X+绝对会后悔
2. 控制字数在20字以内
3. 生成5个标题，选择1个作为最终标题
4. 生成正文大纲
5. 生成5个标签

**输出格式必须只输出下面 JSON**：
{{
  "titles": ["标题1", "标题2", "标题3", "标题4", "标题5"],
  "final_title": "最终标题",
  "content_outline": ["要点1", "要点2", "要点3"],
  "tags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"]
}}"""

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )

        content = response.choices[0].message.content
        return self._parse_json(content)

    def generate_content(self, structure: Dict) -> Dict:
        """生成完整内容"""
        print(f"📝 正在生成完整内容...")

        prompt = f"""你是一位资深的小红书内容创作专家。

用户需求：
标题：{structure['final_title']}
主题：{structure.get('subject', '')}
大纲：{structure['content_outline']}
背景：{structure.get('context', '')}

## 正文创作规则：
1. 风格匹配：根据主题匹配对应风格
2. 内容要求：结尾设互动，结构清晰，口语化表达，字数50-{structure.get('word_count', 600)}字
3. 严格围绕大纲创作

输出 Markdown：
## 标题
{structure['final_title']}

## 正文
（正文内容）

## 标签
{structure['tags']}"""

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )

        content = response.choices[0].message.content
        return self._parse_markdown(content)

    def _parse_json(self, content: str) -> Dict:
        """解析 JSON"""
        # 移除 markdown 代码块标记
        content = content.replace('```json', '').replace('```', '').strip()
        return json.loads(content)

    def _parse_markdown(self, content: str) -> Dict:
        """解析 Markdown"""
        title = ''
        body = ''
        tags = []

        lines = content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                current_section = line[3:].strip()
            elif current_section == '标题' and not title:
                title = line
            elif current_section == '正文':
                body += line + '\n'
            elif current_section == '标签':
                tags.extend(line.split())

        return {
            'title': title,
            'content': body.strip(),
            'tags': tags
        }


class ImageGenerator:
    """图片生成器"""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    def generate_prompts(self, content: Dict) -> Dict:
        """生成图片提示词"""
        print(f"🎨 正在生成图片提示词...")

        prompt = f"""你是小红书配图专家。

标题：{content['title']}

正文摘要：
{content['content'][:200]}...

请生成：
1. 1条封面图 Prompt（科技风格，浅色背景）
2. 2-3条内容图 Prompt（对应正文观点）

生成规则：
- 科技风格，浅色背景
- 不出现emoji、水印、logo
- 不出现乱码、假字

只输出严格 JSON：
{{
  "cover_image": "封面图提示词",
  "content_images": ["内容图1", "内容图2"],
  "content_images_count": 2
}}"""

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )

        content = response.choices[0].message.content
        return self._parse_json(content)

    def generate_images(self, prompts: Dict) -> List[str]:
        """生成图片"""
        print(f"🎨 正在生成图片...")

        images = []

        # 生成封面图
        if prompts.get('cover_image'):
            print(f"   - 生成封面图...")
            url = self._generate_single_image(prompts['cover_image'])
            images.append(url)

        # 生成内容图
        for i, prompt_text in enumerate(prompts.get('content_images', [])):
            print(f"   - 生成内容图 {i+1}...")
            url = self._generate_single_image(prompt_text)
            images.append(url)

        return images

    def _generate_single_image(self, prompt: str) -> str:
        """生成单张图片"""
        response = self.client.images.generate(
            model=self.config.image_model,
            prompt=prompt,
            response_format="url",
            size="1728x2304"
        )
        return response.data[0].url

    def _parse_json(self, content: str) -> Dict:
        """解析 JSON"""
        content = content.replace('```json', '').replace('```', '').strip()
        return json.loads(content)


class PreviewManager:
    """预览管理器"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_preview(self, data: Dict) -> str:
        """生成 HTML 预览"""
        images_html = '\n'.join([f'<img src="{img}" class="slide-img" />' for img in data['images']])
        tags_html = ' '.join(data['tags'])

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>小红书发布预览</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body {{ margin: 0; padding: 20px; background: #f6f6f6; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", Arial; }}
    .card {{ max-width: 420px; margin: 0 auto; background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 28px rgba(0,0,0,0.08); }}
    .images {{ display: flex; overflow-x: auto; }}
    .images img {{ width: 100%; height: auto; flex-shrink: 0; }}
    .content {{ padding: 16px; }}
    h1 {{ font-size: 18px; margin: 0 0 12px; line-height: 1.4; }}
    .text {{ font-size: 14px; line-height: 1.7; white-space: pre-wrap; color: #333; }}
    .tags {{ margin-top: 12px; color: #999; font-size: 13px; }}
    .status {{ padding: 12px; background: #fafafa; text-align: center; font-size: 13px; color: #666; border-top: 1px solid #eee; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="images">{images_html}</div>
    <div class="content">
      <h1>{data['title']}</h1>
      <div class="text">{data['content']}</div>
      <div class="tags">{tags_html}</div>
    </div>
    <div class="status">预览已完成，请在命令行确认发布</div>
  </div>
</body>
</html>"""

        return html

    def show_preview(self, html: str) -> str:
        """显示预览并返回文件路径"""
        filename = f"preview_{int(time.time())}.html"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        # 在浏览器中打开
        webbrowser.open(f'file://{os.path.abspath(filepath)}')

        return filepath


class Publisher:
    """发布器"""

    def __init__(self, config: Config):
        self.config = config

    def publish(self, data: Dict, scheduled_time: Optional[str] = None):
        """发布内容"""
        print(f"📤 准备发布...")

        if scheduled_time:
            print(f"⏰ 定时发布: {scheduled_time}")
            # 等待到指定时间
            schedule_time = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            wait_seconds = (schedule_time - now).total_seconds()

            if wait_seconds > 0:
                print(f"⏳ 等待 {int(wait_seconds)} 秒...")
                time.sleep(wait_seconds)

        # 模拟发布（实际需要调用小红书 API）
        print(f"📝 标题: {data['title']}")
        print(f"📝 正文: {data['content'][:50]}...")
        print(f"🏷️  标签: {data['tags']}")
        print(f"🖼️  图片: {len(data['images'])} 张")

        # 如果配置了 MCP，尝试使用 MCP
        if self.config.mcp_url:
            try:
                self._publish_via_mcp(data)
            except Exception as e:
                print(f"⚠️  MCP 发布失败: {e}")
                self._publish_simulation(data)
        else:
            self._publish_simulation(data)

    def _publish_via_mcp(self, data: Dict):
        """通过 MCP 发布"""
        print(f"🔗 使用 MCP 服务端发布...")
        response = requests.post(
            self.config.mcp_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "publish_content",
                    "arguments": data
                }
            },
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        print(f"✅ MCP 发布成功")

    def _publish_simulation(self, data: Dict):
        """模拟发布"""
        print(f"✅ 模拟发布成功")
        print(f"💡 提示: 实际发布需要配置小红书 API 或 MCP 服务端")


def main():
    """主函数"""
    print("🚀 小红书自动化发布工具 - 简化版\n")

    # 加载配置
    config = Config('.env')
    if not config.validate():
        sys.exit(1)

    # 获取输入
    if len(sys.argv) > 1:
        # 命令行参数模式
        args = parse_args()
        topic = args.topic
        word_count = args.word_count
        context = args.context or ''
        quick = args.quick
    else:
        # 交互式模式
        topic = input("请输入主题: ").strip()
        word_count = int(input("请输入字数 (默认600): ").strip() or "600")
        context = input("请输入背景说明 (可选): ").strip()
        quick = input("是否快速发布（跳过预览）？(y/n, 默认n): ").strip().lower() == 'y'

    print(f"\n📋 主题: {topic}")
    print(f"📋 字数: {word_count}")
    print(f"📋 背景: {context if context else '无'}\n")

    try:
        # 生成内容
        generator = ContentGenerator(config)
        structure = generator.generate_structure(topic, word_count, context)
        structure['subject'] = topic
        structure['context'] = context
        structure['word_count'] = word_count

        content = generator.generate_content(structure)

        print(f"✅ 标题: {content['title']}")
        print(f"✅ 标签: {content['tags']}\n")

        # 生成图片
        image_gen = ImageGenerator(config)
        prompts = image_gen.generate_prompts(content)
        images = image_gen.generate_images(prompts)

        print(f"✅ 图片生成完成，共 {len(images)} 张\n")

        # 预览
        if not quick:
            preview_mgr = PreviewManager(config.output_dir)
            html = preview_mgr.generate_preview({
                'title': content['title'],
                'content': content['content'],
                'tags': content['tags'],
                'images': images
            })

            filepath = preview_mgr.show_preview(html)
            print(f"👀 预览已打开: {filepath}")

            confirm = input("\n确认发布吗？(y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消发布")
                return

            scheduled = input("是否定时发布？(y/n, 默认n): ").strip().lower()
            scheduled_time = None
            if scheduled == 'y':
                scheduled_time = input("请输入发布时间 (格式: YYYY-MM-DD HH:MM:SS): ").strip()
        else:
            scheduled_time = None

        # 发布
        publisher = Publisher(config)
        publisher.publish({
            'title': content['title'],
            'content': content['content'],
            'tags': content['tags'],
            'images': images
        }, scheduled_time)

        print(f"\n🎉 发布流程完成！")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def parse_args():
    """解析命令行参数"""
    import argparse
    parser = argparse.ArgumentParser(description='小红书自动化发布工具')
    parser.add_argument('-t', '--topic', help='主题/选题')
    parser.add_argument('-w', '--word-count', type=int, default=600, help='字数')
    parser.add_argument('-c', '--context', help='背景说明')
    parser.add_argument('-q', '--quick', action='store_true', help='快速发布（跳过预览）')
    return parser.parse_args()


if __name__ == '__main__':
    main()