"""
MD5验证模块
用于文件完整性验证
"""

import hashlib
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import json

class MD5Verifier:
    """MD5验证器"""
    
    def __init__(self):
        self.checksums = {}  # 存储文件校验和
        
    def calculate_md5(self, file_path: str, chunk_size: int = 8192) -> str:
        """
        计算文件的MD5值
        
        Args:
            file_path: 文件路径
            chunk_size: 分块大小
            
        Returns:
            MD5哈希值
        """
        md5_hash = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            raise Exception(f"计算MD5失败 {file_path}: {str(e)}")
    
    def verify_file(self, source_path: str, dest_path: str) -> Tuple[bool, str]:
        """
        验证两个文件是否相同
        
        Args:
            source_path: 源文件路径
            dest_path: 目标文件路径
            
        Returns:
            (是否相同, 错误信息)
        """
        try:
            source_md5 = self.calculate_md5(source_path)
            dest_md5 = self.calculate_md5(dest_path)
            
            if source_md5 == dest_md5:
                return True, ""
            else:
                return False, f"MD5不匹配: 源={source_md5}, 目标={dest_md5}"
                
        except Exception as e:
            return False, f"验证失败: {str(e)}"
    
    def create_checksum_file(self, folder_path: str, output_file: str = None) -> str:
        """
        为文件夹创建校验和文件
        
        Args:
            folder_path: 文件夹路径
            output_file: 输出文件路径（可选）
            
        Returns:
            校验和文件路径
        """
        if output_file is None:
            output_file = os.path.join(folder_path, "checksums.md5")
            
        checksums = {}
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file == "checksums.md5":  # 跳过已有的校验和文件
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, folder_path)
                
                try:
                    md5_hash = self.calculate_md5(file_path)
                    checksums[rel_path] = md5_hash
                except Exception as e:
                    print(f"计算MD5失败 {file_path}: {str(e)}")
                    
        # 保存校验和文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for rel_path, md5_hash in checksums.items():
                    f.write(f"{md5_hash}  {rel_path}\n")
            return output_file
        except Exception as e:
            raise Exception(f"保存校验和文件失败: {str(e)}")
    
    def load_checksum_file(self, checksum_file: str) -> Dict[str, str]:
        """
        加载校验和文件
        
        Args:
            checksum_file: 校验和文件路径
            
        Returns:
            文件路径到MD5的映射字典
        """
        checksums = {}
        
        try:
            with open(checksum_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('  ', 1)  # 使用两个空格分隔
                        if len(parts) == 2:
                            md5_hash, file_path = parts
                            checksums[file_path] = md5_hash
                            
        except Exception as e:
            raise Exception(f"加载校验和文件失败: {str(e)}")
            
        return checksums
    
    def verify_folder(self, source_folder: str, dest_folder: str, create_checksums: bool = True) -> Dict[str, Tuple[bool, str]]:
        """
        验证两个文件夹是否相同
        
        Args:
            source_folder: 源文件夹
            dest_folder: 目标文件夹
            create_checksums: 是否创建校验和文件
            
        Returns:
            验证结果字典
        """
        results = {}
        
        # 为源文件夹创建校验和文件
        if create_checksums:
            try:
                source_checksum_file = self.create_checksum_file(source_folder)
                print(f"创建源文件夹校验和文件: {source_checksum_file}")
            except Exception as e:
                print(f"创建源文件夹校验和文件失败: {str(e)}")
                
        # 获取源文件夹的所有文件
        source_files = {}
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file == "checksums.md5":
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_folder)
                source_files[rel_path] = file_path
        
        # 验证每个文件
        for rel_path, source_file in source_files.items():
            dest_file = os.path.join(dest_folder, rel_path)
            
            if not os.path.exists(dest_file):
                results[rel_path] = (False, "目标文件不存在")
                continue
                
            is_valid, error_msg = self.verify_file(source_file, dest_file)
            results[rel_path] = (is_valid, error_msg)
            
        return results
    
    def get_file_info(self, file_path: str) -> Dict[str, any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'md5': self.calculate_md5(file_path)
            }
        except Exception as e:
            raise Exception(f"获取文件信息失败: {str(e)}")

def test_md5_verifier():
    """测试MD5验证器"""
    verifier = MD5Verifier()
    
    # 创建测试文件
    test_file = "test_file.txt"
    with open(test_file, 'w') as f:
        f.write("这是一个测试文件\n")
        
    try:
        # 计算MD5
        md5_hash = verifier.calculate_md5(test_file)
        print(f"文件MD5: {md5_hash}")
        
        # 验证文件
        is_valid, error_msg = verifier.verify_file(test_file, test_file)
        print(f"文件验证结果: {is_valid}, {error_msg}")
        
        # 创建校验和文件
        checksum_file = verifier.create_checksum_file(".")
        print(f"校验和文件: {checksum_file}")
        
        # 加载校验和文件
        checksums = verifier.load_checksum_file(checksum_file)
        print(f"加载的校验和: {checksums}")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists("checksums.md5"):
            os.remove("checksums.md5")

if __name__ == "__main__":
    test_md5_verifier()