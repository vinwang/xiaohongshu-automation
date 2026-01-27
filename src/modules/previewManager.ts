/**
 * 预览管理模块
 */

import * as fs from 'fs';
import * as path from 'path';
import open from 'open';
import { PreviewManager, PreviewData, Config } from '../types';
import { ConfigManager } from '../config';
import inquirer from 'inquirer';

export class PreviewManagerImpl implements PreviewManager {
  private config: Config;
  private outputDir: string;

  constructor(outputDir?: string, configManager?: ConfigManager) {
    const manager = configManager || new ConfigManager();
    this.config = manager.get();
    this.outputDir = outputDir || this.config.storage.previewDir;

    // 确保输出目录存在
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  /**
   * 生成 HTML 预览
   */
  generatePreview(data: PreviewData): string {
    const imagesHtml = data.images
      .map(url => `<img src="${url}" class="slide-img" />`)
      .join('');

    const tagsHtml = Array.isArray(data.tags) ? data.tags.join(' ') : data.tags;

    // 生成唯一的时间戳用于文件名
    const timestamp = Date.now();

    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>小红书发布预览</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <style>
    body {
      margin: 0;
      padding: 20px;
      background: #f6f6f6;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", Arial;
    }

    .card {
      max-width: 420px;
      margin: 0 auto;
      background: #fff;
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 10px 28px rgba(0,0,0,0.08);
    }

    /* Carousel Container */
    .carousel-wrapper {
      position: relative;
      background: #000;
    }

    .images {
      display: flex;
      overflow-x: auto;
      scroll-snap-type: x mandatory;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      scroll-behavior: smooth;
    }
    .images::-webkit-scrollbar {
      display: none;
    }

    .images img {
      width: 100%;
      height: auto;
      flex-shrink: 0;
      scroll-snap-align: center;
      aspect-ratio: 3/4;
      object-fit: contain;
      display: block;
    }

    /* Navigation Arrows */
    .nav-btn {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      background: rgba(255, 255, 255, 0.2);
      border: none;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 18px;
      transition: background 0.3s;
      z-index: 10;
    }
    .nav-btn:hover {
      background: rgba(255, 255, 255, 0.4);
    }
    .nav-prev {
      left: 10px;
    }
    .nav-next {
      right: 10px;
    }

    /* Dots Indicator */
    .dots {
      position: absolute;
      bottom: 10px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
    }
    .dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.5);
      transition: background 0.3s;
    }
    .dot.active {
      background: white;
    }

    .content {
      padding: 16px;
    }

    h1 {
      font-size: 18px;
      margin: 0 0 12px;
      line-height: 1.4;
    }

    .text {
      font-size: 14px;
      line-height: 1.7;
      white-space: pre-wrap;
      color: #333;
    }

    .tags {
      margin-top: 12px;
      color: #999;
      font-size: 13px;
    }

    .actions {
      padding: 16px;
      background: #fafafa;
      border-top: 1px solid #eee;
    }

    .btn-group {
      display: flex;
      gap: 12px;
    }

    .btn {
      flex: 1;
      padding: 12px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s;
    }

    .btn-confirm {
      background: #ff2442;
      color: white;
    }
    .btn-confirm:hover {
      background: #e02038;
    }

    .btn-cancel {
      background: #f0f0f0;
      color: #666;
    }
    .btn-cancel:hover {
      background: #e0e0e0;
    }

    .schedule-section {
      margin-top: 12px;
      padding: 12px;
      background: white;
      border-radius: 8px;
    }

    .schedule-section label {
      display: block;
      margin-bottom: 8px;
      font-size: 13px;
      color: #666;
    }

    .schedule-section input[type="datetime-local"] {
      width: 100%;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;
    }

    .status {
      padding: 12px;
      background: #fafafa;
      text-align: center;
      font-size: 13px;
      color: #666;
      border-top: 1px solid #eee;
    }
  </style>
</head>

<body>
  <div class="card">
    <!-- 图片轮播 -->
    <div class="carousel-wrapper">
      <div class="images" id="imageCarousel">
        ${imagesHtml}
      </div>

      ${data.images.length > 1 ? `
      <button class="nav-btn nav-prev" onclick="scrollCarousel(-1)">&#10094;</button>
      <button class="nav-btn nav-next" onclick="scrollCarousel(1)">&#10095;</button>

      <div class="dots" id="dots">
        ${data.images.map((_, i) => `<div class="dot ${i === 0 ? 'active' : ''}"></div>`).join('')}
      </div>
      ` : ''}
    </div>

