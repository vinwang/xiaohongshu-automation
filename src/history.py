#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录管理模块
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class HistoryManager:
    """历史记录管理器"""

    def __init__(self, output_dir: str = './output'):
        self.output_dir = output_dir
        self.history_file = os.path.join(output_dir, 'history.json')
        self._ensure_history_file()

    def _ensure_history_file(self):
        """确保历史记录文件存在"""
        if not os.path.exists(self.history_file):
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def add_record(self, data: Dict, status: str = 'success', publish_method: str = 'auto') -> Dict:
        """添加历史记录"""
        record = {
            'id': f"record_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'title': data.get('title', ''),
            'content': data.get('content', ''),
            'tags': data.get('tags', []),
            'images': data.get('images', []),
            'status': status,
            'publish_method': publish_method,
            'word_count': len(data.get('content', ''))
        }

        # 读取现有记录
        records = self._load_records()
        records.insert(0, record)  # 新记录放在前面

        # 保存记录
        self._save_records(records)

        return record

    def update_status(self, record_id: str, status: str, message: str = '') -> bool:
        """更新记录状态"""
        records = self._load_records()

        for record in records:
            if record['id'] == record_id:
                record['status'] = status
                record['status_message'] = message
                record['updated_at'] = datetime.now().isoformat()
                self._save_records(records)
                return True

        return False

    def _load_records(self) -> List[Dict]:
        """加载历史记录"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载历史记录失败: {e}")
            return []

    def _save_records(self, records: List[Dict]):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存历史记录失败: {e}")

    def get_records(self, limit: int = 10, status: Optional[str] = None) -> List[Dict]:
        """获取历史记录"""
        records = self._load_records()

        if status:
            records = [r for r in records if r.get('status') == status]

        return records[:limit]

    def get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """根据ID获取记录"""
        records = self._load_records()

        for record in records:
            if record['id'] == record_id:
                return record

        return None

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        records = self._load_records()

        total = len(records)
        success = len([r for r in records if r.get('status') == 'success'])
        failed = len([r for r in records if r.get('status') == 'failed'])
        pending = len([r for r in records if r.get('status') == 'pending'])

        methods = {}
        for record in records:
            method = record.get('publish_method', 'auto')
            methods[method] = methods.get(method, 0) + 1

        return {
            'total': total,
            'success': success,
            'failed': failed,
            'pending': pending,
            'methods': methods,
            'success_rate': f"{(success / total * 100):.1f}%" if total > 0 else "0%"
        }

    def clear_old_records(self, days: int = 30):
        """清除旧记录"""
        records = self._load_records()
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)

        new_records = []
        for record in records:
            try:
                record_time = datetime.fromisoformat(record['timestamp']).timestamp()
                if record_time > cutoff_date:
                    new_records.append(record)
            except:
                continue

        self._save_records(new_records)
        print(f"✅ 已清除 {len(records) - len(new_records)} 条旧记录")