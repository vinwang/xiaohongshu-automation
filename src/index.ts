/**
 * 小红书自动化发布工具 - 主入口
 */

import { XHSInput } from './types';
import { ConfigManager } from './config';
import { ContentGeneratorImpl } from './modules/contentGenerator';
import { ImageGeneratorImpl } from './modules/imageGenerator';
import { PreviewManagerImpl } from './modules/previewManager';
import { PublisherImpl } from './modules/publisher';

export class XHSAutomation {
  private contentGenerator: ContentGeneratorImpl;
  private imageGenerator: ImageGeneratorImpl;
  private previewManager: PreviewManagerImpl;
  private publisher: PublisherImpl;

  constructor() {
    const configManager = new ConfigManager();
    configManager.validate();

    this.contentGenerator = new ContentGeneratorImpl(configManager);
    this.imageGenerator = new ImageGeneratorImpl(configManager);
    this.previewManager = new PreviewManagerImpl(undefined, configManager);
    this.publisher = new PublisherImpl(configManager);
  }

  /**
   * 完整的工作流程
   */
  async run(input: XHSInput): Promise<void> {
    console.log('🚀 开始小红书自动化发布流程...\n');

    try {
      // 步骤 1: 生成内容结构
      console.log('📝 步骤 1/5: 生成内容结构...');
      const structure = await this.contentGenerator.generateStructure(input);
      console.log(`✅ 标题: ${structure.final_title}`);
      console.log(`✅ 标签: ${structure.tags.join(', ')}\n`);

      // 步骤 2: 生成完整内容
      console.log('📝 步骤 2/5: 生成完整内容...');
      const content = await this.contentGenerator.generateContent(structure);
      console.log(`✅ 正文长度: ${content.content.length} 字\n`);

      // 步骤 3: 生成图片配置
      console.log('🎨 步骤 3/5: 生成图片配置...');
      const imageConfig = await this.imageGenerator.generateImagePrompts(content);
      console.log(`✅ 封面图: ${imageConfig.cover_image.substring(0, 50)}...`);
      console.log(`✅ 内容图数量: ${imageConfig.content_images_count}\n`);

      // 步骤 4: 生成图片
      console.log('🎨 步骤 4/5: 生成图片...');
      const images = await this.imageGenerator.generateImages(imageConfig);
      console.log(`✅ 图片生成完成，共 ${images.length} 张\n`);

      // 步骤 5: 预览和确认
      console.log('👀 步骤 5/5: 生成预览并等待确认...');
      const previewData = {
        title: content.title,
        content: content.content,
        tags: content.tags,
        images: images
      };

      const html = this.previewManager.generatePreview(previewData);
      const result = await this.previewManager.showPreviewWithSchedule(html);

      if (!result.confirmed) {
        console.log('❌ 用户取消发布');
        return;
      }

      // 发布
      console.log('\n📤 开始发布...');

      if (result.scheduleTime) {
        // 定时发布
        await this.publisher.schedulePublish({
          title: content.title,
          content: content.content,
          tags: content.tags,
          images: images,
          scheduled_time: result.scheduleTime
        });
      } else {
        // 立即发布
        await this.publisher.publish({
          title: content.title,
          content: content.content,
          tags: content.tags,
          images: images
        });
      }

      console.log('\n🎉 全部流程完成！');

    } catch (error) {
      console.error('\n❌ 流程执行失败:', error);
      throw error;
    }
  }

  /**
   * 快速发布（跳过预览）
   */
  async quickPublish(input: XHSInput): Promise<void> {
    console.log('🚀 开始快速发布...\n');

    const structure = await this.contentGenerator.generateStructure(input);
    const content = await this.contentGenerator.generateContent(structure);
    const imageConfig = await this.imageGenerator.generateImagePrompts(content);
    const images = await this.imageGenerator.generateImages(imageConfig);

    await this.publisher.publish({
      title: content.title,
      content: content.content,
      tags: content.tags,
      images: images
    });

    console.log('\n🎉 快速发布完成！');
  }

  /**
   * 只生成内容，不发布
   */
  async generateOnly(input: XHSInput): Promise<{ content: any; images: string[] }> {
    console.log('🚀 开始生成内容...\n');

    const structure = await this.contentGenerator.generateStructure(input);
    const content = await this.contentGenerator.generateContent(structure);
    const imageConfig = await this.imageGenerator.generateImagePrompts(content);
    const images = await this.imageGenerator.generateImages(imageConfig);

    console.log('\n✅ 内容生成完成！');
    console.log(`标题: ${content.title}`);
    console.log(`正文: ${content.content}`);
    console.log(`标签: ${content.tags.join(', ')}`);
    console.log(`图片: ${images.length} 张`);

    return { content, images };
  }
}

export * from './types';
export * from './modules/contentGenerator';
export * from './modules/imageGenerator';
export * from './modules/previewManager';
export * from './modules/publisher';
export { ConfigManager } from './config';