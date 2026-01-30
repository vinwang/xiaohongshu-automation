"""
内容生成工具
使用火山引擎 API 生成小红书笔记内容
"""

from typing import Dict, Any
from openai import OpenAI
import re
import json

from mcp.types import Tool

# 工具定义
generate_content_tool = Tool(
    name="xhs_generate_content",
    description="生成小红书笔记内容（标题、正文、标签）",
    inputSchema={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "笔记主题"
            },
            "word_count": {
                "type": "integer",
                "description": "正文字数",
                "default": 600
            },
            "context": {
                "type": "string",
                "description": "背景说明（可选）"
            },
            "style": {
                "type": "string",
                "description": "内容风格",
                "enum": ["生活", "职场", "情感", "促销"],
                "default": "职场"
            }
        },
        "required": ["topic"]
    }
)

async def handle_generate_content(arguments: Dict[str, Any]) -> Dict:
    """
    处理内容生成请求
    
    Args:
        arguments: 工具参数
        
    Returns:
        生成结果
    """
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
        
        from src.config import Config
        
        config = Config()
        client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        
        topic = arguments["topic"]
        word_count = arguments.get("word_count", 600)
        context = arguments.get("context", "")
        style = arguments.get("style", "职场")
        
        # 构建提示词
        prompt = f"""你是一位资深的小红书内容创作专家。

根据以下要求生成小红书笔记内容：

主题：{topic}
字数：{word_count}字
背景：{context}
风格：{style}

## 要求：
1. 使用二极管标题法（字数<20字，包含数字）
2. 开篇有钩子（痛点引入）
3. 包含实际案例或数据
4. 结尾有互动引导
5. 标签5-10个
6. 口语化表达

## 输出格式（JSON）：
{{
  "title": "标题",
  "content": "正文内容",
  "tags": ["#标签1", "#标签2", ...]
}}

只输出 JSON，不要其他内容。"""

        response = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
            timeout=60
        )
        
        content = response.choices[0].message.content
        
        # 解析 JSON
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group()
        
        result = json.loads(content)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "内容生成失败"
        }