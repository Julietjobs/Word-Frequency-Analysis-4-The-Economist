#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将EPUB格式的电子书转换为纯文本文件
"""

import sys
import os
from ebooklib import epub
from bs4 import BeautifulSoup


def epub_to_text(epub_path):
    """
    将EPUB文件转换为文本内容
    
    Args:
        epub_path: EPUB文件路径
        
    Returns:
        提取的文本内容
    """
    try:
        book = epub.read_epub(epub_path)
        text_content = []
        
        # 遍历所有项目
        for item in book.get_items():
            # 处理文档项 (类型9) 和 HTML文件 (类型0)
            # 类型9: ITEM_DOCUMENT (旧格式EPUB)
            # 类型0: 未分类项，包括2025年新格式的HTML文件
            if item.get_type() == 9:  # ITEM_DOCUMENT
                # 获取HTML内容
                html_content = item.get_content()
                # 使用BeautifulSoup解析HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                # 提取纯文本
                text = soup.get_text(separator=' ', strip=True)
                if text:
                    text_content.append(text)
            elif item.get_type() == 0:  # 未分类项
                # 只处理HTML文件，跳过其他文件（如toc.html、cover等）
                name = item.get_name().lower()
                if name.endswith(('.html', '.htm', '.xhtml')) and 'toc' not in name and 'nav' not in name and 'cover' not in name:
                    try:
                        html_content = item.get_content()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        # 只添加有实质内容的文本（长度>100字符）
                        if text and len(text) > 100:
                            text_content.append(text)
                    except:
                        # 如果某个文件解析失败，跳过继续处理其他文件
                        pass
        
        return '\n\n'.join(text_content)
    
    except Exception as e:
        print(f"错误：处理文件 {epub_path} 时出错: {str(e)}")
        return None


def convert_epub_to_txt(epub_path, output_path):
    """
    将EPUB文件转换为TXT文件
    
    Args:
        epub_path: EPUB文件路径
        output_path: 输出TXT文件路径
    """
    print(f"正在转换: {epub_path}")
    
    text = epub_to_text(epub_path)
    
    if text:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入文本文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"转换完成: {output_path}")
        return True
    else:
        print(f"转换失败: {epub_path}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python epub2txt.py <epub文件路径> [输出txt文件路径]")
        sys.exit(1)
    
    epub_file = sys.argv[1]
    
    if not os.path.exists(epub_file):
        print(f"错误：文件不存在 - {epub_file}")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # 默认输出到txt目录
        base_name = os.path.splitext(os.path.basename(epub_file))[0]
        output_file = os.path.join('txt', base_name + '.txt')
    
    convert_epub_to_txt(epub_file, output_file)

