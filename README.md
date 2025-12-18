# CardCopyer-拷贝乐

<div align="center">
  <img src="appicon.png" alt="CardCopyer Logo" width="128" height="128">
  
  <h3>专业、安全、高效的 DIT 拷卡工具</h3>
  
  <p>
    <a href="#-下载--download">下载</a> •
    <a href="#-核心功能--features">功能</a> •
    <a href="#-更新日志--logs">更新日志</a> •
    <a href="#-开发指南--development">开发</a> •
    <a href="#-版权--copyright">版权</a>
  </p>
</div>

---

**CardCopyer-拷贝乐** 是一款专为影视行业 DIT (Digital Imaging Technician) 和摄影师设计的数据备份工具。它旨在提供高速、安全的数据传输，并确保源数据与备份数据的一致性。

## 📥 下载 / Download

我们建议您前往官方网站下载最新发布的版本（支持 Windows 和 macOS）：

👉 **[点击访问官方网站下载](https://dit.superjia.com.cn)**

> **注意**: 
> 1. GitHub 仓库主要用于源代码托管和问题追踪。
> 2. 如果您希望使用稳定版本，请务必从官网下载。

## ✨ 核心功能 / Features

- 🛡️ **数据安全校验**: 内置 MD5 校验算法，确保每一个比特的数据都准确无误地从源卡传输到目标存储。
- ⚡ **高速多线程**: 优化的多线程拷贝引擎，充分利用系统资源，大幅缩短大容量素材的备份时间。
- 📝 **详细日志审计**: 全程记录操作日志，每一次拷贝、校验都有据可查，满足专业工作流程的严苛要求。
- 🖥️ **跨平台支持**: 完美支持 Windows 10+ 及 macOS (Apple Silicon)。
- 🎨 **现代界面**: 基于 ttkbootstrap 的现代化深色主题界面，不仅美观，更适合片场暗光环境工作。

## 📝 更新日志 / Logs

### 版本 1.1.3b （2025-12-18）
- 新增“是否只拷贝媒体文件”功能及悬浮说明。
- 扩展媒体类型支持：r3d、braw、ari、cine、heic/heif、mxf、mts 等。
- 拷贝完成时在开启媒体过滤情况下新增提醒弹窗。
- 文件夹名称预览逻辑优化，支持关闭日期前缀。

### 版本 1.1.2b （2025-12-16）
- 初始版本发布，包含基础的拷卡功能。

## 🛠️ 开发指南 / Development

如果您是开发者，想从源码运行或参与开发，请遵循以下步骤：

### 1. 环境要求
- Python 3.8 或更高版本
- 建议使用虚拟环境 (venv)

### 2. 安装依赖
```bash
# 克隆仓库
git clone https://github.com/PeterJia/CardCopyer.git
cd CardCopyer

# 安装依赖包
pip install -r requirements.txt
```

### 3. 运行程序
```bash
python main.py
```

### 4. 打包发布
本项目使用 PyInstaller 进行打包。可参考 [PACKAGING.md](readme/PACKAGING.md)。

## 📄 版权 / Copyright

Copyright © 2025-Now **SuperJia**. All rights reserved.

---

<div align="center">
  <sub>Built with Python & Tkinter</sub>
</div>
