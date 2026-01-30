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
import re
from history import HistoryManager
from logger import Logger


def parse_json(content: str) -> Dict:
    """共享的 JSON 解析函数，包含错误处理和正则提取"""
    try:
        # 移除 markdown 代码块标记
        content = content.replace('```json', '').replace('```', '').strip()

        # 尝试提取 JSON（处理可能的额外文本）
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group()

        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        print(f"原始内容: {content[:200]}...")
        raise ValueError("AI 返回的内容格式不正确，请重试") from e

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
            max_tokens=1000,
            timeout=self.config.api_timeout
        )

        content = response.choices[0].message.content
        return parse_json(content)

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
            max_tokens=2000,
            timeout=self.config.api_timeout
        )

        content = response.choices[0].message.content
        result = self._parse_markdown(content)

        # 调用 humanizer-zh skill 优化内容
        if result.get('content'):
            print(f"🔄 正在优化内容，使其更自然...")
            result['content'] = self._humanize_content(result['content'], structure['final_title'])

        return result

    def _humanize_content(self, content: str, title: str) -> str:
        """使用 humanizer-zh skill 优化内容"""
        try:
            # 构建 humanizer-zh 的请求
            humanizer_prompt = f"""请帮我优化以下小红书笔记内容，使其更自然、更人性化，减少 AI 痕迹：

标题：{title}

正文：
{content}

要求：
1. 保持原有的核心信息和结构
2. 使用更口语化、自然的表达方式
3. 添加适当的语气词和情感表达
4. 避免过于正式或机械的表述
5. 保持小红书平台的风格特点
6. 不要改变字数太多

请直接返回优化后的正文内容，不要添加其他说明。"""

            # 调用 AI 进行人性化优化
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": humanizer_prompt}],
                temperature=0.8,  # 稍高的温度以增加创造性
                max_tokens=2000,
                timeout=self.config.api_timeout
            )

            optimized_content = response.choices[0].message.content.strip()

            # 移除可能的 markdown 标记
            optimized_content = optimized_content.replace('```', '').strip()

            print(f"✅ 内容优化完成")
            return optimized_content

        except Exception as e:
            print(f"⚠️  内容优化失败，使用原始内容: {e}")
            return content

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
1. 1条封面图 Prompt（现代简洁风格，突出主题关键词）
2. 2-3条内容图 Prompt（对应正文观点，可视化关键概念）

生成规则：
- 现代简洁风格，配色协调
- 封面图：必须包含主题关键词的视觉化表达（如图标、符号、抽象图形）
- 内容图：配合正文观点，使用清晰的视觉元素
- 严禁：水印、logo、emoji、乱码、假字、二维码
- 严禁：任何形式的品牌标识或推广文字
- 使用干净的背景，避免杂乱元素
- 图片尺寸：1728x2304（3:4 比例）

只输出严格 JSON：
{{
  "cover_image": "封面图提示词，包含主题关键词的视觉元素",
  "content_images": ["内容图1提示词", "内容图2提示词"],
  "content_images_count": 2
}}"""

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            timeout=self.config.api_timeout
        )

        content = response.choices[0].message.content
        return parse_json(content)

    def generate_images(self, prompts: Dict) -> List[str]:
        """生成图片"""
        print(f"🎨 正在生成图片...")

        images = []

        # 生成封面图
        if prompts.get('cover_image'):
            print(f"   - 生成封面图...")
            filepath = self._generate_single_image(prompts['cover_image'], 'cover', 0)
            images.append(filepath)

        # 生成内容图
        for i, prompt_text in enumerate(prompts.get('content_images', [])):
            print(f"   - 生成内容图 {i+1}...")
            filepath = self._generate_single_image(prompt_text, 'content', i + 1)
            images.append(filepath)

        return images

    def _generate_single_image(self, prompt: str, image_type: str = 'content', index: int = 0) -> str:
        """生成单张图片并下载到本地"""
        # 构建增强的 prompt，使用明确的否定语言来避免水印等元素
        enhanced_prompt = f"""{prompt}

重要要求：
1. 必须创建纯净的图像，不要添加任何水印、logo、文字、品牌标识或签名
2. 不要包含任何中文字符、英文字母、数字或符号
3. 不要添加 emoji 表情符号或二维码
4. 避免模糊、噪点或任何视觉伪影
5. 使用清晰的视觉元素来表达主题，而不是文字

