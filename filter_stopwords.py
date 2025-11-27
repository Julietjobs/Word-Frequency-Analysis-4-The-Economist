#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
过滤停用词，生成更适合学习的词汇表
"""

import csv
from pathlib import Path


# 英语常见停用词列表
COMMON_STOPWORDS = {
    # 冠词
    'a', 'an', 'the',
    # 代词
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
    'this', 'that', 'these', 'those', 'who', 'which', 'what', 'whom', 'whose',
    # 连词
    'and', 'but', 'or', 'nor', 'for', 'yet', 'so', 'because', 'if', 'when', 'while',
    'although', 'though', 'unless', 'until', 'since', 'before', 'after',
    # 介词
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'from', 'by', 'about', 'as',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down',
    'out', 'off', 'over', 'under', 'between', 'among', 'against', 'through',
    # Be动词和助动词
    'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'will', 'would', 'shall', 'should', 'may', 'might', 'can', 'could', 'must',
    # 其他常见词
    'not', 'no', 'yes', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'than', 'too', 'very', 'just', 'also', 'only',
    'own', 'same', 'so', 'then', 'there', 'here', 'where', 'how', 'why',
    'now', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    # The Economist常见格式词
    'section', 'sections', 'article', 'articles', 'print', 'edition', 'next',
    'mr', 'ms', 'mrs', 'dr', 'st'
}


def load_custom_stopwords(file_path):
    """
    从文件加载自定义停用词
    
    Args:
        file_path: 停用词文件路径（每行一个词）
    
    Returns:
        set: 停用词集合
    """
    stopwords = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    stopwords.add(word)
    except FileNotFoundError:
        pass
    
    return stopwords


def filter_word_frequency_csv(
    input_csv,
    output_csv,
    stopwords=None,
    min_freq=1,
    max_freq=float('inf'),
    min_length=3,
    top_n=None
):
    """
    过滤词频CSV文件
    
    Args:
        input_csv: 输入CSV文件路径
        output_csv: 输出CSV文件路径
        stopwords: 停用词集合（如果为None，使用默认停用词）
        min_freq: 最小词频阈值
        max_freq: 最大词频阈值
        min_length: 最小单词长度
        top_n: 只保留前N个单词（在过滤后）
    """
    if stopwords is None:
        stopwords = COMMON_STOPWORDS
    
    input_path = Path(input_csv)
    if not input_path.exists():
        print(f"错误: 文件不存在 - {input_csv}")
        return
    
    print(f"处理文件: {input_path.name}")
    print("=" * 80)
    
    # 读取并过滤数据
    filtered_words = []
    total_words = 0
    filtered_count = 0
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row['Word']
            freq = int(row['Frequency'])
            total_words += 1
            
            # 应用过滤条件
            if word in stopwords:
                filtered_count += 1
                continue
            if len(word) < min_length:
                filtered_count += 1
                continue
            if freq < min_freq or freq > max_freq:
                filtered_count += 1
                continue
            
            filtered_words.append((word, freq))
    
    # 如果指定了top_n，只保留前N个
    if top_n is not None and top_n > 0:
        filtered_words = filtered_words[:top_n]
    
    # 保存过滤后的数据
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'Frequency', 'Rank'])
        
        for rank, (word, freq) in enumerate(filtered_words, 1):
            writer.writerow([word, freq, rank])
    
    print(f"原始单词数: {total_words}")
    print(f"过滤掉: {filtered_count}")
    print(f"保留: {len(filtered_words)}")
    print(f"\n过滤后的词频已保存到: {output_csv}")
    
    # 显示前50个单词
    print("\n前50个学习词汇:")
    print("-" * 80)
    for rank, (word, freq) in enumerate(filtered_words[:50], 1):
        print(f"{rank:3d}. {word:25s} - {freq:6d} 次")
    
    return filtered_words


def create_study_lists(input_csv, output_prefix="study_list", words_per_level=500):
    """
    根据词频创建分级学习列表
    
    Args:
        input_csv: 输入CSV文件路径
        output_prefix: 输出文件前缀
        words_per_level: 每个级别的单词数
    """
    print("\n" + "=" * 80)
    print("创建分级学习列表...")
    print("=" * 80)
    
    # 先过滤停用词
    temp_csv = "temp_filtered.csv"
    filtered_words = filter_word_frequency_csv(
        input_csv,
        temp_csv,
        stopwords=COMMON_STOPWORDS,
        min_length=3
    )
    
    # 分级
    total_words = len(filtered_words)
    num_levels = (total_words + words_per_level - 1) // words_per_level  # 向上取整
    
    print(f"\n总词汇数: {total_words}")
    print(f"每级词汇数: {words_per_level}")
    print(f"总级别数: {num_levels}")
    
    for level in range(num_levels):
        start_idx = level * words_per_level
        end_idx = min((level + 1) * words_per_level, total_words)
        level_words = filtered_words[start_idx:end_idx]
        
        # 保存该级别的单词
        output_file = f"{output_prefix}_level_{level + 1}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Word', 'Frequency', 'Level_Rank', 'Overall_Rank'])
            
            for level_rank, (word, freq) in enumerate(level_words, 1):
                overall_rank = start_idx + level_rank
                writer.writerow([word, freq, level_rank, overall_rank])
        
        print(f"\n级别 {level + 1}: {len(level_words)} 个单词 -> {output_file}")
        print(f"  范围: 第 {start_idx + 1} - {end_idx} 个单词")
        print(f"  示例: {', '.join([word for word, _ in level_words[:10]])}")
    
    # 删除临时文件
    Path(temp_csv).unlink(missing_ok=True)
    
    print("\n" + "=" * 80)
    print("分级学习列表创建完成！")


if __name__ == '__main__':
    import sys
    
    # 示例1: 基本过滤
    print("示例1: 基本过滤（移除停用词，最短3字母）")
    print("=" * 80)
    filter_word_frequency_csv(
        input_csv="2016-01-02_word_frequency.csv",
        output_csv="2016-01-02_learning_vocabulary.csv",
        stopwords=COMMON_STOPWORDS,
        min_freq=5,      # 至少出现5次
        min_length=3     # 至少3个字母
    )
    
    # 示例2: 创建分级学习列表
    print("\n\n示例2: 创建分级学习列表")
    print("=" * 80)
    create_study_lists(
        input_csv="2016-01-02_word_frequency.csv",
        output_prefix="2016-01-02_study",
        words_per_level=500  # 每级500个单词
    )
    
    # 如果有合并后的文件，也处理它
    if Path("all_years_word_frequency.csv").exists():
        print("\n\n示例3: 处理合并后的所有年份词频")
        print("=" * 80)
        filter_word_frequency_csv(
            input_csv="all_years_word_frequency.csv",
            output_csv="all_years_learning_vocabulary.csv",
            stopwords=COMMON_STOPWORDS,
            min_freq=10,     # 至少出现10次（因为是多年合并）
            min_length=3
        )
        
        create_study_lists(
            input_csv="all_years_word_frequency.csv",
            output_prefix="all_years_study",
            words_per_level=500
        )

