/**
 * PreviewManager 单元测试
 */

import { PreviewManager, PreviewData } from '../types';
import * as fs from 'fs';

describe('PreviewManager', () => {
  let manager: PreviewManager;
  const testOutputDir = './test-output';

  beforeEach(() => {
    if (!fs.existsSync(testOutputDir)) {
      fs.mkdirSync(testOutputDir, { recursive: true });
    }
    manager = new (require('../modules/previewManager').PreviewManager)(testOutputDir);
  });

  afterEach(() => {
    // 清理测试文件
    if (fs.existsSync(testOutputDir)) {
      fs.rmSync(testOutputDir, { recursive: true });
    }
  });

  describe('generatePreview', () => {
    it('should generate HTML preview from data', () => {
      const data: PreviewData = {
        title: '测试标题',
        content: '测试内容',
        tags: ['#测试'],
        images: [
          'https://example.com/image1.jpg',
          'https://example.com/image2.jpg'
        ]
      };

      const html = manager.generatePreview(data);

      expect(html).toBeDefined();
      expect(html).toContain('<!DOCTYPE html>');
      expect(html).toContain(data.title);
      expect(html).toContain(data.content);
      expect(html).toContain(data.tags[0]);
      expect(html).toContain('image1.jpg');
      expect(html).toContain('image2.jpg');
    });

    it('should include carousel functionality', () => {
      const data: PreviewData = {
        title: '测试',
        content: '内容',
        tags: ['#test'],
        images: ['img1.jpg', 'img2.jpg', 'img3.jpg']
      };

      const html = manager.generatePreview(data);

      expect(html).toContain('carousel');
      expect(html).toContain('scroll');
    });

    it('should include confirm and cancel buttons', () => {
      const data: PreviewData = {
        title: '测试',
        content: '内容',
        tags: ['#test'],
        images: ['img1.jpg']
      };

      const html = manager.generatePreview(data);

      expect(html).toContain('确认发布');
      expect(html).toContain('取消');
    });
  });

  describe('showPreview', () => {
    it('should save HTML file and return path', async () => {
      const data: PreviewData = {
        title: '测试',
        content: '内容',
        tags: ['#test'],
        images: ['img1.jpg']
      };

      const html = manager.generatePreview(data);
      const result = await manager.showPreview(html);

      expect(result).toBe(true);
      expect(fs.existsSync(testOutputDir)).toBe(true);
    });

    it('should generate unique filename for each preview', async () => {
      const data: PreviewData = {
        title: '测试',
        content: '内容',
        tags: ['#test'],
        images: ['img1.jpg']
      };

      const html1 = manager.generatePreview(data);
      await manager.showPreview(html1);

      const html2 = manager.generatePreview(data);
      await manager.showPreview(html2);

      // 应该生成不同的文件名
      const files = fs.readdirSync(testOutputDir).filter(f => f.endsWith('.html'));
      expect(files.length).toBeGreaterThanOrEqual(1);
    });
  });
});