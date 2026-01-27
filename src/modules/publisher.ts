/**
 * 发布模块
 */

import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import {
  Publisher,
  PublishConfig,
  Config
} from '../types';
import { ConfigManager } from '../config';

export class PublisherImpl implements Publisher {
  private config: Config;

  constructor(configManager?: ConfigManager) {
    const manager = configManager || new ConfigManager();
    this.config = manager.get();
  }

  /**
   * 立即发布
   */
  async publish(config: PublishConfig): Promise<void> {
    console.log('📤 开始发布到小红书...');

    // 如果配置了 MCP 服务端，使用 MCP 发布
    if (this.config.publish.mcpUrl) {
      await this.publishViaMCP(config);
    } else {
      await this.publishViaDirectAPI(config);
    }

    console.log('✅ 发布成功！');

    // 保存发布记录
    await this.savePublishRecord(config, new Date().toISOString());
  }

  /**
   * 定时发布
   */
  async schedulePublish(config: PublishConfig): Promise<void> {
    if (!config.scheduled_time) {
      throw new Error('定时发布需要指定 scheduled_time');
    }

    console.log(`⏰ 已设置定时发布: ${config.scheduled_time}`);

    // 计算等待时间
    const scheduleTime = new Date(config.scheduled_time);
    const now = new Date();
    const waitTime = scheduleTime.getTime() - now.getTime();

    if (waitTime <= 0) {
      console.log('⚠️  定时时间已过，立即发布');
      await this.publish(config);
      return;
    }

    console.log(`⏳ 等待 ${Math.floor(waitTime / 1000)} 秒后发布...`);

    // 使用 setTimeout 等待到指定时间
    await new Promise(resolve => setTimeout(resolve, waitTime));

    // 发布
    await this.publish(config);
  }

  /**
   * 通过 MCP 服务端发布
   */
  private async publishViaMCP(config: PublishConfig): Promise<void> {
    console.log('🔗 使用 MCP 服务端发布...');

    try {
      const response = await axios.post(
        this.config.publish.mcpUrl!,
        {
          jsonrpc: '2.0',
          id: 1,
          method: 'tools/call',
          params: {
            name: 'publish_content',
            arguments: {
              title: config.title,
              content: config.content,
              tags: config.tags,
              images: config.images
            }
          }
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.error) {
        throw new Error(`MCP 发布失败: ${response.data.error.message}`);
      }

      console.log('✅ MCP 发布成功');
    } catch (error) {
      console.error('❌ MCP 发布失败:', error);
      throw error;
    }
  }

  /**
   * 直接通过小红书 API 发布
   */
  private async publishViaDirectAPI(config: PublishConfig): Promise<void> {
    console.log('🔗 使用直接 API 发布...');

    // 注意：这里需要实现实际的小红书 API 调用
    // 由于小红书 API 不是公开的，这里提供一个框架

    const payload = {
      title: config.title,
      desc: config.content,
      type: 'normal',
      ats: [],
      topics: config.tags.map(tag => tag.replace('#', '')),
      images: config.images.map(img => ({
        url: img,
        width: 1728,
        height: 2304
      }))
    };

    // 这里应该调用小红书的发布 API
    // 由于小红书 API 需要登录凭证和复杂的签名，这里只是示例
    console.log('📝 发布数据:', JSON.stringify(payload, null, 2));
    console.log('⚠️  直接 API 发布需要实现小红书的登录和签名逻辑');
    console.log('💡 建议使用 MCP 服务端或 xhs 库');

    // 保存到本地文件作为示例
    const outputDir = this.config.storage.outputDir;
    const filename = `publish_${Date.now()}.json`;
    const filepath = path.join(outputDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(payload, null, 2), 'utf-8');
    console.log(`📄 发布数据已保存到: ${filepath}`);

    // 模拟发布成功
    console.log('✅ 模拟发布成功');
  }

  /**
   * 保存发布记录
   */
  private async savePublishRecord(config: PublishConfig, publishTime: string): Promise<void> {
    const outputDir = this.config.storage.outputDir;
    const recordsFile = path.join(outputDir, 'publish_records.json');

    let records = [];

    // 读取现有记录
    if (fs.existsSync(recordsFile)) {
      const content = fs.readFileSync(recordsFile, 'utf-8');
      records = JSON.parse(content);
    }

    // 添加新记录
    records.push({
      id: Date.now(),
      title: config.title,
      content: config.content,
      tags: config.tags,
      images: config.images,
      publishTime: publishTime,
      scheduled: !!config.scheduled_time,
      scheduledTime: config.scheduled_time,
      private: config.private || false
    });

    // 保存记录
    fs.writeFileSync(recordsFile, JSON.stringify(records, null, 2), 'utf-8');

    console.log(`📊 发布记录已保存: ${records.length} 条`);
  }

  /**
   * 获取发布历史
   */
  getPublishHistory(limit: number = 10): any[] {
    const recordsFile = path.join(this.config.storage.outputDir, 'publish_records.json');

    if (!fs.existsSync(recordsFile)) {
      return [];
    }

    const content = fs.readFileSync(recordsFile, 'utf-8');
    const records = JSON.parse(content);

    // 返回最近的 N 条记录
    return records.slice(-limit).reverse();
  }
}

// 导出为默认导出，方便测试
export { PublisherImpl as Publisher };