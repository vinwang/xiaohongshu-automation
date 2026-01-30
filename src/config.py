#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
支持 .env 文件和环境变量
"""

import os
import getpass
from typing import Dict, Optional
from pathlib import Path


class Config:
    """配置管理"""

    def __init__(self, env_file: str = '.env'):
        self.env_file = env_file
        self._load_env()

    def _load_env(self):
        """加载 .env 文件"""
        env_path = Path(self.env_file)
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # 跳过注释和空行
                        if not line or line.startswith('#'):
                            continue
                        # 解析 key=value
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # 只设置未设置的环境变量
                            if key not in os.environ:
                                os.environ[key] = value
                print(f"✅ 已加载配置文件: {self.env_file}")
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")
        else:
            print(f"⚠️  配置文件不存在: {self.env_file}")

    @property
    def api_key(self) -> str:
        return os.getenv('XHS_API_KEY', '')

    @property
    def model(self) -> str:
        return os.getenv('XHS_MODEL', 'doubao-seed-1-8-251228')

    @property
    def base_url(self) -> str:
        return os.getenv('XHS_API_ENDPOINT', 'https://ark.cn-beijing.volces.com/api/v3')

    @property
    def image_model(self) -> str:
        return os.getenv('XHS_IMAGE_MODEL', 'doubao-seedream-4-5-251128')

    @property
    def mcp_url(self) -> str:
        return os.getenv('XHS_MCP_URL', '')

    @property
    def mcp_tool(self) -> str:
        return os.getenv('XHS_MCP_TOOL', 'publish_content')

    @property
    def default_account(self) -> str:
        return os.getenv('XHS_DEFAULT_ACCOUNT', '你的账号')

    @property
    def default_word_count(self) -> int:
        return int(os.getenv('XHS_DEFAULT_WORD_COUNT', '500'))

    @property
    def output_dir(self) -> str:
        return os.getenv('XHS_OUTPUT_DIR', './output')

    @property
    def api_timeout(self) -> int:
        return int(os.getenv('XHS_API_TIMEOUT', '60'))

    def validate(self) -> bool:
        """验证配置，返回是否成功"""
        if not self.api_key:
            print("⚠️  未配置火山引擎 API Key")
            print("💡 配置方式:")
            print("   1. 编辑 .env 文件，设置 XHS_API_KEY")
            print("   2. 设置环境变量 XHS_API_KEY")

            # 使用 getpass 隐藏输入
            self.api_key_input = getpass.getpass("请输入火山引擎 API Key: ").strip()
            if not self.api_key_input:
                print("❌ API Key 不能为空")
                return False

            # 验证 API Key 格式（示例：火山引擎 API Key 通常至少 16 个字符）
            if len(self.api_key_input) < 16:
                print("❌ API Key 格式不正确（至少需要 16 个字符）")
                return False

            # 临时保存
            os.environ['XHS_API_KEY'] = self.api_key_input
            # 清空明文变量
            self.api_key_input = None

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        return True

    def to_dict(self) -> Dict:
        """返回配置字典"""
        return {
            'api_key': self.api_key,
            'api_endpoint': self.base_url,
            'model_text': self.model,
            'model_image': self.image_model,
            'mcp_url': self.mcp_url,
            'mcp_tool': self.mcp_tool,
            'default_account': self.default_account,
            'default_word_count': self.default_word_count,
            'output_dir': self.output_dir
        }