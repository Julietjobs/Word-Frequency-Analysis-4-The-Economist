#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将MOBI格式的电子书转换为纯文本文件
"""

import sys
import os
import subprocess
import tempfile
from bs4 import BeautifulSoup


def extract_text_with_kindleunpack(mobi_path):
    """
    使用KindleUnpack提取MOBI内容
    
    Args:
        mobi_path: MOBI文件路径
        
    Returns:
        提取的文本内容
    """
    try:
        # 尝试导入KindleUnpack
        try:
            # 如果有mobi包，使用它
            import mobi
            tempdir, filepath = mobi.extract(mobi_path)
            
            # 读取提取的HTML文件
            html_files = []
            for root, dirs, files in os.walk(tempdir):
                for file in files:
                    if file.endswith(('.html', '.htm', '.xhtml')):
                        html_files.append(os.path.join(root, file))
            
            if html_files:
                text_parts = []
                for html_file in html_files:
                    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                        html_content = f.read()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        if text:
                            text_parts.append(text)
                
                # 清理临时目录
                import shutil
                shutil.rmtree(tempdir, ignore_errors=True)
                
                return '\n\n'.join(text_parts) if text_parts else None
        except ImportError:
            pass
        
        return None
    
    except Exception as e:
        print(f"KindleUnpack方法失败: {str(e)}")
        return None


def mobi_to_text_via_converter(mobi_path):
    """
    使用ebook-convert工具将MOBI转换为文本
    需要安装Calibre
    
    Args:
        mobi_path: MOBI文件路径
        
    Returns:
        提取的文本内容
    """
    try:
        # 创建临时txt文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
            tmp_path = tmp_file.name
        
        # 使用ebook-convert转换
        cmd = ['ebook-convert', mobi_path, tmp_path, '--txt-output-encoding=utf-8']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(tmp_path):
            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            os.unlink(tmp_path)
            return text if text else None
        else:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return None
    
    except FileNotFoundError:
        print("提示：未找到ebook-convert工具。如需处理更多MOBI文件，请安装Calibre。")
        return None
    except Exception as e:
        print(f"ebook-convert方法失败: {str(e)}")
        return None


def mobi_to_text(mobi_path):
    """
    将MOBI文件转换为文本内容，尝试多种方法
    
    Args:
        mobi_path: MOBI文件路径
        
    Returns:
        提取的文本内容
    """
    # 首先尝试使用mobi包
    print("尝试使用mobi库提取...")
    text = extract_text_with_kindleunpack(mobi_path)
    if text and len(text) > 100:
        print("mobi库提取成功！")
        return text
    
    # 如果失败，尝试使用ebook-convert（需要安装Calibre）
    print("尝试使用ebook-convert工具...")
    text = mobi_to_text_via_converter(mobi_path)
    if text and len(text) > 100:
        print("ebook-convert转换成功！")
        return text
    
    print(f"\n警告：无法转换文件 {mobi_path}")
    print("建议：")
    print("  1. 安装mobi包: pip install mobi")
    print("  2. 或安装Calibre软件: https://calibre-ebook.com/download")
    return None


def convert_mobi_to_txt(mobi_path, output_path):
    """
    将MOBI文件转换为TXT文件
    
    Args:
        mobi_path: MOBI文件路径
        output_path: 输出TXT文件路径
    """
    print(f"正在转换: {mobi_path}")
    
    text = mobi_to_text(mobi_path)
    
    if text:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入文本文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"转换完成: {output_path}")
        return True
    else:
        print(f"转换失败: {mobi_path}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python mobi2txt.py <mobi文件路径> [输出txt文件路径]")
        sys.exit(1)
    
    mobi_file = sys.argv[1]
    
    if not os.path.exists(mobi_file):
        print(f"错误：文件不存在 - {mobi_file}")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # 默认输出到txt目录
        base_name = os.path.splitext(os.path.basename(mobi_file))[0]
        output_file = os.path.join('txt', base_name + '.txt')
    
    convert_mobi_to_txt(mobi_file, output_file)

