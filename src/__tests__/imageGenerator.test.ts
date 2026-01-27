/**
 * ImageGenerator 单元测试
 */

import { ImageGenerator, XHSContent, ImageConfig } from '../types';

describe('ImageGenerator', () => {
  let generator: ImageGenerator;

  beforeEach(() => {
    generator = new (require('../modules/imageGenerator').ImageGenerator)();
  });

  describe('generateImagePrompts', () => {
    it('should generate image prompts from content', async () => {
      const content: XHSContent = {
        title: 'AI写作工具',
        content: 'AI写作工具可以大大提高写作效率...',
        tags: ['#AI写作', '#效率工具']
      };

      const config = await generator.generateImagePrompts(content);

      expect(config).toBeDefined();
      expect(config.cover_image).toBeDefined();
      expect(config.cover_image.length).toBeGreaterThan(0);
      expect(config.content_images).toBeDefined();
      expect(config.content_images.length).toBeGreaterThanOrEqual(2);
      expect(config.content_images_count).toBe(config.content_images.length);
    });

    it('should generate prompts without forbidden elements', async () => {
      const content: XHSContent = {
        title: '测试',
        content: '测试内容',
        tags: ['#测试']
      };

      const config = await generator.generateImagePrompts(content);

      // 检查 prompt 中不包含违禁词
      const allPrompts = [config.cover_image, ...config.content_images].join(' ');
      expect(allPrompts).not.toMatch(/emoji|水印|logo|假字|乱码/);
    });

    it('should generate tech-style prompts', async () => {
      const content: XHSContent = {
        title: '科技产品',
        content: '科技产品介绍',
        tags: ['#科技']
      };

      const config = await generator.generateImagePrompts(content);

      // 检查是否包含科技风格描述
      const allPrompts = [config.cover_image, ...config.content_images].join(' ');
      expect(allPrompts).toMatch(/科技|科技感|浅色|未来|现代/);
    });
  });

  describe('generateImages', () => {
    it('should generate images from config', async () => {
      const config: ImageConfig = {
        cover_image: '科技风格封面，展示AI写作界面',
        content_images: [
          '用户使用AI写作工具的场景',
          'AI写作工具的界面展示'
        ],
        content_images_count: 2
      };

      const images = await generator.generateImages(config);

      expect(images).toBeDefined();
      expect(images.length).toBe(3); // 1封面 + 2内容图
      expect(images.every(img => img.startsWith('http'))).toBe(true);
    });

    it('should handle image generation errors gracefully', async () => {
      const config: ImageConfig = {
        cover_image: '无效的prompt',
        content_images: [],
        content_images_count: 0
      };

      // 应该抛出错误或返回空数组
      await expect(generator.generateImages(config)).rejects.toThrow();
    });
  });
});