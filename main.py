#!/usr/bin/env python3

import sys
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# 全局图标管理器
_global_icon_image = None  # 存储PIL Image对象
_icon_preloaded = False

def preload_icon():
    """预加载图标，确保在窗口创建前就可用了"""
    global _icon_preloaded, _global_icon_image
    
    if not _icon_preloaded:
        try:
            # 确保PIL模块可用
            if 'PIL_Image' not in globals() or 'PIL_ImageTk' not in globals():
                from PIL import Image as PIL_Image
                from PIL import ImageTk as PIL_ImageTk
                # 将其注入全局命名空间以便其他函数使用
                globals()['PIL_Image'] = PIL_Image
                globals()['PIL_ImageTk'] = PIL_ImageTk
            
            icon_path = get_icon_path()
            if icon_path and 'PIL_Image' in globals():
                # 只加载Image对象，不创建PhotoImage，因为PhotoImage依赖于特定的Tk实例
                _global_icon_image = PIL_Image.open(icon_path)
                _icon_preloaded = True
                print(f"图标图像预加载成功: {icon_path}")
                return True
        except Exception as e:
            print(f"图标预加载失败: {e}")
            _icon_preloaded = False
    
    return _icon_preloaded is True

def get_global_icon_image():
    """获取全局图标Image对象"""
    global _global_icon_image
    
    if _global_icon_image is None:
        preload_icon()
    
    return _global_icon_image

def get_global_icon_photo():
    """已废弃：为了兼容性保留，但返回None以强制重新创建"""
    return None

def get_icon_path():
    """获取图标文件的完整路径"""
    # 检查当前目录（源码运行）
    if os.path.exists('appicon.png'):
        return 'appicon.png'
    
    # 检查可执行文件所在目录（打包后运行）
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径
        icon_path = os.path.join(sys._MEIPASS, 'appicon.png')
        if os.path.exists(icon_path):
            return icon_path
    
    # 检查应用包内的 Resources 目录
    app_path = os.path.dirname(os.path.abspath(__file__))
    resources_path = os.path.join(app_path, 'appicon.png')
    if os.path.exists(resources_path):
        return resources_path
    
    return None

def get_log_directory():
    """获取跨平台的日志目录路径"""
    system = sys.platform
    
    if system == "darwin":  # macOS
        # macOS: ~/Documents/CardCopyer/logs
        log_dir = os.path.expanduser("~/Documents/CardCopyer/logs")
    elif system == "win32":  # Windows
        # Windows: ~/Documents/CardCopyer/logs
        log_dir = os.path.expanduser("~/Documents/CardCopyer/logs")
    else:  # Linux 和其他系统
        # Linux: ~/.local/share/CardCopyer/logs
        log_dir = os.path.expanduser("~/.local/share/CardCopyer/logs")
    
    # 确保目录存在
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        # 如果无法创建目录，回退到应用目录
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
    
    return log_dir

# 延迟导入 - 提高启动速度
def import_heavy_modules():
    """延迟导入重量级的模块"""
    global tk, ttk, tb, filedialog, messagebox, shutil, hashlib, psutil, json, subprocess, PIL_Image, PIL_ImageTk
    
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from tkinter.constants import BOTH, YES, NO, X, Y, LEFT, RIGHT, TOP, BOTTOM, W, E, N, S, CENTER, HORIZONTAL, VERTICAL
    import shutil
    import hashlib
    import json
    import subprocess
    
    # 这些模块较重，延迟导入
    try:
        import ttkbootstrap as tb
        from ttkbootstrap.constants import PRIMARY, SUCCESS, INFO, WARNING, DANGER
    except ImportError:
        tb = None
    
    try:
        import psutil
    except ImportError:
        psutil = None
    
    try:
        from PIL import Image as PIL_Image, ImageTk as PIL_ImageTk
    except ImportError:
        PIL_Image = None
        PIL_ImageTk = None

# 快速依赖检查（只检查关键模块）
def quick_check_dependencies():
    """快速依赖检查，只检查最基本的模块"""
    required_modules = ["tkinter"]
    missing_modules = []
    
    for module_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(module_name)
    
    if missing_modules:
        if getattr(sys, 'frozen', False):
            error_msg = f"缺少必要的依赖模块: {', '.join(missing_modules)}\n"
            error_msg += "请重新打包程序或联系开发者。"
            print(error_msg)
            return False
        else:
            print(f"缺少依赖模块: {', '.join(missing_modules)}")
            return False
    
    return True

# 完整依赖检查（在后台线程中执行）
def full_check_dependencies():
    """完整的依赖检查"""
    required_modules = ["ttkbootstrap", "psutil", "PIL"]
    missing_modules = []
    
    for module_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(module_name)
    
    if missing_modules:
        if getattr(sys, 'frozen', False):
            return False, f"缺少必要的依赖模块: {', '.join(missing_modules)}"
        else:
            return False, f"缺少依赖模块: {', '.join(missing_modules)}\n请在命令行中运行: pip install ttkbootstrap psutil Pillow"
    
    return True, None

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
        widget.bind("<Motion>", self.move)
    def show(self, event=None):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip, text=self.text, justify="left", relief="solid", borderwidth=1, background="#ffffe0", foreground="#333", font=("Arial", 10))
        label.pack(padx=8, pady=6)
    def move(self, event):
        if self.tip:
            x = event.x_root + 12
            y = event.y_root + 12
            self.tip.wm_geometry(f"+{x}+{y}")
    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class CopyManager:
    """拷贝管理器 - 优化性能和资源管理"""
    def __init__(self):
        self.copying = False
        self.verifying = False
        self.total_files = 0
        self.copied_files = 0
        self.verified_files = 0
        self.errors = []
        
        # 日志文件相关
        self.log_file = None
        self.log_buffer = []  # 日志缓冲区
        
        # 拷贝进度相关
        self.total_size = 0  # 总大小（字节）
        self.copied_size = 0  # 已拷贝大小（字节）
        self.copy_start_time = 0  # 拷贝开始时间
        self.copy_speed = 0  # 拷贝速度（字节/秒）
        self.copy_eta = 0  # 预计剩余时间（秒）
        
        # 验证进度相关
        self.verified_size = 0  # 已验证大小（字节）
        self.verify_start_time = 0  # 验证开始时间
        self.verify_speed = 0  # 验证速度（字节/秒）
        self.verify_eta = 0  # 预计剩余时间（秒）
        
        # 日期文件夹名称（用于保持拷贝和验证使用相同的时间戳）
        self.date_folder = None
        
        # MD5验证统计
        self.total_md5_files = 0  # 需要验证MD5的文件总数
        self.md5_verified_files = 0  # 已完成MD5验证的文件数
        self.md5_calc_size = 0  # 已计算MD5的数据量（字节）
        self.md5_calc_speed = 0  # MD5计算速度（字节/秒）
        self.md5_start_time = 0  # MD5验证开始时间
        
        # 性能优化：缓存文件大小计算结果
        self._size_cache = {}
        self._size_cache_timeout = 5  # 缓存超时时间（秒）
    
    def get_folder_size(self, folder_path: str) -> int:
        """计算文件夹总大小（字节）- 使用缓存优化"""
        # 检查缓存
        current_time = time.time()
        cache_key = folder_path
        if cache_key in self._size_cache:
            cached_size, cache_time = self._size_cache[cache_key]
            if current_time - cache_time < self._size_cache_timeout:
                return cached_size
        
        total_size = 0
        try:
            # 使用更快的文件遍历方法
            for root, dirs, files in os.walk(folder_path, followlinks=False):
                # 限制遍历深度，避免深层嵌套目录
                if root.count(os.sep) - folder_path.count(os.sep) > 10:
                    dirs[:] = []  # 不继续深入
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.lstat(file_path)  # 使用lstat避免符号链接
                        total_size += stat.st_size
                    except (OSError, PermissionError, FileNotFoundError):
                        # 跳过无法访问的文件
                        continue
        except (OSError, PermissionError):
            # 跳过无法访问的文件夹
            pass
        
        # 缓存结果
        self._size_cache[cache_key] = (total_size, current_time)
        return total_size
    
    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def format_time(self, seconds) -> str:
        """格式化时间显示"""
        if seconds < 0:
            seconds = 0
        
        seconds = int(seconds)  # 转换为整数
        
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}分{secs}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}小时{minutes}分{secs}秒"
    
    def init_log_file(self, log_dir: str, session_name: str):
        """初始化日志文件"""
        try:
            # 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)
            
            # 生成日志文件名（使用时间戳和会话名称）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"copy_log_{timestamp}_{session_name}.log"
            log_path = os.path.join(log_dir, log_filename)
            
            self.log_file = open(log_path, 'w', encoding='utf-8')
            
            # 写入日志头
            self.log_file.write("="*80 + "\n")
            self.log_file.write(f"CardCopyer-拷贝乐 - 拷贝日志\n")
            self.log_file.write(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.log_file.write(f"会话名称: {session_name}\n")
            self.log_file.write("="*80 + "\n\n")
            self.log_file.flush()
            
            return log_path
        except Exception as e:
            print(f"初始化日志文件失败: {e}")
            return None
    
    def write_log(self, message: str):
        """写入日志到文件"""
        if self.log_file:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log_file.write(f"[{timestamp}] {message}\n")
                self.log_file.flush()
            except Exception as e:
                print(f"写入日志失败: {e}")
    
    def close_log_file(self):
        """关闭日志文件 - 优化清理过程"""
        if self.log_file:
            try:
                # 确保所有缓冲的日志都被写入
                if self.log_buffer:
                    for message in self.log_buffer:
                        self.log_file.write(message + "\n")
                    self.log_buffer.clear()
                
                self.log_file.write("\n" + "="*80 + "\n")
                self.log_file.write(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.log_file.write("="*80 + "\n")
                self.log_file.flush()  # 确保数据写入磁盘
                self.log_file.close()
                self.log_file = None
            except Exception as e:
                print(f"关闭日志文件失败: {e}")
        
        # 清理缓存
        self._size_cache.clear()

class StartupWindow:
    """启动窗口 - 显示加载进度"""
    def __init__(self):
        # 确保tkinter已导入
        if 'tk' not in globals():
            import tkinter as tk
            from tkinter import ttk
        
        # 确保PIL已导入
        if 'PIL_Image' not in globals() or 'PIL_ImageTk' not in globals():
            try:
                from PIL import Image as PIL_Image, ImageTk as PIL_ImageTk
            except ImportError:
                pass
        
        self.root = tk.Tk()
        self.root.title("CardCopyer-拷贝乐 - 启动中")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        
        # 设置窗口图标
        try:
            icon_path = get_icon_path()
            if icon_path and 'PIL_Image' in globals() and 'PIL_ImageTk' in globals():
                icon_image = PIL_Image.open(icon_path)
                icon_photo = PIL_ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, icon_photo)
        except Exception:
            pass  # 如果图标设置失败，继续使用默认图标
        
        # 居中显示
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 300) // 2
        y = (self.root.winfo_screenheight() - 150) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # 设置样式
        self.root.configure(bg='#2b3e50')
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="CardCopyer-拷贝乐",
            font=("Arial", 16, "bold"),
            bg='#2b3e50',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # 进度标签
        self.progress_label = tk.Label(
            self.root,
            text="正在初始化...",
            font=("Arial", 10),
            bg='#2b3e50',
            fg='white'
        )
        self.progress_label.pack()
        
        # 进度条
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=250
        )
        self.progress.pack(pady=10)
        self.progress.start()
        
    def update_progress(self, message):
        """更新进度信息"""
        self.progress_label.config(text=message)
        self.root.update()
        
    def close(self):
        """关闭启动窗口"""
        self.progress.stop()
        self.root.destroy()


