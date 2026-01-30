"""
图片生成工具
使用火山引擎 API 生成小红书笔记图片
"""

from typing import Dict, Any
from openai import OpenAI
import re
import json
import requests
import time
import os

from mcp.types import Tool

# 工具定义
generate_images_tool = Tool(
    name="xhs_generate_images",
    description="生成小红书笔记图片（封面图和内容图）",
    inputSchema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "笔记标题"
            },
            "content": {
                "type": "string",
                "description": "笔记正文摘要"
            },
            "count": {
                "type": "integer",
                "description": "图片数量（1-4）",
                "default": 3,
                "minimum": 1,
                "maximum": 4
            }
        },
        "required": ["title", "content"]
    }
)

async def handle_generate_images(arguments: Dict[str, Any]) -> Dict:
    """
    处理图片生成请求
    
    Args:
        arguments: 工具参数
        
    Returns:
        生成结果
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
        
        from src.config import Config
        
        config = Config()
        client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        
        title = arguments["title"]
        content = arguments["content"]
        count = arguments.get("count", 3)
        
        # 生成图片提示词
        prompts = await _generate_prompts(client, config, title, content, count)
        
        # 生成图片
        images = []
        
        # 生成封面图
        if prompts["cover"]:
            response = client.images.generate(
                model=config.image_model,
                prompt=prompts["cover"],
                response_format="url",
                size="1728x2304",
                extra_body={"watermark": False},
                timeout=60
            )
            image_url = response.data[0].url
            filepath = await _download_image(image_url, config.output_dir, "cover", 0)
            images.append({
                "type": "cover",
                "url": image_url,
                "path": filepath,
                "description": "封面图"
            })
        
        # 生成内容图
        for i, prompt in enumerate(prompts["content"][:count-1]):
            response = client.images.generate(
                model=config.image_model,
                prompt=prompt,
                response_format="url",
                size="1728x2304",
                extra_body={"watermark": False},
                timeout=60
            )
            image_url = response.data[0].url
            filepath = await _download_image(image_url, config.output_dir, "content", i + 1)
            images.append({
                "type": "content",
                "index": i + 1,
                "url": image_url,
                "path": filepath,
                "description": f"内容图{i+1}"
            })
        
        return {
            "success": True,
            "data": {
                "images": images,
                "count": len(images)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "图片生成失败"
        }

async def _generate_prompts(
    client: OpenAI,
    config,
    title: str,
    content: str,
    count: int
) -> Dict:
    """生成图片提示词"""
    prompt = f"""你是小红书配图专家。

标题：{title}

正文摘要：
{content[:200]}...

请生成：
1. 1条封面图 Prompt（现代简洁风格，突出主题关键词）
2. {count-1}条内容图 Prompt（对应正文观点，可视化关键概念）

生成规则：
- 现代简洁风格，配色协调
- 严禁：水印、logo、emoji、乱码、假字、二维码
- 使用干净的背景，避免杂乱元素
- 图片尺寸：1728x2304（3:4 比例）

只输出严格 JSON：
{{
  "cover": "封面图提示词",
  "content": ["内容图1提示词", "内容图2提示词"]
}}"""
    
    response = client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000,
        timeout=60
    )
    
    content = response.choices[0].message.content
    json_match = re.search(r'\{[\s\S]*\}', content)
    if json_match:
        content = json_match.group()
    
    return json.loads(content)

async def _download_image(
    url: str,
    output_dir: str,
    image_type: str = 'content',
    index: int = 0
) -> str:
    """下载图片到本地"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = int(time.time())
    filename = f"{image_type}_{index}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    return filepath