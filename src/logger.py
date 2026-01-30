#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块
"""

import os
import sys
from datetime import datetime
from typing import Optional


class Logger:
    """日志管理器"""

    def __init__(self, output_dir: str = './output', log_to_file: bool = True):
        self.output_dir = output_dir
        self.log_to_file = log_to_file
        self.log_file = os.path.join(output_dir, 'app.log')
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if self.log_to_file:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def _write_to_file(self, message: str):
        """写入日志文件"""
        if not self.log_to_file:
            return

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except Exception as e:
            print(f"⚠️  写入日志文件失败: {e}")

    def info(self, message: str):
        """信息日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[INFO] {timestamp} - {message}"
        self._write_to_file(log_message)

    def success(self, message: str):
        """成功日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[SUCCESS] {timestamp} - {message}"
        self._write_to_file(log_message)

    def warning(self, message: str):
        """警告日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[WARNING] {timestamp} - {message}"
        self._write_to_file(log_message)

    def error(self, message: str):
        """错误日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[ERROR] {timestamp} - {message}"
        self._write_to_file(log_message)

    def debug(self, message: str):
        """调试日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[DEBUG] {timestamp} - {message}"
        self._write_to_file(log_message)

    def step(self, step_num: int, total_steps: int, message: str):
        """步骤日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[STEP {step_num}/{total_steps}] {timestamp} - {message}"
        self._write_to_file(log_message)

    def clear_logs(self):
        """清空日志文件"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                print(f"✅ 日志文件已清空")
            except Exception as e:
                print(f"⚠️  清空日志文件失败: {e}")