    <!-- 内容 -->
    <div class="content">
      <h1>${data.title}</h1>
      <div class="text">${data.content}</div>
      <div class="tags">${tagsHtml}</div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <div class="btn-group">
        <button class="btn btn-cancel" onclick="handleCancel()">取消</button>
        <button class="btn btn-confirm" onclick="handleConfirm()">确认发布</button>
      </div>

      <div class="schedule-section">
        <label>
          <input type="checkbox" id="scheduleCheckbox" onchange="toggleSchedule()">
          定时发布
        </label>
        <input type="datetime-local" id="scheduleTime" style="display: none; margin-top: 8px;" />
      </div>
    </div>

    <div class="status">
      查看预览，确认无误后点击"确认发布"
    </div>
  </div>

  <script>
    const carousel = document.getElementById('imageCarousel');
    const dots = document.getElementById('dots');
    let currentIndex = 0;
    const images = ${JSON.stringify(data.images)};

    function scrollCarousel(direction) {
      const newIndex = currentIndex + direction;
      if (newIndex >= 0 && newIndex < images.length) {
        currentIndex = newIndex;
        updateCarousel();
      }
    }

    function updateCarousel() {
      carousel.scrollTo({
        left: currentIndex * carousel.offsetWidth,
        behavior: 'smooth'
      });

      // 更新指示点
      if (dots) {
        const dotElements = dots.querySelectorAll('.dot');
        dotElements.forEach((dot, i) => {
          dot.classList.toggle('active', i === currentIndex);
        });
      }
    }

    function toggleSchedule() {
      const checkbox = document.getElementById('scheduleCheckbox');
      const input = document.getElementById('scheduleTime');
      input.style.display = checkbox.checked ? 'block' : 'none';
    }

    function handleConfirm() {
      const isScheduled = document.getElementById('scheduleCheckbox').checked;
      const scheduleTime = isScheduled ? document.getElementById('scheduleTime').value : null;

      // 向父窗口发送确认消息
      window.parent.postMessage({
        type: 'confirm',
        timestamp: ${timestamp},
        scheduled: isScheduled,
        scheduleTime: scheduleTime
      }, '*');
    }

    function handleCancel() {
      window.parent.postMessage({
        type: 'cancel',
        timestamp: ${timestamp}
      }, '*');
    }

    // 自动轮播（可选）
    let autoScrollInterval;
    if (images.length > 1) {
      autoScrollInterval = setInterval(() => {
        scrollCarousel(1);
      }, 5000);
    }

    // 用户交互时停止自动轮播
    carousel.addEventListener('touchstart', () => clearInterval(autoScrollInterval));
    carousel.addEventListener('mouseenter', () => clearInterval(autoScrollInterval));
  </script>
</body>
</html>`;

    return html;
  }

  /**
   * 显示预览并等待用户确认
   */
  async showPreview(html: string): Promise<boolean> {
    // 生成文件名
    const filename = `preview_${Date.now()}.html`;
    const filepath = path.join(this.outputDir, filename);

    // 保存 HTML 文件
    fs.writeFileSync(filepath, html, 'utf-8');

    // 在浏览器中打开
    const fileUrl = `file://${filepath}`;
    await open(fileUrl);

    // 等待用户在命令行确认
    const answer = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'confirmed',
        message: '请在浏览器中查看预览，确认发布吗？',
        default: true
      }
    ]);

    return answer.confirmed;
  }

  /**
   * 显示预览并等待定时发布时间
   */
  async showPreviewWithSchedule(html: string): Promise<{ confirmed: boolean; scheduleTime?: string }> {
    // 生成文件名
    const filename = `preview_${Date.now()}.html`;
    const filepath = path.join(this.outputDir, filename);

    // 保存 HTML 文件
    fs.writeFileSync(filepath, html, 'utf-8');

    // 在浏览器中打开
    const fileUrl = `file://${filepath}`;
    await open(fileUrl);

    // 等待用户在命令行确认
    const answers = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'confirmed',
        message: '请在浏览器中查看预览，确认发布吗？',
        default: true
      },
      {
        type: 'confirm',
        name: 'scheduled',
        message: '是否定时发布？',
        default: false,
        when: (answers) => answers.confirmed
      },
      {
        type: 'input',
        name: 'scheduleTime',
        message: '请输入发布时间 (格式: YYYY-MM-DD HH:mm:ss)',
        when: (answers) => answers.scheduled,
        validate: (input) => {
          const regex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;
          return regex.test(input) || '时间格式不正确，请使用 YYYY-MM-DD HH:mm:ss 格式';
        }
      }
    ]);

    return {
      confirmed: answers.confirmed,
      scheduleTime: answers.scheduleTime
    };
  }
}

// 导出为默认导出，方便测试
export { PreviewManagerImpl as PreviewManager };