视觉风格：
- 现代简洁的设计风格
- 色彩协调，饱和度适中
- 良好的光影效果和对比度
- 专业摄影或高质量设计风格
- 保持画面干净整洁，无多余元素"""

        response = self.client.images.generate(
            model=self.config.image_model,
            prompt=enhanced_prompt,
            response_format="url",
            size="1728x2304",
            extra_body={
                "watermark": False
            },
            timeout=self.config.api_timeout
        )

        image_url = response.data[0].url

        # 下载图片到本地
        return ImageDownloader.download(
            image_url,
            self.config.output_dir,
            image_type,
            index
        )


class ImageDownloader:
    """图片下载器"""

    @staticmethod
    def download(url: str, output_dir: str, image_type: str = 'content', index: int = 0) -> str:
        """下载图片到本地"""
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            # 生成文件名
            timestamp = int(time.time())
            filename = f"{image_type}_{index}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)

            # 下载图片
            print(f"   📥 下载图片: {filename}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # 验证图片
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                raise ValueError(f"下载的不是图片: {content_type}")

            # 保存图片
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # 验证文件大小
            file_size = os.path.getsize(filepath)
            if file_size < 1024:  # 小于1KB可能是错误图片
                raise ValueError(f"图片过小: {file_size} bytes")

            print(f"   ✅ 图片保存成功: {filepath}")
            return filepath

        except requests.exceptions.Timeout:
            raise ValueError("图片下载超时")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"图片下载失败: {e}")
        except Exception as e:
            raise ValueError(f"图片处理失败: {e}")


class PreviewManager:
    """预览管理器"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_preview(self, data: Dict) -> str:
        """生成 HTML 预览"""
        # 生成本地图片路径
        images_html = ''
        for i, img in enumerate(data['images']):
            # 将本地路径转换为file://协议
            abs_path = os.path.abspath(img)
            file_url = f'file:///{abs_path.replace("\\", "/")}'
            images_html += f'<img src="{file_url}" class="slide-img" data-index="{i}" />'

        tags_html = ' '.join(data['tags'])

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>小红书发布预览</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 20px;
      background: #f6f6f6;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
      min-height: 100vh;
    }}
    .container {{
      max-width: 480px;
      margin: 0 auto;
    }}
    .card {{
      background: #fff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }}
    .images-container {{
      position: relative;
      background: #f0f0f0;
    }}
    .images {{
      display: flex;
      overflow-x: auto;
      scroll-snap-type: x mandatory;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }}
    .images::-webkit-scrollbar {{
      display: none;
    }}
    .images img {{
      width: 100%;
      height: auto;
      flex-shrink: 0;
      scroll-snap-align: start;
      object-fit: cover;
      aspect-ratio: 3/4;
    }}
    .image-counter {{
      position: absolute;
      bottom: 12px;
      right: 12px;
      background: rgba(0,0,0,0.6);
      color: #fff;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
    }}
    .dots {{
      display: flex;
      justify-content: center;
      gap: 6px;
      padding: 10px;
      background: #fff;
    }}
    .dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #ddd;
      cursor: pointer;
      transition: all 0.3s ease;
    }}
    .dot.active {{
      background: #ff2442;
      transform: scale(1.2);
    }}
    .content {{
      padding: 16px;
    }}
    h1 {{
      font-size: 17px;
      font-weight: 600;
      margin: 0 0 12px;
      line-height: 1.4;
      color: #333;
    }}
    .text {{
      font-size: 15px;
      line-height: 1.7;
      white-space: pre-wrap;
      color: #333;
      margin-bottom: 12px;
    }}
    .tags {{
      margin-top: 12px;
      color: #ff2442;
      font-size: 14px;
      word-break: break-all;
    }}
    .status {{
      padding: 16px;
      background: #fafafa;
      text-align: center;
      font-size: 14px;
      color: #666;
      border-top: 1px solid #eee;
    }}
    .btn-group {{
      display: flex;
      gap: 10px;
      margin-top: 10px;
    }}
    .btn {{
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s ease;
    }}
    .btn-primary {{
      background: #ff2442;
      color: #fff;
    }}
    .btn-primary:hover {{
      background: #e01f3a;
    }}
    .btn-secondary {{
      background: #f0f0f0;
      color: #666;
    }}
    .btn-secondary:hover {{
      background: #e0e0e0;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div class="images-container">
        <div class="images" id="imageSlider">{images_html}</div>
        <div class="image-counter" id="imageCounter">1/{len(data['images'])}</div>
      </div>
      <div class="dots" id="dots"></div>
      <div class="content">
        <h1>{data['title']}</h1>
        <div class="text">{data['content']}</div>
        <div class="tags">{tags_html}</div>
      </div>
      <div class="status">
        <div>预览已完成，请在命令行确认发布</div>
        <div class="btn-group">
          <button class="btn btn-secondary" onclick="window.location.reload()">重新生成</button>
          <button class="btn btn-primary" onclick="confirmPublish()">确认发布</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    const slider = document.getElementById('imageSlider');
    const dotsContainer = document.getElementById('dots');
    const counter = document.getElementById('imageCounter');
    const images = slider.querySelectorAll('img');
    let currentIndex = 0;

    // 创建指示点
    images.forEach((_, index) => {{
      const dot = document.createElement('div');
      dot.className = 'dot' + (index === 0 ? ' active' : '');
      dot.addEventListener('click', () => {{
        slider.scrollTo({{ left: index * slider.offsetWidth, behavior: 'smooth' }});
      }});
      dotsContainer.appendChild(dot);
    }});

    // 更新当前图片索引
    slider.addEventListener('scroll', () => {{
      currentIndex = Math.round(slider.scrollLeft / slider.offsetWidth);
      updateDots();
      updateCounter();
    }});

    function updateDots() {{
      const dots = dotsContainer.querySelectorAll('.dot');
      dots.forEach((dot, index) => {{
        dot.classList.toggle('active', index === currentIndex);
      }});
    }}

    function updateCounter() {{
      counter.textContent = `${{currentIndex + 1}}/${{images.length}}`;
    }}

    function confirmPublish() {{
      console.log('CONFIRM_PUBLISH');
    }}
  </script>
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

    def publish(self, data: Dict, scheduled_time: Optional[str] = None, publish_method: str = 'auto'):
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

        # 根据发布方式选择发布方法
        if publish_method == 'browser':
            try:
                self._publish_via_browser(data)
            except Exception as e:
                print(f"⚠️  浏览器发布失败: {e}")
                print(f"💡 请检查是否安装了 playwright: pip install playwright && playwright install")
                self._publish_simulation(data)
        elif self.config.mcp_url:
            try:
                self._publish_via_mcp(data)
            except Exception as e:
                print(f"⚠️  MCP 发布失败: {e}")
                self._publish_simulation(data)
        else:
            self._publish_simulation(data)

    def _publish_via_mcp(self, data: Dict, max_retries: int = 3) -> bool:
        """通过 MCP 发布"""
        print(f"🔗 使用 MCP 服务端发布...")

        for attempt in range(max_retries):
            try:
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
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                response.raise_for_status()

                # 验证响应
                result = response.json()
                if result.get('error'):
                    raise ValueError(f"MCP 错误: {result['error']}")

                print(f"✅ MCP 发布成功")
                return True

            except requests.exceptions.Timeout:
                print(f"⚠️  MCP 请求超时，尝试 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

            except requests.exceptions.ConnectionError:
                print(f"⚠️  MCP 连接失败，尝试 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

            except requests.exceptions.HTTPError as e:
                print(f"❌ MCP HTTP 错误: {e}")
                return False

            except Exception as e:
                print(f"❌ MCP 发布失败: {e}")
                return False

        print(f"❌ MCP 发布失败，已重试 {max_retries} 次")
        return False

    def _publish_simulation(self, data: Dict):
        """模拟发布"""
        print(f"✅ 模拟发布成功")
        print(f"💡 提示: 实际发布需要配置小红书 API 或 MCP 服务端")


class XHSBrowserPublisher:
    """小红书浏览器自动发布器"""

    def __init__(self, config: Config):
        self.config = config

    def publish(self, data: Dict, headless: bool = False):
        """使用浏览器自动操作发布到小红书"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError("请先安装 playwright: pip install playwright && playwright install")

        print(f"🌐 启动浏览器自动操作...")

        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            context = browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = context.new_page()

            try:
                # 访问小红书发布页面
                print(f"📱 打开小红书发布页面...")
                page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=30000)

                # 等待页面加载
                page.wait_for_load_state('networkidle')

                # 检查是否需要登录
                if self._need_login(page):
                    print(f"🔐 检测到需要登录")
                    print(f"💡 请在浏览器中完成登录...")
                    print(f"⏳ 等待登录完成...")

                    # 等待用户手动登录（最多等待120秒）
                    for i in range(120):
                        time.sleep(1)
                        if not self._need_login(page):
                            print(f"✅ 登录成功")
                            break
                        if i % 10 == 0 and i > 0:
                            print(f"⏳ 等待登录中... ({i}/120秒)")
                    else:
                        raise TimeoutError("登录超时，请重新运行程序")

                # 上传图片
                print(f"🖼️  开始上传图片 ({len(data['images'])} 张)...")
                self._upload_images(page, data['images'])

                # 输入标题
                print(f"📝 输入标题...")
                self._input_title(page, data['title'])

                # 输入正文
                print(f"📝 输入正文...")
                self._input_content(page, data['content'], data['tags'])

                # 等待确认
                print(f"✅ 内容已填写完成，请在浏览器中检查")
                print(f"💡 请在浏览器中点击发布按钮完成发布")
                print(f"⏳ 等待30秒后自动关闭浏览器...")

                # 等待30秒让用户检查和发布
                time.sleep(30)

                print(f"✅ 浏览器发布流程完成")

            except Exception as e:
                print(f"❌ 浏览器操作失败: {e}")
                raise

            finally:
                browser.close()

    def _need_login(self, page) -> bool:
        """检查是否需要登录"""
        try:
            # 检查是否存在登录按钮或登录相关元素
            login_selectors = [
                'text=登录',
                'text=扫码登录',
                'text=账号密码登录',
                '.login-btn',
                '[class*="login"]'
            ]

            for selector in login_selectors:
                if page.locator(selector).count() > 0:
                    return True

            return False

        except Exception:
            return False

    def _upload_images(self, page, image_paths: List[str]):
        """上传图片"""
        try:
            # 查找上传按钮（可能的选择器）
            upload_selectors = [
                'input[type="file"]',
                '[class*="upload"]',
                '[class*="image-upload"]',
                'text=上传图片'
            ]

            file_input = None
            for selector in upload_selectors:
                try:
                    file_input = page.locator(selector).first
                    if file_input.count() > 0:
                        break
                except:
                    continue

            if not file_input:
                raise Exception("未找到上传按钮，请手动上传图片")

            # 上传所有图片
            file_input.set_input_files(image_paths)

            # 等待上传完成
            time.sleep(3)

            print(f"✅ 图片上传完成")

        except Exception as e:
            print(f"⚠️  图片上传失败: {e}")
            print(f"💡 请在浏览器中手动上传图片")

    def _input_title(self, page, title: str):
        """输入标题"""
        try:
            # 查找标题输入框
            title_selectors = [
                'input[placeholder*="标题"]',
                'input[placeholder*="填写标题"]',
                '[class*="title"] input',
                '[class*="title-input"]'
            ]

            title_input = None
            for selector in title_selectors:
                try:
                    title_input = page.locator(selector).first
                    if title_input.count() > 0:
                        break
                except:
                    continue

            if title_input:
                title_input.fill(title)
                print(f"✅ 标题已输入")
            else:
                print(f"⚠️  未找到标题输入框，请手动输入")

        except Exception as e:
            print(f"⚠️  标题输入失败: {e}")
            print(f"💡 请在浏览器中手动输入标题")

    def _input_content(self, page, content: str, tags: List[str]):
        """输入正文和标签"""
        try:
            # 查找正文输入框
            content_selectors = [
                'textarea[placeholder*="正文"]',
                'textarea[placeholder*="填写正文"]',
                '[class*="content"] textarea',
                '[class*="content-input"]',
                'div[contenteditable="true"]'
            ]

            content_input = None
            for selector in content_selectors:
                try:
                    content_input = page.locator(selector).first
                    if content_input.count() > 0:
                        break
                except:
                    continue

            if content_input:
                # 组合正文和标签
                full_content = f"{content}\n\n{' '.join(tags)}"
                content_input.fill(full_content)
                print(f"✅ 正文和标签已输入")
            else:
                print(f"⚠️  未找到正文输入框，请手动输入")

        except Exception as e:
            print(f"⚠️  正文输入失败: {e}")
            print(f"💡 请在浏览器中手动输入正文和标签")


def main():
    """主函数"""
    print("🚀 小红书自动化发布工具 - 简化版\n")

    # 加载配置
    config = Config('.env')
    if not config.validate():
        sys.exit(1)

    # 初始化历史记录和日志
    history_mgr = HistoryManager(config.output_dir)
    logger = Logger(config.output_dir)

    logger.info("程序启动")

    # 获取输入
    if len(sys.argv) > 1:
        # 命令行参数模式
        args = parse_args()
        topic = args.topic
        word_count = args.word_count
        context = args.context or ''
        quick = args.quick
        publish_method = args.publish_method
    else:
        # 交互式模式
        topic = input("请输入主题: ").strip()
        word_count = int(input("请输入字数 (默认600): ").strip() or "600")
        context = input("请输入背景说明 (可选): ").strip()
        quick = input("是否快速发布（跳过预览）？(y/n, 默认n): ").strip().lower() == 'y'
        publish_method = input("发布方式 (auto/mcp/browser, 默认auto): ").strip().lower() or 'auto'

    print(f"\n📋 主题: {topic}")
    print(f"📋 字数: {word_count}")
    print(f"📋 背景: {context if context else '无'}")
    print(f"📋 发布方式: {publish_method}\n")

    logger.info(f"开始生成内容 - 主题: {topic}")

    try:
        # 生成内容
        logger.step(1, 5, "生成内容结构")
        generator = ContentGenerator(config)
        structure = generator.generate_structure(topic, word_count, context)
        structure['subject'] = topic
        structure['context'] = context
        structure['word_count'] = word_count

        logger.step(2, 5, "生成完整内容")
        content = generator.generate_content(structure)

        print(f"✅ 标题: {content['title']}")
        print(f"✅ 标签: {content['tags']}\n")
        logger.success(f"内容生成完成 - 标题: {content['title']}")

        # 生成图片
        logger.step(3, 5, "生成图片提示词")
        image_gen = ImageGenerator(config)
        prompts = image_gen.generate_prompts(content)

        logger.step(4, 5, "生成图片")
        images = image_gen.generate_images(prompts)

        print(f"✅ 图片生成完成，共 {len(images)} 张\n")
        logger.success(f"图片生成完成 - 共 {len(images)} 张")

        # 预览
        if not quick:
            logger.step(5, 5, "生成预览")
            preview_mgr = PreviewManager(config.output_dir)
            html = preview_mgr.generate_preview({
                'title': content['title'],
                'content': content['content'],
                'tags': content['tags'],
                'images': images
            })

            filepath = preview_mgr.show_preview(html)
            print(f"👀 预览已打开: {filepath}")
            logger.info(f"预览已生成: {filepath}")

            confirm = input("\n确认发布吗？(y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消发布")
                logger.warning("用户取消发布")
                # 记录取消的历史
                history_mgr.add_record({
                    'title': content['title'],
                    'content': content['content'],
                    'tags': content['tags'],
                    'images': images
                }, status='cancelled', publish_method=publish_method)
                return

            scheduled = input("是否定时发布？(y/n, 默认n): ").strip().lower()
            scheduled_time = None
            if scheduled == 'y':
                scheduled_time = input("请输入发布时间 (格式: YYYY-MM-DD HH:MM:SS): ").strip()
        else:
            scheduled_time = None

        # 发布
        print(f"\n📤 开始发布...")
        logger.info(f"开始发布 - 方式: {publish_method}")

        publish_data = {
            'title': content['title'],
            'content': content['content'],
            'tags': content['tags'],
            'images': images
        }

        # 添加待发布记录
        record_id = history_mgr.add_record(publish_data, status='pending', publish_method=publish_method)

        try:
            if publish_method == 'browser':
                browser_publisher = XHSBrowserPublisher(config)
                browser_publisher.publish(publish_data)
            else:
                publisher = Publisher(config)
                publisher.publish(publish_data, scheduled_time, publish_method)

            # 更新记录状态为成功
            history_mgr.update_status(record_id, 'success')
            logger.success(f"发布成功 - 记录ID: {record_id}")
            print(f"\n🎉 发布流程完成！")

        except Exception as publish_error:
            # 更新记录状态为失败
            history_mgr.update_status(record_id, 'failed', str(publish_error))
            logger.error(f"发布失败 - {publish_error}")
            raise publish_error

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        logger.error(f"程序异常 - {e}")
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
    parser.add_argument('-m', '--publish-method', default='auto', choices=['auto', 'mcp', 'browser'],
                       help='发布方式 (auto/mcp/browser)')
    return parser.parse_args()


if __name__ == '__main__':
    main()