class DITCopyTool:
    """CardCopyer主窗口"""
    
    def __init__(self):
        # 导入重量级模块
        import_heavy_modules()
        
        # 检查ttkbootstrap是否可用
        if tb is None:
            self.show_error_and_exit("ttkbootstrap模块不可用", "请安装ttkbootstrap: pip install ttkbootstrap")
            return
        
        # 预加载图标，确保在窗口创建前准备好
        preload_icon()
        self.icon_photo = None
        
        # 创建主窗口但先隐藏，避免显示默认图标
        self.window = tb.Window(
            title="CardCopyer-拷贝乐",
            themename="darkly",
            size=(1400, 900),
            resizable=(True, True)
        )
        
        # 立即隐藏窗口，防止显示默认图标
        self.window.withdraw()
        
        # 尝试立即设置图标（窗口隐藏状态下）
        try:
            icon_image = get_global_icon_image()
            if icon_image and 'PIL_ImageTk' in globals():
                self.icon_photo = PIL_ImageTk.PhotoImage(icon_image, master=self.window)
                self.window.wm_iconphoto(True, self.icon_photo)
                if hasattr(self.window, 'iconphoto'):
                    self.window.iconphoto(True, self.icon_photo)
                print("主窗口图标在隐藏状态下设置成功")
        except Exception as e:
            print(f"隐藏状态下设置主窗口图标失败: {e}")
        
        # 设置窗口关闭事件处理
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.copy_manager = CopyManager()
        self.source_items = []  # 源项目列表
        self.destination_path = ""
        self.copy_thread = None
        self.media_extensions = {
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic", ".heif",
            ".cr2", ".cr3", ".nef", ".arw", ".dng", ".rw2", ".orf", ".raf", ".srw", ".pef", ".rwl",
            ".r3d", ".braw", ".ari", ".cine",
            ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".m4v", ".webm", ".mxf", ".mts", ".m2ts", ".ts", ".3gp", ".3g2",
            ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".aiff", ".aif", ".wma"
        }
        
        # 延迟UI初始化（窗口仍在隐藏状态）
        self.window.after(100, self._show_main_window_with_icon)
        
        # 启动图标监控定时器
        if self.icon_photo:
            self._start_icon_monitor()
    
    def _show_main_window_with_icon(self):
        """显示主窗口并确保图标正确设置"""
        try:
            # 先设置UI
            self.setup_ui()
            
            # 尝试设置图标
            self._try_set_icon()
            
            # 显示窗口
            self.window.deiconify()
            print("主窗口已显示")
            
        except Exception as e:
            print(f"显示主窗口时发生异常: {e}")
            # 确保窗口显示，但不重复设置UI
            self.window.deiconify()

    def _try_set_icon(self):
        """尝试设置窗口图标，处理跨实例问题"""
        try:
            # 获取PIL Image对象而不是预先创建的PhotoImage
            icon_image = get_global_icon_image()
            if icon_image:
                # 为当前窗口创建专用的PhotoImage
                if 'PIL_ImageTk' in globals():
                    self.icon_photo = PIL_ImageTk.PhotoImage(icon_image, master=self.window)
                    self.window.wm_iconphoto(True, self.icon_photo)
                    if hasattr(self.window, 'iconphoto'):
                        self.window.iconphoto(True, self.icon_photo)
                    print("图标设置成功")
        except Exception as e:
            print(f"设置图标失败: {e}")
    
    def _set_window_icon(self):
        """延迟设置主窗口图标，使用全局图标确保一致性"""
        try:
            # 使用全局图标管理器获取Image对象
            icon_image = get_global_icon_image()
            
            if icon_image and self.window:
                # 为当前窗口创建专用的PhotoImage
                if 'PIL_ImageTk' in globals():
                    self.icon_photo = PIL_ImageTk.PhotoImage(icon_image, master=self.window)
                    
                    # 使用多种方法设置图标，确保兼容性
                    self.window.wm_iconphoto(True, self.icon_photo)
                    if hasattr(self.window, 'iconphoto'):
                        self.window.iconphoto(True, self.icon_photo)
                    
                    # 启动图标监控定时器
                    self._start_icon_monitor()
            elif not icon_image:
                # 如果全局图标不可用，尝试本地创建
                icon_path = get_icon_path()
                if icon_path and 'PIL_Image' in globals() and 'PIL_ImageTk' in globals():
                    icon_image = PIL_Image.open(icon_path)
                    self.icon_photo = PIL_ImageTk.PhotoImage(icon_image, master=self.window)
                    if self.window and self.icon_photo:
                        self.window.wm_iconphoto(True, self.icon_photo)
                        if hasattr(self.window, 'iconphoto'):
                            self.window.iconphoto(True, self.icon_photo)
                        
                        # 启动图标监控定时器
                        self._start_icon_monitor()
        except Exception as e:
            print(f"设置主窗口图标失败: {e}")
            pass
    
    def _start_icon_monitor(self):
        """启动图标监控定时器，防止图标被系统重置"""
        def check_and_restore_icon():
            try:
                # 检查图标是否仍然有效
                if self.window and self.icon_photo:
                    # 重新应用图标
                    self.window.wm_iconphoto(True, self.icon_photo)
                    if hasattr(self.window, 'iconphoto'):
                        self.window.iconphoto(True, self.icon_photo)
                
                # 每5秒检查一次
                self.window.after(5000, check_and_restore_icon)
            except Exception:
                pass
        
        # 启动第一次检查
        self.window.after(5000, check_and_restore_icon)
    
    def show_error_and_exit(self, title, message):
        """显示错误并退出"""
        messagebox.showerror(title, message)
        sys.exit(1)
    
    def on_closing(self):
        """窗口关闭事件处理 - 优化退出性能"""
        try:
            # 如果有正在进行的拷贝线程，先停止它
            if self.copy_thread and self.copy_thread.is_alive():
                if messagebox.askyesno("确认", "有拷贝任务正在进行中，确定要退出吗？"):
                    # 设置停止标志
                    self.copy_manager.copying = False
                    self.copy_manager.verifying = False
                    # 等待线程结束（最多3秒）
                    self.copy_thread.join(timeout=3)
                else:
                    return
            
            # 清理资源
            self.cleanup_resources()
            
            # 销毁窗口
            self.window.quit()
            self.window.destroy()
            
        except Exception as e:
            print(f"退出时出错: {e}")
            # 强制退出
            try:
                self.window.quit()
                self.window.destroy()
            except:
                pass
    
    def cleanup_resources(self):
        """清理资源 - 优化退出性能"""
        try:
            # 关闭日志文件
            if hasattr(self, 'copy_manager'):
                self.copy_manager.close_log_file()
            
            # 清理UI组件引用（帮助垃圾回收）
            if hasattr(self, 'source_tree'):
                self.source_tree.delete(*self.source_tree.get_children())
            
            # 清理线程引用
            if hasattr(self, 'copy_thread'):
                self.copy_thread = None
            
            # 清理大对象引用
            if hasattr(self, 'copy_manager'):
                self.copy_manager = None
                
        except Exception as e:
            print(f"清理资源时出错: {e}")
        
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = tb.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # 标题
        title_label = tb.Label(
            main_frame,
            text="CardCopyer-拷贝乐",
            font=("Arial", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))
        
        # 主要内容区域
        content_frame = tb.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # 左侧 - 源选择
        self.setup_source_frame(content_frame)
        
        # 中间列容器
        middle_column = tb.Frame(content_frame)
        middle_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # 中间 - 目的地选择
        self.setup_destination_frame(middle_column)
        # 中间 - 设置
        self.setup_settings_frame(middle_column)
        
        # 右侧 - 进度显示
        self.setup_progress_frame(content_frame)
        
        # 底部按钮区域
        self.setup_bottom_frame(main_frame)
        
    def setup_source_frame(self, parent):
        """设置源选择框架"""
        source_frame = ttk.LabelFrame(
            parent,
            text="源文件夹选择",
            bootstyle="primary",
            padding=15
        )
        source_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # 文件夹选择区域
        folder_select_frame = tb.Frame(source_frame)
        folder_select_frame.pack(fill="x", pady=(0, 10))
        
        # 添加文件夹按钮
        add_folder_btn = tb.Button(
            folder_select_frame,
            text="添加文件夹",
            bootstyle="success-outline",
            command=self.add_source_folder
        )
        add_folder_btn.pack(side="left", padx=(0, 10))
        
        # 文件夹大小统计
        self.folder_size_label = tb.Label(
            folder_select_frame,
            text="总大小: 0 GB",
            font=("Arial", 10),
            bootstyle="info"
        )
        self.folder_size_label.pack(side="left")
        
        # 源项目列表
        tb.Label(source_frame, text="已选择的源文件夹:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        source_items_frame = tb.Frame(source_frame)
        source_items_frame.pack(fill="both", expand=True)
        
        source_scroll = tb.Scrollbar(source_items_frame)
        source_scroll.pack(side="right", fill="y")
        
        self.source_items_listbox = tk.Listbox(
            source_items_frame,
            yscrollcommand=source_scroll.set,
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white",
            selectbackground="#005a9e"
        )
        self.source_items_listbox.pack(side="left", fill="both", expand=True)
        source_scroll.config(command=self.source_items_listbox.yview)
        
        # 操作按钮区域
        button_frame = tb.Frame(source_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # 修改名称按钮
        rename_folder_btn = tb.Button(
            button_frame,
            text="修改名称",
            bootstyle="warning-outline",
            command=self.rename_selected_folder
        )
        rename_folder_btn.pack(side="left", padx=(0, 10))
        
        # 移除选中文件夹按钮
        remove_folder_btn = tb.Button(
            button_frame,
            text="移除选中",
            bootstyle="danger-outline",
            command=self.remove_selected_folder
        )
        remove_folder_btn.pack(side="left", padx=(0, 10))
        
        # 清空所有按钮
        clear_all_btn = tb.Button(
            button_frame,
            text="清空所有",
            bootstyle="secondary-outline",
            command=self.clear_all_folders
        )
        clear_all_btn.pack(side="left")
        
    def setup_destination_frame(self, parent):
        """设置目的地选择框架"""
        dest_frame = ttk.LabelFrame(
            parent,
            text="目的地选择",
            bootstyle="info",
            padding=15
        )
        dest_frame.pack(fill="x", padx=(0, 10))
        
        # 目的地路径显示
        self.dest_path_label = tb.Label(
            dest_frame,
            text="未选择目的地",
            font=("Arial", 11),
            bootstyle="secondary",
            wraplength=300
        )
        self.dest_path_label.pack(pady=(0, 15))
        
        # 选择目的地按钮
        select_dest_btn = tb.Button(
            dest_frame,
            text="选择目的地文件夹",
            bootstyle="info",
            command=self.select_destination
        )
        select_dest_btn.pack(pady=(0, 10))
        
        # 自动创建文件夹（默认启用，不再显示选框）
        self.auto_folder_var = tk.BooleanVar(value=True)
        
        # 自动日期前缀开关
        self.auto_date_prefix_var = tk.BooleanVar(value=True)
        date_prefix_cb = tb.Checkbutton(
            dest_frame,
            text="自动添加日期前缀",
            variable=self.auto_date_prefix_var,
            bootstyle="info-round-toggle",
            command=self.update_folder_preview
        )
        date_prefix_cb.pack(pady=(0, 10))
        
        # 项目名称输入区域
        project_frame = tb.Frame(dest_frame)
        project_frame.pack(fill="x", pady=(0, 15))
        
        tb.Label(
            project_frame,
            text="项目名称:",
            bootstyle="info"
        ).pack(side="left", padx=(0, 10))
        
        self.project_name_var = tk.StringVar()
        self.project_name_entry = tb.Entry(
            project_frame,
            textvariable=self.project_name_var,
            width=20,
            bootstyle="info"
        )
        self.project_name_entry.pack(side="left", fill="x", expand=True)
        
        # 项目名称提示
        tb.Label(
            dest_frame,
            text="关闭日期前缀时必须输入项目名称",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(pady=(0, 5))
        
        # 文件夹名称预览
        self.folder_preview_label = tb.Label(
            dest_frame,
            text="",
            font=("Arial", 9, "italic"),
            bootstyle="info"
        )
        self.folder_preview_label.pack(pady=(0, 15))
        
        # 目的地信息
        self.dest_info_label = tb.Label(
            dest_frame,
            text="",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.dest_info_label.pack()
        
        # 绑定项目名称变化事件，实时更新预览
        self.project_name_var.trace_add("write", lambda *args: self.update_folder_preview())
        self.update_folder_preview()

    def setup_settings_frame(self, parent):
        settings_frame = ttk.LabelFrame(
            parent,
            text="设置",
            bootstyle="secondary",
            padding=10
        )
        settings_frame.pack(fill="x", pady=(15, 0))
        
        settings_row = tb.Frame(settings_frame)
        settings_row.pack(fill="x")
        
        self.only_media_var = tk.BooleanVar(value=False)
        only_media_cb = tb.Checkbutton(
            settings_row,
            text="是否只拷贝媒体文件",
            variable=self.only_media_var,
            bootstyle="info-round-toggle",
            command=self.on_only_media_toggle
        )
        only_media_cb.pack(side="left")
        
        help_label = tb.Label(
            settings_row,
            text="?",
            font=("Arial", 10, "bold"),
            bootstyle="info",
            cursor="hand2"
        )
        help_label.pack(side="left", padx=(8, 0))
        Tooltip(help_label, "启用后仅拷贝常见媒体文件（图片、视频、音频、RAW）。不拷贝文档、工程文件等。")
        
        btn_row = tb.Frame(settings_frame)
        btn_row.pack(fill="x", pady=(10, 0))
        self.edit_media_btn = tb.Button(
            btn_row,
            text="编辑媒体文件类型",
            bootstyle="info",
            command=self.open_media_types_editor,
            state="disabled",
            width=20
        )
        self.edit_media_btn.pack(side="left")
        self.on_only_media_toggle()
    
    def on_only_media_toggle(self):
        if self.only_media_var.get():
            self.edit_media_btn.config(state="normal")
            messagebox.showinfo("危险！！", "此操作很危险！！开启仅拷贝媒体文件后，非媒体文件将被忽略。请核对文件类型是否正确，如果空间足够不建议打开。")
        else:
            self.edit_media_btn.config(state="disabled")
    
    def open_media_types_editor(self):
        editor = tk.Toplevel(self.window)
        editor.title("编辑媒体文件类型")
        editor.geometry("400x500")
        editor.transient(self.window)
        editor.grab_set()
        
        text = tk.Text(editor, font=("Courier", 11))
        text.pack(fill="both", expand=True)
        initial = "\n".join(sorted(self.get_media_extensions()))
        text.insert("1.0", initial)
        
        button_frame = tb.Frame(editor, padding=10)
        button_frame.pack(fill="x")
        
        def save():
            content = text.get("1.0", "end").strip().splitlines()
            cleaned = set()
            for line in content:
                s = line.strip().lower()
                if not s:
                    continue
                if not s.startswith("."):
                    s = "." + s
                cleaned.add(s)
            if cleaned:
                self.media_extensions = cleaned
            editor.destroy()
        
        save_btn = tb.Button(button_frame, text="保存", bootstyle="success", command=save, width=12)
        save_btn.pack(side="right", padx=(10, 0))
        cancel_btn = tb.Button(button_frame, text="取消", bootstyle="secondary", command=editor.destroy, width=12)
        cancel_btn.pack(side="right")
        
    def setup_progress_frame(self, parent):
        """设置进度显示框架"""
        progress_frame = ttk.LabelFrame(
            parent,
            text="拷贝进度",
            bootstyle="success",
            padding=15
        )
        progress_frame.pack(side="left", fill="both", expand=True)
        
        # 拷贝进度
        tb.Label(progress_frame, text="拷贝进度:", font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.copy_progress = tb.Progressbar(
            progress_frame,
            bootstyle="success-striped",
            length=300,
            mode='determinate'
        )
        self.copy_progress.pack(fill="x", pady=(5, 15))
        
        self.copy_status_label = tb.Label(
            progress_frame,
            text="等待开始拷贝...",
            font=("Arial", 10)
        )
        self.copy_status_label.pack(anchor="w")
        
        # 拷贝速度和进度信息
        self.copy_speed_label = tb.Label(
            progress_frame,
            text="速度: 0 MB/s | 已用: 00:00 | 剩余: 00:00",
            font=("Arial", 9)
        )
        self.copy_speed_label.pack(anchor="w", pady=(2, 0))
        
        # 验证进度
        tb.Label(progress_frame, text="验证进度:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(20, 5))
        
        self.verify_progress = tb.Progressbar(
            progress_frame,
            bootstyle="warning-striped",
            length=300,
            mode='determinate'
        )
        self.verify_progress.pack(fill="x", pady=(5, 15))
        
        self.verify_status_label = tb.Label(
            progress_frame,
            text="等待拷贝完成...",
            font=("Arial", 10)
        )
        self.verify_status_label.pack(anchor="w")
        
        # 验证速度信息
        self.verify_speed_label = tb.Label(
            progress_frame,
            text="速度: 0 MB/s | 已用: 00:00 | 剩余: 00:00",
            font=("Arial", 9)
        )
        self.verify_speed_label.pack(anchor="w", pady=(2, 0))
        
        # 统计信息
        stats_frame = tb.Frame(progress_frame)
        stats_frame.pack(fill="x", pady=(20, 0))
        
        self.total_files_label = tb.Label(stats_frame, text="总文件数: 0", font=("Arial", 10))
        self.total_files_label.pack(side="left")
        
        self.copied_files_label = tb.Label(stats_frame, text="已拷贝: 0", font=("Arial", 10))
        self.copied_files_label.pack(side="left", padx=(20, 0))
        
        self.verified_files_label = tb.Label(stats_frame, text="已验证: 0", font=("Arial", 10))
        self.verified_files_label.pack(side="left", padx=(20, 0))
        
        # 日志区域
        tb.Label(progress_frame, text="操作日志:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(20, 5))
        
        log_frame = tb.Frame(progress_frame)
        log_frame.pack(fill="both", expand=True)
        
        log_scroll = tb.Scrollbar(log_frame)
        log_scroll.pack(side="right", fill="y")
        
        self.log_text = tk.Text(
            log_frame,
            height=10,
            yscrollcommand=log_scroll.set,
            font=("Courier", 9),
            bg="#1e1e1e",
            fg="white"
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.config(command=self.log_text.yview)
        
    def setup_bottom_frame(self, parent):
        """设置底部按钮框架"""
        bottom_frame = tb.Frame(parent)
        bottom_frame.pack(fill="x", pady=(20, 0))
        
        # 开始按钮
        self.start_btn = tb.Button(
            bottom_frame,
            text="开始拷贝",
            bootstyle="success",
            command=self.start_copy,
            width=20
        )
        self.start_btn.pack(side="left", padx=(0, 10))
        
        # 停止按钮
        self.stop_btn = tb.Button(
            bottom_frame,
            text="停止拷贝",
            bootstyle="danger",
            command=self.stop_copy,
            width=20,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        # 清空按钮
        clear_btn = tb.Button(
            bottom_frame,
            text="清空列表",
            bootstyle="warning",
            command=self.clear_all,
            width=15
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        # 查看日志按钮
        view_logs_btn = tb.Button(
            bottom_frame,
            text="查看日志",
            bootstyle="info",
            command=self.open_log_viewer,
            width=15
        )
        view_logs_btn.pack(side="left", padx=(0, 10))
        
        # 版权信息标签（可点击）
        copyright_label = tb.Label(
            bottom_frame,
            text="Copyright ©️ 2025-Now SuperJia 保留所有权利，CardCopyer-拷贝乐 v1.1.3(beta) 点击前往官网",
            font=("Arial", 9),
            bootstyle="secondary",
            cursor="hand2"  # 鼠标悬停时显示手型光标
        )
        copyright_label.pack(side="left", padx=(10, 0))
        
        # 绑定点击事件
        copyright_label.bind("<Button-1>", self.open_official_website)
        
        # 退出按钮
        exit_btn = tb.Button(
            bottom_frame,
            text="退出",
            bootstyle="secondary",
            command=self.window.destroy,
            width=15
        )
        exit_btn.pack(side="right")
        
    def format_time(self, seconds):
        """格式化时间显示"""
        if seconds <= 0:
            return "00:00"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
            
    def update_total_size(self):
        """更新总大小显示"""
        total_size = sum(item['size'] for item in self.source_items)
        size_str = self.copy_manager.format_size(total_size)
        self.folder_size_label.config(text=f"总大小: {size_str}")
        
        # 如果总大小超过1GB，显示更详细的信息
        if total_size > 1024**3:
            gb_size = total_size / (1024**3)
            self.folder_size_label.config(text=f"总大小: {size_str} ({gb_size:.2f} GB)")
            
    def add_source_folder(self):
        """添加源文件夹"""
        folder = filedialog.askdirectory(title="选择源文件夹")
        if folder:
            # 获取文件夹名称和大小
            folder_name = os.path.basename(folder)
            try:
                # 使用复制管理器的文件夹大小计算功能
                total_size = self.copy_manager.get_folder_size(folder)
                size_str = self.copy_manager.format_size(total_size)
                
                # 弹出对话框让用户自定义命名
                custom_name = self.ask_custom_folder_name(folder_name)
                if custom_name is None:  # 用户取消
                    return
                
                source_item = {
                    'path': folder,
                    'name': folder_name,
                    'custom_name': custom_name,
                    'size': total_size,
                    'display': f"{folder_name} - {size_str}"
                }
                
                # 如果自定义名称与原始名称不同，在显示中添加提示
                if custom_name != folder_name:
                    source_item['display'] = f"{folder_name} - {size_str} (→ {custom_name})"
                
                self.source_items.append(source_item)
                self.source_items_listbox.insert(tk.END, source_item['display'])
                self.log_message(f"添加源文件夹: {folder} ({size_str})")
                if custom_name != folder_name:
                    self.log_message(f"自定义命名为: {custom_name}")
                
                # 更新总大小显示
                self.update_total_size()
                
            except Exception as e:
                messagebox.showerror("错误", f"无法读取文件夹信息: {str(e)}")
    
    def ask_custom_folder_name(self, original_name):
        """询问用户自定义文件夹名称"""
        dialog = tk.Toplevel(self.window)
        dialog.title("自定义文件夹名称")
        dialog.geometry("400x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 提示信息
        info_frame = tb.Frame(dialog, padding=20)
        info_frame.pack(fill="both", expand=True)
        
        tb.Label(info_frame, text="为源文件夹设置目标名称", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        tb.Label(info_frame, text=f"原始名称: {original_name}", font=("Arial", 10)).pack(pady=(0, 15))
        
        # 输入框
        name_var = tk.StringVar(value=original_name)
        entry = tb.Entry(info_frame, textvariable=name_var, width=40, font=("Arial", 11))
        entry.pack(pady=(0, 20))
        entry.focus()
        entry.select_range(0, tk.END)
        
        # 按钮区域
        button_frame = tb.Frame(info_frame)
        button_frame.pack(fill="x")
        
        def on_ok():
            dialog.result = name_var.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.result = None
            dialog.destroy()
        
        tb.Button(button_frame, text="确定", bootstyle="success", command=on_ok).pack(side="right", padx=(10, 0))
        tb.Button(button_frame, text="取消", bootstyle="secondary", command=on_cancel).pack(side="right")
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: on_ok())
        entry.bind("<Escape>", lambda e: on_cancel())
        
        # 等待对话框关闭
        dialog.wait_window(dialog)
        return getattr(dialog, 'result', None)
    
    def rename_selected_folder(self):
        """修改选中文件夹的自定义名称"""
        selection = self.source_items_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要修改名称的文件夹")
            return
            
        if len(selection) > 1:
            messagebox.showinfo("提示", "一次只能修改一个文件夹的名称")
            return
            
        index = selection[0]
        source_item = self.source_items[index]
        
        # 询问新的自定义名称
        new_custom_name = self.ask_custom_folder_name(source_item['name'])
        if new_custom_name is None:  # 用户取消
            return
            
        # 更新自定义名称
        old_custom_name = source_item.get('custom_name', source_item['name'])
        source_item['custom_name'] = new_custom_name
        
        # 更新显示
        size_str = self.copy_manager.format_size(source_item['size'])
        if new_custom_name != source_item['name']:
            source_item['display'] = f"{source_item['name']} - {size_str} (→ {new_custom_name})"
        else:
            source_item['display'] = f"{source_item['name']} - {size_str}"
            
        # 更新列表框
        self.source_items_listbox.delete(index)
        self.source_items_listbox.insert(index, source_item['display'])
        self.source_items_listbox.selection_set(index)
        
        # 记录日志
        if old_custom_name != new_custom_name:
            self.log_message(f"修改文件夹名称: {source_item['path']}")
            self.log_message(f"  从 '{old_custom_name}' 改为 '{new_custom_name}'")
    
    def remove_selected_folder(self):
        """移除选中的文件夹"""
        selection = self.source_items_listbox.curselection()
        if selection:
            # 从后往前删除，避免索引问题
            for index in reversed(selection):
                removed_item = self.source_items.pop(index)
                self.source_items_listbox.delete(index)
                self.log_message(f"移除源文件夹: {removed_item['path']}")
            
            # 更新总大小显示
            self.update_total_size()
        else:
            messagebox.showinfo("提示", "请先选择要移除的文件夹")
    
    def clear_all_folders(self):
        """清空所有文件夹"""
        if not self.source_items:
            messagebox.showinfo("提示", "当前没有选择任何文件夹")
            return
            
        # 确认对话框
        result = messagebox.askyesno(
            "确认清空",
            f"确定要清空所有 {len(self.source_items)} 个文件夹吗？\n\n此操作不会删除实际文件，只是取消选择。"
        )
        
        if result:
            self.source_items.clear()
            self.source_items_listbox.delete(0, tk.END)
            self.update_total_size()
            self.log_message("清空所有源文件夹")
    
    def select_destination(self):
        """选择目的地"""
        folder = filedialog.askdirectory(title="选择目的地文件夹")
        if folder:
            self.destination_path = folder
            self.dest_path_label.config(text=folder)
            
            # 更新目的地信息
            try:
                usage = psutil.disk_usage(folder)
                free_gb = usage.free / (1024**3)
                self.dest_info_label.config(text=f"可用空间: {free_gb:.2f}GB")
            except:
                self.dest_info_label.config(text="无法获取空间信息")
                
            self.log_message(f"选择目的地: {folder}")
            
            # 更新文件夹预览
            self.update_folder_preview()
            
    def update_folder_preview(self):
        """更新文件夹名称预览"""
        # 生成预览文件夹名称
        from datetime import datetime
        project_name = self.project_name_var.get().strip()
        
        # 清理项目名称中的特殊字符
        safe_project_name = ""
        if project_name:
            safe_project_name = "".join(c for c in project_name if c.isalnum() or c in "-_ ")
            safe_project_name = safe_project_name.strip().replace(" ", "_")
            
        if self.auto_date_prefix_var.get():
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            if safe_project_name:
                folder_name = f"{date_str}_{safe_project_name}"
            else:
                folder_name = date_str
        else:
            # 不使用日期前缀
            if safe_project_name:
                folder_name = safe_project_name
            else:
                folder_name = "(需输入项目名称)"
            
        self.folder_preview_label.config(text=f"📁 将创建文件夹: {folder_name}")
    
    def get_media_extensions(self):
        return getattr(self, "media_extensions", set())
    
    def is_media_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.get_media_extensions()
            
    def start_copy(self):
        """开始拷贝"""
        if not self.source_items:
            messagebox.showwarning("警告", "请先选择源文件夹")
            return
            
        if not self.destination_path:
            messagebox.showwarning("警告", "请先选择目的地")
            return
            
        # 验证项目名称
        if not self.auto_date_prefix_var.get():
            project_name = self.project_name_var.get().strip()
            if not project_name:
                messagebox.showwarning("警告", "关闭自动日期前缀后，必须输入项目名称！")
                return
                
            # 检查有效字符
            safe_name = "".join(c for c in project_name if c.isalnum() or c in "-_ ")
            if not safe_name.strip():
                messagebox.showwarning("警告", "项目名称必须包含字母、数字、下划线或连字符！")
                return
            
        # 禁用开始按钮，启用停止按钮
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # 开始拷贝线程
        self.copy_thread = threading.Thread(target=self.copy_process)
        self.copy_thread.daemon = True
        self.copy_thread.start()
        
    def stop_copy(self):
        """停止拷贝"""
        self.copy_manager.copying = False
        self.log_message("用户停止拷贝操作")
        
    def copy_process(self):
        """拷贝过程"""
        import time
        try:
            self.copy_manager.copying = True
            self.copy_manager.total_files = 0
            self.copy_manager.copied_files = 0
            self.copy_manager.verified_files = 0
            self.copy_manager.total_size = 0
            self.copy_manager.copied_size = 0
            
            # 重置日期文件夹，确保每次拷贝都使用新的时间戳
            self.copy_manager.date_folder = None
            
            # 初始化日志文件
            log_dir = get_log_directory()
            session_name = self.project_name_var.get().strip() or "untitled"
            log_path = self.copy_manager.init_log_file(log_dir, session_name)
            
            if log_path:
                self.log_message(f"📋 日志文件已创建: {log_path}")
            else:
                self.log_message("⚠️  日志文件创建失败，继续拷贝...")
            
            # 创建目标文件夹
            if self.auto_folder_var.get():
                # 生成文件夹名称
                if self.copy_manager.date_folder is None:
                    project_name = self.project_name_var.get().strip()
                    
                    # 清理项目名称
                    safe_project_name = ""
                    if project_name:
                        safe_project_name = "".join(c for c in project_name if c.isalnum() or c in "-_ ")
                        safe_project_name = safe_project_name.strip().replace(" ", "_")
                    
                    if self.auto_date_prefix_var.get():
                        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        if safe_project_name:
                            self.copy_manager.date_folder = f"{date_str}_{safe_project_name}"
                        else:
                            self.copy_manager.date_folder = date_str
                    else:
                        # 不使用日期前缀，使用项目名称
                        self.copy_manager.date_folder = safe_project_name
                        
                final_dest = os.path.join(self.destination_path, self.copy_manager.date_folder)
            else:
                final_dest = self.destination_path
                
            os.makedirs(final_dest, exist_ok=True)
            self.log_message(f"创建目标文件夹: {final_dest}")
            if self.auto_folder_var.get() and self.copy_manager.date_folder:
                self.log_message(f"使用日期文件夹: {self.copy_manager.date_folder}")
            
            # 统计总文件数和总大小
            self.log_message("正在统计文件...")
            for source_item in self.source_items:
                for root, dirs, files in os.walk(source_item['path']):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.only_media_var.get() and not self.is_media_file(file_path):
                            continue
                        self.copy_manager.total_files += 1
                        try:
                            self.copy_manager.total_size += os.path.getsize(file_path)
                        except:
                            pass
                            
            self.update_stats()
            self.log_message(f"总计 {self.copy_manager.total_files} 个文件 ({self.copy_manager.format_size(self.copy_manager.total_size)})")
            
            # 记录开始时间
            self.copy_manager.copy_start_time = time.time()
            
            # 开始拷贝
            for source_item in self.source_items:
                if not self.copy_manager.copying:
                    break
                
                # 使用自定义名称进行拷贝
                folder_name = source_item.get('custom_name', source_item['name'])
                self.copy_folder(source_item['path'], final_dest, folder_name)
                
            # 开始验证
            if self.copy_manager.copying and self.copy_manager.copied_files > 0:
                self.verify_files()
                
            # 完成
            if self.copy_manager.copying:
                self.copy_complete()
            else:
                self.copy_stopped()
                
        except Exception as e:
            self.log_message(f"拷贝过程出错: {str(e)}")
            messagebox.showerror("错误", f"拷贝过程出错: {str(e)}")
            
        finally:
            # 恢复按钮状态
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            
    def copy_file_with_progress(self, source_file, dest_file, file_size):
        """优化的分块拷贝文件，支持实时进度更新"""
        import time
        
        # 根据文件大小调整块大小 - 优化大文件处理
        if file_size > 500 * 1024 * 1024:  # 大于500MB
            chunk_size = 16 * 1024 * 1024  # 16MB块
        elif file_size > 100 * 1024 * 1024:  # 大于100MB
            chunk_size = 8 * 1024 * 1024   # 8MB块
        elif file_size > 10 * 1024 * 1024:  # 大于10MB
            chunk_size = 4 * 1024 * 1024   # 4MB块
        else:
            chunk_size = 1024 * 1024       # 1MB块
            
        copied_size = 0
        last_update_time = time.time()
        last_progress_log = 0  # 上次记录进度的时间
        update_interval = 0.2  # 减少更新频率到200ms
        
        # 对于大文件，显示开始拷贝信息
        if file_size > 50 * 1024 * 1024:
            self.log_message(f"📁 开始拷贝大文件: {os.path.basename(source_file)} ({self.copy_manager.format_size(file_size)})")
        
        try:
            # 使用缓冲IO提高性能
            with open(source_file, 'rb', buffering=chunk_size) as src:
                with open(dest_file, 'wb', buffering=chunk_size) as dst:
                    while True:
                        if not self.copy_manager.copying:
                            break
                            
                        # 读取数据块
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                            
                        # 写入数据块
                        dst.write(chunk)
                        copied_size += len(chunk)
                        
                        # 按间隔更新进度，避免过于频繁
                        current_time = time.time()
                        if current_time - last_update_time >= update_interval:
                            # 对于大文件，记录进度百分比（减少日志频率）
                            if file_size > 100 * 1024 * 1024 and current_time - last_progress_log >= 10:  # 每10秒记录一次
                                progress_percent = (copied_size / file_size) * 100
                                self.log_message(f"⏳ 拷贝进度: {progress_percent:.1f}% ({self.copy_manager.format_size(copied_size)}/{self.copy_manager.format_size(file_size)})")
                                last_progress_log = current_time
                            
                            # 批量更新进度（减少UI更新频率）
                            if self.copy_manager.total_size > 0:
                                file_progress_ratio = copied_size / file_size if file_size > 0 else 0
                                temp_copied_size = self.copy_manager.copied_size + (file_size * file_progress_ratio)
                                temp_copied_size = min(temp_copied_size, self.copy_manager.total_size)
                                
                                # 只在有显著变化时更新UI
                                if abs(temp_copied_size - self.copy_manager.copied_size) > (self.copy_manager.total_size * 0.01):  # 变化超过1%
                                    original_copied_size = self.copy_manager.copied_size
                                    self.copy_manager.copied_size = temp_copied_size
                                    self.update_progress()
                                    self.copy_manager.copied_size = original_copied_size
                            
                            self.window.update()  # 刷新界面
                            last_update_time = current_time
                            
        except Exception as e:
            # 如果分块拷贝失败，回退到标准拷贝
            self.log_message(f"分块拷贝失败，回退到标准拷贝: {str(e)}")
            shutil.copy2(source_file, dest_file)
    
    def copy_folder(self, source_path, dest_path, folder_name):
        """拷贝文件夹"""
        import time
        target_path = os.path.join(dest_path, folder_name)
        
        # 调试信息：路径构建
        self.log_message(f"📁 拷贝文件夹信息:")
        self.log_message(f"   源路径: {source_path}")
        self.log_message(f"   目标基础路径: {dest_path}")
        self.log_message(f"   文件夹名称: {folder_name}")
        self.log_message(f"   完整目标路径: {target_path}")
        
        os.makedirs(target_path, exist_ok=True)
        
        for root, dirs, files in os.walk(source_path):
            if not self.copy_manager.copying:
                break
                
            # 创建子目录
            rel_path = os.path.relpath(root, source_path)
            if rel_path == '.':
                current_dest = target_path
            else:
                current_dest = os.path.join(target_path, rel_path)
                
            # 调试信息：相对路径处理
            self.log_message(f"📂 相对路径处理:")
            self.log_message(f"   源根目录: {source_path}")
            self.log_message(f"   当前源目录: {root}")
            self.log_message(f"   相对路径: {rel_path}")
            self.log_message(f"   目标根目录: {target_path}")
            self.log_message(f"   当前目标目录: {current_dest}")
                
            # 调试信息：目录创建
            self.log_message(f"📂 创建目录: {current_dest}")
            try:
                os.makedirs(current_dest, exist_ok=True)
                self.log_message(f"   ✅ 目录创建成功: {current_dest}")
                self.log_message(f"   📍 目录存在: {os.path.exists(current_dest)}")
            except Exception as e:
                self.log_message(f"   ❌ 目录创建失败: {current_dest} - {str(e)}")
            
            # 拷贝文件
            for file in files:
                if not self.copy_manager.copying:
                    break
                    
                source_file = os.path.join(root, file)
                dest_file = os.path.join(current_dest, file)
                
                if self.only_media_var.get() and not self.is_media_file(source_file):
                    continue
                
                try:
                    # 获取文件大小
                    file_size = os.path.getsize(source_file)
                    copy_start = time.time()
                    
                    # 调试信息
                    self.log_message(f"📁 拷贝文件: {file}")
                    self.log_message(f"   从: {source_file}")
                    self.log_message(f"   到: {dest_file}")
                    
                    # 分块拷贝文件，支持实时进度更新
                    self.copy_file_with_progress(source_file, dest_file, file_size)
                    
                    # 验证拷贝结果
                    if os.path.exists(dest_file):
                        self.log_message(f"   ✅ 拷贝成功: {file}")
                        # 验证文件大小
                        source_size = os.path.getsize(source_file)
                        dest_size = os.path.getsize(dest_file)
                        if source_size == dest_size:
                            self.log_message(f"   ✅ 文件大小匹配: {source_size} bytes")
                        else:
                            self.log_message(f"   ⚠️ 文件大小不匹配: 源={source_size}, 目标={dest_size}")
                    else:
                        self.log_message(f"   ❌ 拷贝后文件不存在: {file}")
                        # 检查父目录
                        parent_dir = os.path.dirname(dest_file)
                        self.log_message(f"   📍 父目录: {parent_dir}")
                        self.log_message(f"   📂 父目录存在: {os.path.exists(parent_dir)}")
                        if os.path.exists(parent_dir):
                            files = os.listdir(parent_dir)
                            self.log_message(f"   📄 父目录内容: {files}")
                    
                    # 文件拷贝完成，更新进度
                    copy_time = time.time() - copy_start
                    self.copy_manager.copied_files += 1
                    
                    # 确保总大小正确（在文件拷贝完成后更新总大小）
                    self.copy_manager.copied_size += file_size
                    
                    # 计算速度
                    if copy_time > 0:
                        file_speed = file_size / copy_time  # 字节/秒
                        self.copy_manager.copy_speed = file_speed
                    
                    self.update_progress()
                    self.log_message(f"已拷贝: {file} ({self.copy_manager.format_size(file_size)})")
                except Exception as e:
                    self.log_message(f"拷贝失败 {file}: {str(e)}")
                    
    def verify_files(self):
        """验证文件"""
        import time
        self.copy_manager.verifying = True
        self.copy_manager.verify_start_time = time.time()
        self.copy_manager.md5_start_time = time.time()  # MD5验证开始时间
        self.copy_manager.md5_verified_files = 0
        self.copy_manager.md5_calc_size = 0
        
        # 统计需要验证的文件总数
        total_files = 0
        for source_item in self.source_items:
            for root, dirs, files in os.walk(source_item['path']):
                total_files += len(files)
        self.copy_manager.total_md5_files = total_files
        
        self.log_message(f"开始MD5验证，共 {total_files} 个文件...")
        
        # 构建与拷贝时相同的目标路径
        if self.auto_folder_var.get():
            # 使用拷贝时保存的日期文件夹，确保时间戳一致
            if self.copy_manager.date_folder is not None:
                final_dest = os.path.join(self.destination_path, self.copy_manager.date_folder)
            else:
                # 如果date_folder不存在，生成新的（这种情况不应该发生）
                final_dest = self.destination_path
        else:
            final_dest = self.destination_path
        
        # 这里应该实现MD5验证逻辑
        # 简化版本：只检查文件是否存在
        for source_item in self.source_items:
            if not self.copy_manager.copying:
                break
                
            source_path = source_item['path']
            # 使用与拷贝时相同的路径构建逻辑，包括自定义名称
            folder_name = source_item.get('custom_name', source_item['name'])
            dest_path = os.path.join(final_dest, folder_name)
            
            # 调试信息：验证路径
            self.log_message(f"🔍 验证路径构建:")
            self.log_message(f"   源项目路径: {source_item['path']}")
            self.log_message(f"   源项目名称: {source_item['name']}")
            self.log_message(f"   最终目标路径: {final_dest}")
            self.log_message(f"   验证目标路径: {dest_path}")
            if self.auto_folder_var.get() and self.copy_manager.date_folder:
                self.log_message(f"   使用日期文件夹: {self.copy_manager.date_folder}")
                
            self.verify_folder(source_path, dest_path)
            
        # 验证完成，显示总结
        import time
        elapsed_time = time.time() - self.copy_manager.md5_start_time
        if elapsed_time > 0:
            self.copy_manager.md5_calc_speed = self.copy_manager.md5_calc_size / elapsed_time
        
        self.log_message("\n" + "="*60)
        self.log_message("🎉 MD5验证完成！")
        self.log_message(f"📊 验证统计:")
        self.log_message(f"   总文件数: {self.copy_manager.total_md5_files}")
        self.log_message(f"   验证成功: {self.copy_manager.verified_files}")
        self.log_message(f"   验证失败: {self.copy_manager.total_md5_files - self.copy_manager.verified_files}")
        self.log_message(f"   总数据量: {self.copy_manager.format_size(self.copy_manager.md5_calc_size)}")
        self.log_message(f"   用时: {self.copy_manager.format_time(int(elapsed_time))}")
        self.log_message(f"   平均速度: {self.copy_manager.format_size(int(self.copy_manager.md5_calc_speed))}/s")
        self.log_message("="*60)
        
        self.copy_manager.verifying = False
        
    def verify_folder(self, source_path, dest_path):
        """验证文件夹"""
        from md5_verifier import MD5Verifier
        verifier = MD5Verifier()
        
        for root, dirs, files in os.walk(source_path):
            if not self.copy_manager.copying:
                break
                
            rel_path = os.path.relpath(root, source_path)
            if rel_path == '.':
                current_dest = dest_path
            else:
                current_dest = os.path.join(dest_path, rel_path)
                
            for file in files:
                if not self.copy_manager.copying:
                    break
                    
                source_file = os.path.join(root, file)
                dest_file = os.path.join(current_dest, file)
                
                # 更新MD5验证进度
                self.copy_manager.md5_verified_files += 1
                
                # 计算文件大小用于速度统计
                try:
                    file_size = os.path.getsize(source_file)
                    self.copy_manager.md5_calc_size += file_size
                except:
                    file_size = 0
                
                # 调试信息
                self.log_message(f"🔍 检查文件: {file}")
                self.log_message(f"   源路径: {source_file}")
                self.log_message(f"   目标路径: {dest_file}")
                self.log_message(f"   目标存在: {os.path.exists(dest_file)}")
                
                if os.path.exists(dest_file):
                    try:
                        # 计算MD5验证进度和速度
                        import time
                        elapsed_time = time.time() - self.copy_manager.md5_start_time
                        # 确保时间不为负数（防止系统时间被修改）
                        if elapsed_time < 0:
                            self.log_message(f"⚠️ 检测到负MD5时间: {elapsed_time:.2f}s，重置为0")
                            elapsed_time = 0
                        if elapsed_time > 0:
                            self.copy_manager.md5_calc_speed = self.copy_manager.md5_calc_size / elapsed_time
                        
                        md5_progress = (self.copy_manager.md5_verified_files / self.copy_manager.total_md5_files) * 100
                        
                        # 使用MD5验证文件 - 显示详细进度
                        self.log_message(f"🔍 [{md5_progress:.1f}%] 开始MD5验证: {file}")
                        self.log_message(f"   进度: {self.copy_manager.md5_verified_files}/{self.copy_manager.total_md5_files} 文件")
                        self.log_message(f"   速度: {self.copy_manager.format_size(int(self.copy_manager.md5_calc_speed))}/s")
                        
                        # 计算源文件MD5
                        self.log_message(f"   计算源文件MD5...")
                        source_md5 = verifier.calculate_md5(source_file)
                        self.log_message(f"   源MD5: {source_md5}")
                        
                        # 计算目标文件MD5
                        self.log_message(f"   计算目标文件MD5...")
                        dest_md5 = verifier.calculate_md5(dest_file)
                        self.log_message(f"   目标MD5: {dest_md5}")
                        
                        # 对比MD5值
                        if source_md5 == dest_md5:
                            self.copy_manager.verified_files += 1
                            self.update_verify_progress()
                            self.log_message(f"   ✅ MD5匹配: {file}")
                            self.log_message(f"      哈希值: {source_md5}")
                        else:
                            self.log_message(f"   ❌ MD5不匹配: {file}")
                            self.log_message(f"      源哈希: {source_md5}")
                            self.log_message(f"      目标哈希: {dest_md5}")
                            
                    except Exception as e:
                        self.log_message(f"   ❌ MD5验证错误: {file} - {str(e)}")
                        self.log_message(f"      错误详情: {str(e)}")
                else:
                    self.log_message(f"⚠️ 文件不存在: {file}")
                    # 检查父目录是否存在
                    parent_dir = os.path.dirname(dest_file)
                    self.log_message(f"   父目录存在: {os.path.exists(parent_dir)}")
                    if os.path.exists(parent_dir):
                        # 列出父目录中的文件
                        try:
                            files_in_dir = os.listdir(parent_dir)
                            self.log_message(f"   父目录中的文件: {files_in_dir}")
                        except:
                            self.log_message(f"   无法读取父目录")
                    
    def update_progress(self):
        """更新拷贝进度"""
        import time
        if self.copy_manager.total_files > 0:
            # 文件进度
            file_progress = (self.copy_manager.copied_files / self.copy_manager.total_files) * 100
            self.copy_progress.config(value=file_progress)
            
            # 大小进度
            size_progress = 0
            if self.copy_manager.total_size > 0:
                size_progress = (self.copy_manager.copied_size / self.copy_manager.total_size) * 100
            
            # 时间计算
            elapsed_time = 0
            if self.copy_manager.copy_start_time > 0:
                elapsed_time = time.time() - self.copy_manager.copy_start_time
                # 确保时间不为负数（防止系统时间被修改）
                if elapsed_time < 0:
                    self.log_message(f"⚠️ 检测到负时间: {elapsed_time:.2f}s，重置为0")
                    elapsed_time = 0
            
            # 速度计算
            speed_mb_s = 0
            if elapsed_time > 0 and self.copy_manager.copied_size >= 0:
                speed_mb_s = (self.copy_manager.copied_size / (1024 * 1024)) / elapsed_time
                # 确保速度不为负数
                speed_mb_s = max(0, speed_mb_s)
            
            # 调试信息：如果速度异常，记录详细信息
            if speed_mb_s < 0 or speed_mb_s > 10000:  # 异常速度（负数或超过10GB/s）
                self.log_message(f"⚠️ 速度异常: {speed_mb_s:.2f} MB/s")
                self.log_message(f"   已拷贝大小: {self.copy_manager.copied_size} bytes ({self.copy_manager.format_size(self.copy_manager.copied_size)})")
                self.log_message(f"   总大小: {self.copy_manager.total_size} bytes ({self.copy_manager.format_size(self.copy_manager.total_size)})")
                self.log_message(f"   已用时间: {elapsed_time:.2f} seconds")
                self.log_message(f"   开始时间: {self.copy_manager.copy_start_time}")
                self.log_message(f"   当前时间: {time.time()}")
            
            # 预估剩余时间
            eta_seconds = 0
            if speed_mb_s > 0 and self.copy_manager.total_size > self.copy_manager.copied_size:
                remaining_mb = (self.copy_manager.total_size - self.copy_manager.copied_size) / (1024 * 1024)
                eta_seconds = remaining_mb / speed_mb_s
            
            # 格式化时间显示
            elapsed_str = self.format_time(elapsed_time)
            eta_str = self.format_time(eta_seconds)
            
            # 更新状态标签
            self.copy_status_label.config(
                text=f"已拷贝 {self.copy_manager.copied_files}/{self.copy_manager.total_files} 个文件 ({file_progress:.1f}%)"
            )
            self.copy_speed_label.config(
                text=f"速度: {speed_mb_s:.1f} MB/s | 已用: {elapsed_str} | 剩余: {eta_str}"
            )
            
            self.update_stats()
            
    def update_verify_progress(self):
        """更新验证进度"""
        import time
        if self.copy_manager.total_files > 0:
            # 文件进度
            file_progress = (self.copy_manager.verified_files / self.copy_manager.total_files) * 100
            self.verify_progress.config(value=file_progress)
            
            # 时间计算
            elapsed_time = 0
            if self.copy_manager.verify_start_time > 0:
                elapsed_time = time.time() - self.copy_manager.verify_start_time
                # 确保时间不为负数（防止系统时间被修改）
                if elapsed_time < 0:
                    self.log_message(f"⚠️ 检测到负验证时间: {elapsed_time:.2f}s，重置为0")
                    elapsed_time = 0
            
            # 速度计算（基于文件数量估算）
            verify_speed = 0
            if elapsed_time > 0:
                verify_speed = self.copy_manager.verified_files / elapsed_time  # 文件/秒
            
            # 预估剩余时间
            eta_seconds = 0
            if verify_speed > 0 and self.copy_manager.total_files > self.copy_manager.verified_files:
                remaining_files = self.copy_manager.total_files - self.copy_manager.verified_files
                eta_seconds = remaining_files / verify_speed
            
            # 格式化时间显示
            elapsed_str = self.format_time(elapsed_time)
            eta_str = self.format_time(eta_seconds)
            
            # 更新状态标签
            self.verify_status_label.config(
                text=f"已验证 {self.copy_manager.verified_files}/{self.copy_manager.total_files} 个文件 ({file_progress:.1f}%)"
            )
            self.verify_speed_label.config(
                text=f"速度: {verify_speed:.1f} 文件/秒 | 已用: {elapsed_str} | 剩余: {eta_str}"
            )
            
            self.update_stats()
            
    def update_stats(self):
        """更新统计信息"""
        self.total_files_label.config(text=f"总文件数: {self.copy_manager.total_files}")
        self.copied_files_label.config(text=f"已拷贝: {self.copy_manager.copied_files}")
        self.verified_files_label.config(text=f"已验证: {self.copy_manager.verified_files}")
        
    def copy_complete(self):
        """拷贝完成"""
        self.log_message("拷贝和验证完成！")
        self.copy_progress.config(value=100)
        self.verify_progress.config(value=100)
        self.copy_status_label.config(text="拷贝完成！")
        self.verify_status_label.config(text="验证完成！")
        
        # 仅媒体拷贝提示
        try:
            if hasattr(self, "only_media_var") and self.only_media_var.get():
                messagebox.showwarning(
                    "提示",
                    "已开启“仅拷贝媒体文件”。请注意：文档、工程、缓存等非媒体文件可能未被拷贝。\n\n"
                    "建议立即核对源与目标文件夹，确认是否需要补拷。"
                )
        except Exception:
            pass
        
        # 关闭日志文件
        self.copy_manager.close_log_file()
        
        # 计算统计信息
        total_time = 0
        avg_speed = 0
        if self.copy_manager.copy_start_time > 0:
            total_time = time.time() - self.copy_manager.copy_start_time
            if total_time > 0 and self.copy_manager.copied_size > 0:
                avg_speed = (self.copy_manager.copied_size / (1024 * 1024)) / total_time
        
        # 验证状态
        verify_status = "已完成" if self.copy_manager.verified_files > 0 else "未验证"
        if self.copy_manager.verified_files > 0 and self.copy_manager.total_files > 0:
            verify_status = f"已完成 ({self.copy_manager.verified_files}/{self.copy_manager.total_files})"
        
        # 显示增强版庆祝动画
        self.celebrate_completion_with_stats(
            total_files=self.copy_manager.total_files,
            total_size=self.copy_manager.copied_size,
            avg_speed=avg_speed,
            total_time=total_time,
            verify_status=verify_status
        )
        
    def copy_stopped(self):
        """拷贝被停止"""
        self.log_message("拷贝已停止")
        self.copy_status_label.config(text="拷贝已停止")
        self.verify_status_label.config(text="验证已停止")
        
        # 关闭日志文件
        self.copy_manager.close_log_file()
    
    def open_log_viewer(self):
        """打开日志查看器"""
        try:
            # 在打开日志查看器之前，确保主窗口图标已设置
            self.restore_main_window_icon()
            
            log_viewer = LogViewerWindow()
            log_viewer.mainloop()
            
            # 日志查看器关闭后，重新设置主窗口图标以确保一致性
            self.restore_main_window_icon()
        except Exception as e:
            messagebox.showerror("错误", f"无法打开日志查看器: {str(e)}")
    
    def restore_main_window_icon(self):
        """恢复主窗口图标 - 增强版本"""
        try:
            icon_path = get_icon_path()
            if icon_path and 'PIL_Image' in globals() and 'PIL_ImageTk' in globals():
                icon_image = PIL_Image.open(icon_path)
                self.icon_photo = PIL_ImageTk.PhotoImage(icon_image)  # 重新创建图标引用
                
                # 使用多种方法设置图标，确保兼容性
                if self.window:
                    self.window.wm_iconphoto(True, self.icon_photo)
                    if hasattr(self.window, 'iconphoto'):
                        self.window.iconphoto(True, self.icon_photo)
                    
                    # 额外：强制刷新窗口属性
                    self.window.update_idletasks()
        except Exception as e:
            print(f"恢复主窗口图标失败: {e}")
            pass  # 如果恢复失败，保持当前状态
    
    def open_official_website(self, event=None):
        """打开官方网站"""
        try:
            import webbrowser
            webbrowser.open("https://dit.superjia.com.cn")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开官网: {str(e)}")
        
    def celebrate_completion_with_stats(self, total_files, total_size, avg_speed, total_time, verify_status):
        """增强版庆祝完成动画，包含统计信息"""
        # 创建庆祝窗口
        celebrate_window = tk.Toplevel(self.window)
        celebrate_window.title("🎉 拷贝完成！")
        celebrate_window.geometry("500x400")
        celebrate_window.transient(self.window)
        celebrate_window.configure(bg="#1e1e1e")
        
        # 居中显示
        celebrate_window.update_idletasks()
        x = (celebrate_window.winfo_screenwidth() // 2) - (celebrate_window.winfo_width() // 2)
        y = (celebrate_window.winfo_screenheight() // 2) - (celebrate_window.winfo_height() // 2)
        celebrate_window.geometry(f"+{x}+{y}")
        
        # 阻止窗口关闭按钮（用户必须通过按钮操作）
        celebrate_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # 主框架
        main_frame = ttk.Frame(celebrate_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # 庆祝标题
        title_label = ttk.Label(
            main_frame,
            text="🎉 拷贝完成！ 🎉",
            font=("Arial", 28, "bold"),
            bootstyle="success",
            anchor="center"
        )
        title_label.pack(pady=(0, 20))
        
        # 统计信息框架
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill="both", expand=True, pady=10)
        
        # 文件数量
        files_label = ttk.Label(
            stats_frame,
            text=f"📁 文件数量: {total_files} 个",
            font=("Arial", 12),
            bootstyle="info"
        )
        files_label.pack(anchor="w", pady=5)
        
        # 总大小
        size_label = ttk.Label(
            stats_frame,
            text=f"💾 总大小: {self.copy_manager.format_size(total_size)}",
            font=("Arial", 12),
            bootstyle="info"
        )
        size_label.pack(anchor="w", pady=5)
        
        # 平均速度
        speed_label = ttk.Label(
            stats_frame,
            text=f"⚡ 平均速度: {avg_speed:.1f} MB/s",
            font=("Arial", 12),
            bootstyle="info"
        )
        speed_label.pack(anchor="w", pady=5)
        
        # 总用时
        time_label = ttk.Label(
            stats_frame,
            text=f"⏱️ 总用时: {self.format_time(total_time)}",
            font=("Arial", 12),
            bootstyle="info"
        )
        time_label.pack(anchor="w", pady=5)
        
        # 验证状态
        verify_label = ttk.Label(
            stats_frame,
            text=f"✅ 验证状态: {verify_status}",
            font=("Arial", 12),
            bootstyle="success"
        )
        verify_label.pack(anchor="w", pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # 打开目标文件夹按钮
        open_folder_btn = ttk.Button(
            button_frame,
            text="📂 打开目标文件夹",
            bootstyle="info-outline",
            command=lambda: self.open_destination_folder(celebrate_window)
        )
        open_folder_btn.pack(side="left", padx=(0, 10))
        
        # 确定按钮
        ok_btn = ttk.Button(
            button_frame,
            text="确定",
            bootstyle="success",
            command=celebrate_window.destroy
        )
        ok_btn.pack(side="right")
        
        # 设置按钮焦点
        ok_btn.focus()
        
        # 绑定回车键关闭窗口
        celebrate_window.bind("<Return>", lambda e: celebrate_window.destroy())
        
        # 确保窗口在最前面
        celebrate_window.lift()
        celebrate_window.attributes('-topmost', True)
        celebrate_window.after(100, lambda: celebrate_window.attributes('-topmost', False))
    
    def open_destination_folder(self, parent_window):
        """打开目标文件夹"""
        try:
            if self.destination_path and os.path.exists(self.destination_path):
                if os.name == 'nt':  # Windows
                    os.startfile(self.destination_path)
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.run(['open', self.destination_path])
                parent_window.destroy()  # 打开文件夹后关闭庆祝窗口
            else:
                messagebox.showwarning("警告", "目标文件夹不存在！")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目标文件夹: {str(e)}")
        
    def clear_all(self):
        """清空所有选择"""
        self.source_items.clear()
        self.source_items_listbox.delete(0, tk.END)
        self.destination_path = ""
        self.dest_path_label.config(text="未选择目的地")
        self.dest_info_label.config(text="")
        self.log_text.delete(1.0, tk.END)
        
        # 重置进度
        self.copy_progress.config(value=0)
        self.verify_progress.config(value=0)
        self.copy_status_label.config(text="等待开始拷贝...")
        self.verify_status_label.config(text="等待拷贝完成...")
        
        self.copy_manager.total_files = 0
        self.copy_manager.copied_files = 0
        self.copy_manager.verified_files = 0
        self.update_stats()
        
    def log_message(self, message):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.window.update()
        
        # 同时写入日志文件
        if self.copy_manager.log_file:
            self.copy_manager.write_log(message)

class LogViewerWindow:
    """日志查看器窗口"""
    
    def __init__(self):
        """初始化日志查看器 - 完全避免默认图标闪烁"""
        
        # 确保重量级模块已导入
        if 'tb' not in globals() or tb is None:
            import_heavy_modules()
        
        # 预加载图标
        preload_icon()
        self.icon_photo = None
        
        # 创建窗口但先隐藏，避免显示默认图标
        self.window = tb.Window(
            title="日志查看器 - CardCopyer-拷贝乐",
            themename="darkly",
            size=(1200, 800),
            resizable=(True, True)
        )
        
        # 立即隐藏窗口，防止显示默认图标
        self.window.withdraw()
        
        # 尝试立即设置图标（窗口隐藏状态下）
        try:
            icon_image = get_global_icon_image()
            if icon_image and 'PIL_ImageTk' in globals():
                self.icon_photo = PIL_ImageTk.PhotoImage(icon_image, master=self.window)
                self.window.wm_iconphoto(True, self.icon_photo)
                if hasattr(self.window, 'iconphoto'):
                    self.window.iconphoto(True, self.icon_photo)
                print("日志查看器图标在隐藏状态下设置成功")
        except Exception as e:
            print(f"隐藏状态下设置图标失败: {e}")
        
        self.log_dir = get_log_directory()
        self.current_log_file = None
        self.current_log_content = ""
        
        # 设置UI（窗口仍在隐藏状态）
        self.setup_ui()
        self.load_log_files()
        
        # 延迟显示窗口，确保图标已完全设置
        self.window.after(100, self._show_window_with_icon)
    
    def _show_window_with_icon(self):
        """显示窗口并确保图标正确设置"""
        try:
            # 尝试设置图标
            if not self.icon_photo:
                icon_image = get_global_icon_image()
                if icon_image and 'PIL_ImageTk' in globals():
                    self.icon_photo = PIL_ImageTk.PhotoImage(icon_image, master=self.window)
                    self.window.wm_iconphoto(True, self.icon_photo)
                    if hasattr(self.window, 'iconphoto'):
                        self.window.iconphoto(True, self.icon_photo)
            
            # 显示窗口
            self.window.deiconify()
            print("日志查看器窗口已显示")
            
            # 启动图标监控定时器
            if self.icon_photo:
                self._start_icon_monitor()
                
        except Exception as e:
            print(f"显示窗口时设置图标失败: {e}")
            # 即使图标设置失败，也要显示窗口
            self.window.deiconify()
    
    def _set_window_icon(self):
        """延迟设置日志查看器窗口图标，使用全局图标确保一致性"""
        try:
            # 使用全局图标管理器获取Image对象
            icon_image = get_global_icon_image()
            
            if icon_image and self.window:
                # 为当前窗口创建专用的PhotoImage
                if 'PIL_ImageTk' in globals():
                    self.icon_photo = PIL_ImageTk.PhotoImage(icon_image, master=self.window)
                    
                    # 使用多种方法设置图标，确保兼容性
                    self.window.wm_iconphoto(True, self.icon_photo)
                    if hasattr(self.window, 'iconphoto'):
                        self.window.iconphoto(True, self.icon_photo)
                    
                    # 启动图标监控定时器
                    self._start_icon_monitor()
            elif not icon_image:
                # 如果全局图标不可用，尝试本地创建
                icon_path = get_icon_path()
                if icon_path and 'PIL_Image' in globals() and 'PIL_ImageTk' in globals():
                    icon_image = PIL_Image.open(icon_path)
                    self.icon_photo = PIL_ImageTk.PhotoImage(icon_image, master=self.window)
                    if self.window and self.icon_photo:
                        self.window.wm_iconphoto(True, self.icon_photo)
                        if hasattr(self.window, 'iconphoto'):
                            self.window.iconphoto(True, self.icon_photo)
                        
                        # 启动图标监控定时器
                        self._start_icon_monitor()
        except Exception as e:
            print(f"设置日志查看器图标失败: {e}")
            pass
        
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = tb.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # 标题
        title_label = tb.Label(
            main_frame,
            text="日志查看器",
            font=("Arial", 20, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))
        
        # 主要内容区域 - 左右分栏
        content_frame = tb.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # 左侧 - 日志文件列表
        left_frame = tb.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tb.Label(left_frame, text="历史日志文件:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # 日志文件列表框架
        list_frame = tb.Frame(left_frame)
        list_frame.pack(fill="both", expand=True)
        
        # 滚动条
        list_scroll = tb.Scrollbar(list_frame)
        list_scroll.pack(side="right", fill="y")
        
        self.log_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=list_scroll.set,
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white",
            selectbackground="#005a9e",
            height=20
        )
        self.log_listbox.pack(side="left", fill="both", expand=True)
        list_scroll.config(command=self.log_listbox.yview)
        
        # 绑定选择事件
        self.log_listbox.bind('<<ListboxSelect>>', self.on_log_selected)
        
        # 右侧 - 日志内容显示
        right_frame = tb.Frame(content_frame)
        right_frame.pack(side="left", fill="both", expand=True)
        
        tb.Label(right_frame, text="日志内容:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # 日志信息显示框架
        info_frame = tb.Frame(right_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.log_info_label = tb.Label(
            info_frame,
            text="请选择一个日志文件",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.log_info_label.pack(side="left")
        
        # 日志内容显示
        content_frame = tb.Frame(right_frame)
        content_frame.pack(fill="both", expand=True)
        
        content_scroll = tb.Scrollbar(content_frame)
        content_scroll.pack(side="right", fill="y")
        
        self.log_content_text = tk.Text(
            content_frame,
            yscrollcommand=content_scroll.set,
            font=("Courier", 9),
            bg="#1e1e1e",
            fg="white",
            wrap=tk.WORD,
            height=25,
            width=60
        )
        self.log_content_text.pack(side="left", fill="both", expand=True)
        content_scroll.config(command=self.log_content_text.yview)
        
        # 底部按钮区域
        bottom_frame = tb.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=(20, 0))
        
        # 刷新按钮
        refresh_btn = tb.Button(
            bottom_frame,
            text="刷新日志列表",
            bootstyle="info-outline",
            command=self.load_log_files
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # 导出按钮
        export_btn = tb.Button(
            bottom_frame,
            text="导出日志",
            bootstyle="success-outline",
            command=self.export_log
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        # 删除按钮
        delete_btn = tb.Button(
            bottom_frame,
            text="删除日志",
            bootstyle="danger-outline",
            command=self.delete_log
        )
        delete_btn.pack(side="left")
        
        # 关闭按钮
        close_btn = tb.Button(
            bottom_frame,
            text="关闭",
            bootstyle="secondary",
            command=self.window.destroy
        )
        close_btn.pack(side="right")
        
    def load_log_files(self):
        """加载日志文件列表"""
        self.log_listbox.delete(0, tk.END)
        
        try:
            if os.path.exists(self.log_dir):
                log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
                log_files.sort(reverse=True)  # 最新的在前
                
                for log_file in log_files:
                    # 获取文件信息
                    file_path = os.path.join(self.log_dir, log_file)
                    file_size = os.path.getsize(file_path)
                    file_time = os.path.getmtime(file_path)
                    file_date = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M')
                    
                    # 显示格式：文件名 (大小, 日期)
                    size_str = self.format_size(file_size)
                    display_text = f"{log_file} ({size_str}, {file_date})"
                    self.log_listbox.insert(tk.END, display_text)
                    
                if log_files:
                    self.log_info_label.config(text=f"找到 {len(log_files)} 个日志文件")
                else:
                    self.log_info_label.config(text="暂无日志文件")
            else:
                self.log_info_label.config(text="日志目录不存在")
                
        except Exception as e:
            self.log_info_label.config(text=f"加载日志文件失败: {str(e)}")
    
    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def on_log_selected(self, event):
        """选择日志文件时的处理"""
        selection = self.log_listbox.curselection()
        if not selection:
            return
            
        try:
            # 获取选中的日志文件名
            selected_text = self.log_listbox.get(selection[0])
            log_filename = selected_text.split(' (')[0]  # 提取文件名
            
            # 读取日志内容
            log_path = os.path.join(self.log_dir, log_filename)
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_log_file = log_filename
            self.current_log_content = content
            
            # 显示日志内容
            self.log_content_text.delete(1.0, tk.END)
            self.log_content_text.insert(1.0, content)
            
            # 更新信息标签
            file_size = os.path.getsize(log_path)
            file_time = os.path.getmtime(log_path)
            file_date = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
            
            info_text = f"文件名: {log_filename} | 大小: {self.format_size(file_size)} | 修改时间: {file_date}"
            self.log_info_label.config(text=info_text)
            
        except Exception as e:
            self.log_info_label.config(text=f"读取日志文件失败: {str(e)}")
            self.log_content_text.delete(1.0, tk.END)
            self.log_content_text.insert(1.0, f"错误: 无法读取日志文件\n\n{str(e)}")
    
    def export_log(self):
        """导出当前选中的日志"""
        if not self.current_log_file or not self.current_log_content:
            messagebox.showwarning("提示", "请先选择一个日志文件")
            return
            
        # 选择导出位置
        export_path = filedialog.asksaveasfilename(
            title="导出日志",
            initialfile=self.current_log_file,
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if export_path:
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_log_content)
                messagebox.showinfo("成功", f"日志已导出到:\n{export_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出日志失败:\n{str(e)}")
    
    def delete_log(self):
        """删除当前选中的日志"""
        if not self.current_log_file:
            messagebox.showwarning("提示", "请先选择一个日志文件")
            return
            
        result = messagebox.askyesno(
            "确认删除",
            f"确定要删除日志文件:\n{self.current_log_file}?\n\n此操作不可恢复。"
        )
        
        if result:
            try:
                log_path = os.path.join(self.log_dir, self.current_log_file)
                os.remove(log_path)
                messagebox.showinfo("成功", "日志文件已删除")
                
                # 清空显示
                self.log_content_text.delete(1.0, tk.END)
                self.current_log_file = None
                self.current_log_content = ""
                
                # 重新加载列表
                self.load_log_files()
                
            except Exception as e:
                messagebox.showerror("错误", f"删除日志文件失败:\n{str(e)}")
    
    def mainloop(self):
        """运行日志查看器主循环 - 增强图标一致性"""
        try:
            # 确保窗口图标已正确设置 - 使用全局图标确保一致性
            global_icon = get_global_icon_photo()
            if global_icon and self.window:
                self.icon_photo = global_icon
                # 延迟设置以避免初始化问题
                self.window.after(100, lambda: self._apply_window_icon())
            
            # 运行主循环
            self.window.mainloop()
        except Exception as e:
            print(f"日志查看器主循环错误: {e}")
            raise
    
    def _apply_window_icon(self):
        """应用窗口图标 - 分离方法以确保可靠性"""
        try:
            if self.window and self.icon_photo:
                self.window.wm_iconphoto(True, self.icon_photo)
                if hasattr(self.window, 'iconphoto'):
                    self.window.iconphoto(True, self.icon_photo)
        except Exception as e:
            print(f"应用窗口图标失败: {e}")
    
    def _start_icon_monitor(self):
        """启动图标监控定时器，防止图标被系统重置"""
        def check_and_restore_icon():
            try:
                # 检查图标是否仍然有效
                if self.window and self.icon_photo:
                    # 重新应用图标
                    self.window.wm_iconphoto(True, self.icon_photo)
                    if hasattr(self.window, 'iconphoto'):
                        self.window.iconphoto(True, self.icon_photo)
                
                # 每5秒检查一次
                self.window.after(5000, check_and_restore_icon)
            except Exception:
                pass
        
        # 启动第一次检查
        self.window.after(5000, check_and_restore_icon)


def show_startup_error(message, detail=""):
    """显示启动错误对话框"""
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showerror("启动错误", f"{message}\n\n{detail}")
    root.destroy()

def main():
    """主函数 - 优化启动流程"""
    startup_window = None
    
    try:
        # 预加载图标，确保在窗口创建前就可用了
        startup_window = StartupWindow()
        startup_window.update_progress("正在预加载图标...")
        
        # 在后台线程中预加载图标
        def preload_icon_in_background():
            try:
                preload_success = preload_icon()
                if preload_success:
                    startup_window.update_progress("图标预加载成功...")
                else:
                    startup_window.update_progress("图标预加载失败，将使用默认设置...")
            except Exception as e:
                print(f"图标预加载异常: {e}")
                startup_window.update_progress("图标预加载异常，继续启动...")
        
        # 立即开始图标预加载
        threading.Thread(target=preload_icon_in_background, daemon=True).start()
        
        # 快速依赖检查
        startup_window.update_progress("正在检查依赖...")
        if not quick_check_dependencies():
            startup_window.close()
            return
        
        # 在后台线程中进行完整依赖检查
        def check_deps_in_background():
            success, error_msg = full_check_dependencies()
            if not success:
                startup_window.close()
                show_startup_error("依赖检查失败", error_msg)
                return
            
            # 依赖检查通过后，启动主应用
            startup_window.update_progress("正在加载界面...")
            
            # 关闭启动窗口
            if startup_window:
                startup_window.close()
            
            # 创建主应用
            app = DITCopyTool()
            app.window.mainloop()
        
        # 延迟启动依赖检查，让图标预加载先完成
        startup_window.root.after(800, check_deps_in_background)
        
        # 运行启动窗口的主循环
        startup_window.root.mainloop()
        
    except KeyboardInterrupt:
        if startup_window:
            startup_window.close()
    except Exception as e:
        if startup_window:
            startup_window.close()
        show_startup_error("程序启动失败", str(e))

if __name__ == "__main__":
    main()
