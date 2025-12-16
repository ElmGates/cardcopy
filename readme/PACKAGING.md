# CardCopyer-拷贝乐 打包说明

## 已完成的打包

### macOS 版本
- ✅ **CardCopyer-拷贝乐.app** - macOS 应用程序包
- ✅ **CardCopyer** - macOS 可执行文件 (内部二进制名称)

打包文件位置：`/Users/peterjia/Documents/项目工程/cardcopy/dist/`

## Windows 版本打包方法

### 方法一：使用打包脚本
1. 在 Windows 系统中安装 Python 3.7+
2. 将项目文件复制到 Windows 电脑
3. 双击运行 `build_windows.bat`

### 方法二：手动打包
1. 安装依赖：
   ```cmd
   pip install pyinstaller ttkbootstrap psutil Pillow
   ```

2. 执行打包：
   ```cmd
   pyinstaller CardCopyer_windows.spec
   ```

3. 打包完成后，可执行文件在 `dist\CardCopyer-拷贝乐.exe`

## 打包配置说明

### 包含的文件
- `styles.css` - 程序样式文件
- `config.json` - 配置文件
- `launcher.py` - 程序启动器
- `main.py` - 主程序文件
- `md5_verifier.py` - MD5 验证模块

### 隐藏导入的模块
- ttkbootstrap 及其子模块
- psutil
- PIL (Pillow)

### 打包选项
- 不显示控制台窗口（windowed 模式）
- 启用 UPX 压缩
- 包含所有依赖项

## 注意事项

1. **图标文件**：可以在 spec 文件中设置 `icon` 参数来添加程序图标
2. **代码签名**：macOS 版本可以添加代码签名以避免安全警告
3. **权限**：确保程序有访问文件系统的权限

## 文件结构
```
dist/
├── CardCopyer-拷贝乐.app/          # macOS 应用程序包
│   └── Contents/
├── CardCopyer                     # macOS 可执行文件
└── [Windows 打包后]
    └── CardCopyer-拷贝乐.exe       # Windows 可执行文件
```
