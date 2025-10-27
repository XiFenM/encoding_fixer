#!/usr/bin/env python3
"""
File Comparison Tool - Compare txt file contents between chinese_old and chinese directories
"""

import os
import hashlib
import filecmp
from pathlib import Path
from typing import Dict, List, Tuple


class FileComparator:
    def __init__(self, old_dir: str, new_dir: str):
        self.old_dir = Path(old_dir)
        self.new_dir = Path(new_dir)
        self.comparison_results: Dict[str, Dict] = {}
        self.pdf_comparison_results: Dict[str, Dict] = {}
        
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except Exception as e:
            print(f"Error getting size for {file_path}: {e}")
            return 0
    
    def compare_txt_files(self) -> Dict[str, Dict]:
        """Compare txt files between the two directories"""
        print("正在对比txt文件内容...")
        print("-" * 60)
        
        # 获取chinese_old目录中的所有txt文件
        old_txt_files = list(self.old_dir.glob("*.txt"))
        
        for old_file in old_txt_files:
            file_name = old_file.name
            new_file = self.new_dir / file_name
            
            result = {
                "file_name": file_name,
                "old_file_path": str(old_file),
                "new_file_path": str(new_file) if new_file.exists() else None,
                "exists_in_new": new_file.exists(),
                "identical": False,
                "size_match": False,
                "hash_match": False,
                "old_size": self.get_file_size(old_file),
                "new_size": 0,
                "old_hash": "",
                "new_hash": ""
            }
            
            if new_file.exists():
                # 计算两个文件的大小和哈希值
                result["new_size"] = self.get_file_size(new_file)
                result["old_hash"] = self.get_file_hash(old_file)
                result["new_hash"] = self.get_file_hash(new_file)
                
                # 检查是否完全一致
                result["size_match"] = result["old_size"] == result["new_size"]
                result["hash_match"] = result["old_hash"] == result["new_hash"]
                result["identical"] = result["size_match"] and result["hash_match"]
            
            self.comparison_results[file_name] = result
            
            # 打印结果
            if not new_file.exists():
                print(f"❌ {file_name}: 在chinese目录中不存在")
            elif result["identical"]:
                print(f"✅ {file_name}: 完全一致")
            else:
                differences = []
                if not result["size_match"]:
                    differences.append(f"大小不同 ({result['old_size']} vs {result['new_size']} 字节)")
                if not result["hash_match"]:
                    differences.append("内容不同")
                print(f"❌ {file_name}: {', '.join(differences)}")
        
        return self.comparison_results
    
    def compare_pdf_files(self) -> Dict[str, Dict]:
        """Compare PDF files (specifically 鬼穴 files) by size"""
        print("\n正在对比PDF文件大小...")
        print("-" * 60)
        
        # 查找鬼穴PDF文件
        old_ghost_pit = list(self.old_dir.glob("*鬼穴*.pdf"))
        new_ghost_pit = list(self.new_dir.glob("*鬼穴*.pdf"))
        
        if not old_ghost_pit:
            print("❌ chinese_old目录中未找到鬼穴PDF文件")
            return {}
        
        if not new_ghost_pit:
            print("❌ chinese目录中未找到鬼穴PDF文件")
            return {}
        
        old_file = old_ghost_pit[0]
        new_file = new_ghost_pit[0]
        
        old_size = self.get_file_size(old_file)
        new_size = self.get_file_size(new_file)
        
        result = {
            "old_file": str(old_file),
            "new_file": str(new_file),
            "old_size": old_size,
            "new_size": new_size,
            "size_match": old_size == new_size,
            "size_difference": abs(old_size - new_size)
        }
        
        self.pdf_comparison_results["鬼穴.pdf"] = result
        
        if result["size_match"]:
            print(f"✅ 鬼穴PDF文件: 大小完全一致 ({old_size} 字节)")
        else:
            print(f"❌ 鬼穴PDF文件: 大小不同 (chinese_old: {old_size} 字节, chinese: {new_size} 字节, 差异: {result['size_difference']} 字节)")
        
        return self.pdf_comparison_results
    
    def generate_summary_report(self) -> str:
        """生成详细的对比报告"""
        report = []
        report.append("文件对比报告")
        report.append("=" * 60)
        
        # txt文件对比总结
        total_txt_files = len(self.comparison_results)
        identical_files = sum(1 for r in self.comparison_results.values() if r["identical"])
        missing_files = sum(1 for r in self.comparison_results.values() if not r["exists_in_new"])
        different_files = sum(1 for r in self.comparison_results.values() if r["exists_in_new"] and not r["identical"])
        
        report.append(f"\nTXT文件对比总结:")
        report.append(f"chinese_old目录中的txt文件总数: {total_txt_files}")
        report.append(f"完全一致的文件: {identical_files}")
        report.append(f"chinese目录中缺失的文件: {missing_files}")
        report.append(f"内容不同的文件: {different_files}")
        
        if missing_files > 0:
            report.append("\n缺失的文件:")
            for file_name, result in self.comparison_results.items():
                if not result["exists_in_new"]:
                    report.append(f"  - {file_name}")
        
        if different_files > 0:
            report.append("\n内容不同的文件:")
            for file_name, result in self.comparison_results.items():
                if result["exists_in_new"] and not result["identical"]:
                    report.append(f"  - {file_name}")
        
        # PDF文件对比总结
        if self.pdf_comparison_results:
            report.append(f"\nPDF文件对比总结:")
            for pdf_name, result in self.pdf_comparison_results.items():
                if result["size_match"]:
                    report.append(f"✅ {pdf_name}: 大小完全一致")
                else:
                    report.append(f"❌ {pdf_name}: 大小不同 (差异: {result['size_difference']} 字节)")
        
        return "\n".join(report)
    
    def run_comparison(self):
        """运行完整的对比流程"""
        print("开始对比chinese_old和chinese目录中的文件...")
        print("=" * 60)
        
        # 对比txt文件
        self.compare_txt_files()
        
        # 对比PDF文件
        self.compare_pdf_files()
        
        # 生成并打印报告
        print("\n" + "=" * 60)
        report = self.generate_summary_report()
        print(report)
        
        return report


def main():
    # 设置目录路径
    chinese_old_dir = "/app/Xeelee_Sequence/chinese_old"
    chinese_dir = "/app/Xeelee_Sequence/chinese"
    
    # 检查目录是否存在
    if not os.path.exists(chinese_old_dir):
        print(f"错误: 目录 {chinese_old_dir} 不存在")
        return
    
    if not os.path.exists(chinese_dir):
        print(f"错误: 目录 {chinese_dir} 不存在")
        return
    
    # 创建对比器并运行对比
    comparator = FileComparator(chinese_old_dir, chinese_dir)
    comparator.run_comparison()


if __name__ == "__main__":
    main()