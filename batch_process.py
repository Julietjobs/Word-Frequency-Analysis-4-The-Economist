#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量处理The Economist电子书文件，转换为txt并统计词频
"""

import os
import re
import csv
from collections import Counter
from pathlib import Path
import epub2txt
import mobi2txt


def find_ebook_files(base_dir):
    """
    查找所有的EPUB和MOBI文件
    
    Args:
        base_dir: 基础目录路径
        
    Returns:
        文件路径列表
    """
    ebook_files = []
    base_path = Path(base_dir)
    
    # 查找所有epub和mobi文件
    for ext in ['*.epub', '*.mobi', '*.EPUB', '*.MOBI']:
        ebook_files.extend(base_path.rglob(ext))
    
    # 去重（Windows文件系统不区分大小写可能导致重复）
    ebook_files = list(dict.fromkeys(ebook_files))
    
    return sorted(ebook_files)


def convert_ebook_to_txt(ebook_path, txt_dir):
    """
    将电子书转换为txt文件
    
    Args:
        ebook_path: 电子书文件路径
        txt_dir: txt输出目录
        
    Returns:
        输出的txt文件路径，如果失败则返回None
    """
    ebook_path = Path(ebook_path)
    base_name = ebook_path.stem
    
    # 保持目录结构
    relative_path = ebook_path.parent.relative_to(ebook_path.parent.parent)
    output_dir = Path(txt_dir) / relative_path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{base_name}.txt"
    
    # 如果txt文件已存在，跳过转换
    if output_path.exists():
        print(f"文件已存在，跳过: {output_path}")
        return output_path
    
    # 根据文件扩展名选择转换函数
    ext = ebook_path.suffix.lower()
    
    try:
        if ext == '.epub':
            success = epub2txt.convert_epub_to_txt(str(ebook_path), str(output_path))
        elif ext == '.mobi':
            success = mobi2txt.convert_mobi_to_txt(str(ebook_path), str(output_path))
        else:
            print(f"不支持的文件格式: {ebook_path}")
            return None
        
        if success:
            return output_path
        else:
            return None
    
    except Exception as e:
        print(f"转换失败 {ebook_path}: {str(e)}")
        return None


def extract_words(text):
    """
    从文本中提取单词
    
    Args:
        text: 文本内容
        
    Returns:
        单词列表
    """
    # 转换为小写
    text = text.lower()
    
    # 使用正则表达式提取单词（只保留字母）
    words = re.findall(r'\b[a-z]+\b', text)
    
    # 过滤掉太短的单词（如单字母）
    words = [word for word in words if len(word) >= 3]
    
    return words


def count_word_frequency(txt_files):
    """
    统计所有txt文件中的单词频率
    
    Args:
        txt_files: txt文件路径列表
        
    Returns:
        Counter对象，包含单词频率统计
    """
    word_counter = Counter()
    
    for txt_file in txt_files:
        if txt_file and os.path.exists(txt_file):
            try:
                print(f"统计词频: {txt_file}")
                with open(txt_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                words = extract_words(text)
                word_counter.update(words)
            
            except Exception as e:
                print(f"读取文件失败 {txt_file}: {str(e)}")
    
    return word_counter


def save_frequency_to_csv(word_counter, output_path):
    """
    将词频统计结果保存为CSV文件
    
    Args:
        word_counter: Counter对象
        output_path: 输出CSV文件路径
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 按频率降序排序
    sorted_words = word_counter.most_common()
    
    # 写入CSV文件
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'Frequency', 'Rank'])
        
        for rank, (word, freq) in enumerate(sorted_words, 1):
            writer.writerow([word, freq, rank])
    
    print(f"\n词频统计已保存到: {output_path}")
    print(f"总共统计了 {len(sorted_words)} 个不同的单词")
    print(f"总词数: {sum(word_counter.values())}")


def main():
    """
    主函数
    """
    print("=" * 60)
    print("The Economist 词频统计程序")
    print("=" * 60)
    
    # 配置路径
    ebook_dir = 'C:/Users/Jobs/Downloads/TheEcoEpub'
    # ebook_dir = 'TheEconomist'
    txt_dir = 'txt'
    output_csv = 'WordFrequency/word_frequency_all.csv'
    log_file_path = 'WordFrequency/conversion_log.txt'
    
    # 创建日志文件
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    log_file = open(log_file_path, 'w', encoding='utf-8')
    
    # 1. 查找所有电子书文件
    print("\n步骤1: 查找电子书文件...")
    ebook_files = find_ebook_files(ebook_dir)
    print(f"找到 {len(ebook_files)} 个电子书文件")
    
    if not ebook_files:
        print("未找到任何电子书文件，程序退出")
        log_file.close()
        return
    
    # 2. 转换所有电子书为txt
    print("\n步骤2: 转换电子书为TXT文件...")
    print("=" * 60)
    txt_files = []
    for i, ebook_file in enumerate(ebook_files, 1):
        print(f"\n[{i}/{len(ebook_files)}] 处理: {ebook_file.name}")
        txt_file = convert_ebook_to_txt(ebook_file, txt_dir)
        if txt_file:
            txt_files.append(txt_file)
            # 显示txt文件统计信息
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    char_count = len(content)
                    word_count = len(content.split())
                log_msg = f"  ✓ {txt_file.name}:\n    字符数: {char_count:,}\n    单词数: {word_count:,}\n"
                print(log_msg, end='')
                log_file.write(f"[{i}/{len(ebook_files)}] {ebook_file.name}\n{log_msg}\n")
            except Exception as e:
                msg = f"  ✓ 转换完成: {txt_file.name}\n"
                print(msg, end='')
                log_file.write(f"[{i}/{len(ebook_files)}] {ebook_file.name}\n{msg}\n")
    print("\n" + "=" * 60)
    
    print(f"\n成功转换 {len(txt_files)} 个文件")
    
    if not txt_files:
        print("没有成功转换的文件，程序退出")
        log_file.close()
        return
    
    # 3. 统计词频
    print("\n步骤3: 统计词频...")
    word_counter = count_word_frequency(txt_files)
    
    # 4. 保存结果
    print("\n步骤4: 保存结果...")
    save_frequency_to_csv(word_counter, output_csv)
    
    # 显示前20个高频词
    print("\n前20个高频词:")
    print("-" * 40)
    for rank, (word, freq) in enumerate(word_counter.most_common(20), 1):
        print(f"{rank:2d}. {word:15s} - {freq:6d} 次")
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print("=" * 60)
    
    # 关闭日志文件
    log_file.close()
    print(f"\n日志已保存到: {log_file_path}")


if __name__ == '__main__':
    main()

