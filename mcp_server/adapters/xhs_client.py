"""
xhs SDK 适配器
封装 xhs SDK，提供统一的接口
"""

from typing import Dict, List, Optional
import sys
import os

# 尝试导入 xhs SDK
try:
    from xhs import XHSClient
    XHS_AVAILABLE = True
except ImportError:
    XHS_AVAILABLE = False
    XHSClient = None

class XhsClientAdapter:
    """xhs 客户端适配器"""
    
    def __init__(self, cookie: str = None):
        """
        初始化适配器
        
        Args:
            cookie: 小红书 Cookie
        """
        if not XHS_AVAILABLE:
            raise ImportError("xhs SDK 未安装，请运行: pip install xhs")
        
        self.cookie = cookie
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """初始化 xhs 客户端"""
        if self.cookie:
            self._client = XHSClient(cookie=self.cookie)
        else:
            raise ValueError("未提供 Cookie，无法初始化 xhs 客户端")
    
    async def publish_note(
        self,
        title: str,
        content: str,
        images: List[str],
        tags: List[str] = None
    ) -> Dict:
        """
        发布笔记
        
        Args:
            title: 标题
            content: 正文
            images: 图片路径列表
            tags: 标签列表
            
        Returns:
            发布结果
        """
        try:
            # 使用 xhs SDK 发布笔记
            # 注意：这里需要根据 xhs SDK 的实际 API 调整
            result = self._client.create_note(
                title=title,
                desc=content,
                images=images,
                topics=tags or []
            )
            
            return {
                "success": True,
                "note_id": result.get("note_id"),
                "url": result.get("url"),
                "message": "发布成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "发布失败"
            }
    
    async def get_note(self, note_id: str) -> Dict:
        """
        获取笔记详情
        
        Args:
            note_id: 笔记 ID
            
        Returns:
            笔记详情
        """
        try:
            note = self._client.get_note_by_id(note_id)
            return {
                "success": True,
                "data": note
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_notes(self, keyword: str, page: int = 1) -> Dict:
        """
        搜索笔记
        
        Args:
            keyword: 搜索关键词
            page: 页码
            
        Returns:
            搜索结果
        """
        try:
            notes = self._client.search_notes(keyword, page=page)
            return {
                "success": True,
                "data": notes
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }