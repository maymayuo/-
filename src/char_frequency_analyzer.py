#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三国演义字频统计系统
Author: 校招新人
Date: 2025
Description: 统计《三国演义》中汉字出现频次的完整系统
"""

import re
import json
import logging
import time
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import chardet
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams

# 配置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

@dataclass
class AnalysisConfig:
    """分析配置类"""
    top_n: int = 50
    min_frequency: int = 1
    exclude_punctuation: bool = True
    save_results: bool = True
    generate_charts: bool = True
    chunk_size: int = 1024 * 1024  # 1MB chunks for large files

class CharFrequencyAnalyzer:
    """汉字频率分析器"""
    
    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        self.logger = self._setup_logger()
        self.char_counter = Counter()
        self.analysis_stats = {}
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志系统"""
        logger = logging.getLogger('CharFrequencyAnalyzer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def detect_encoding(self, file_path: Path) -> str:
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB检测编码
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                self.logger.info(f"检测到文件编码: {encoding} (置信度: {confidence:.2f})")
                return encoding or 'utf-8'
        except Exception as e:
            self.logger.warning(f"编码检测失败，使用默认UTF-8: {e}")
            return 'utf-8'
    
    def load_text_file(self, file_path: str) -> str:
        """加载文本文件，支持大文件分块读取"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_size = file_path.stat().st_size
        self.logger.info(f"文件大小: {file_size / (1024*1024):.2f} MB")
        
        encoding = self.detect_encoding(file_path)
        
        try:
            # 对于大文件使用分块读取
            if file_size > 50 * 1024 * 1024:  # 50MB以上
                return self._load_large_file(file_path, encoding)
            else:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    self.logger.info(f"成功加载文件，字符数: {len(content)}")
                    return content
        except UnicodeDecodeError as e:
            self.logger.error(f"文件编码错误: {e}")
            # 尝试其他常见编码
            for fallback_encoding in ['gbk', 'gb2312', 'utf-8', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=fallback_encoding, errors='ignore') as f:
                        content = f.read()
                        self.logger.info(f"使用备用编码 {fallback_encoding} 成功加载")
                        return content
                except:
                    continue
            raise Exception("无法使用任何编码读取文件")
    
    def _load_large_file(self, file_path: Path, encoding: str) -> str:
        """分块加载大文件"""
        self.logger.info("检测到大文件，使用分块加载...")
        content_parts = []
        
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            while True:
                chunk = f.read(self.config.chunk_size)
                if not chunk:
                    break
                content_parts.append(chunk)
        
        content = ''.join(content_parts)
        self.logger.info(f"分块加载完成，总字符数: {len(content)}")
        return content
    
    def extract_chinese_chars(self, text: str) -> List[str]:
        """提取汉字字符"""
        start_time = time.time()
        
        # 汉字Unicode范围
        chinese_pattern = r'[\u4e00-\u9fff]'
        chinese_chars = re.findall(chinese_pattern, text)
        
        # 过滤标点符号（如果配置要求）
        if self.config.exclude_punctuation:
            # 中文标点符号范围
            punctuation_pattern = r'[\u3000-\u303f\uff00-\uffef]'
            chinese_chars = [char for char in chinese_chars 
                           if not re.match(punctuation_pattern, char)]
        
        extract_time = time.time() - start_time
        self.logger.info(f"汉字提取完成，耗时: {extract_time:.2f}秒，提取字符数: {len(chinese_chars)}")
        
        return chinese_chars
    
    def calculate_frequency(self, chars: List[str]) -> Dict[str, int]:
        """计算字符频率"""
        start_time = time.time()
        
        self.char_counter = Counter(chars)
        
        # 过滤低频词
        if self.config.min_frequency > 1:
            self.char_counter = Counter({
                char: count for char, count in self.char_counter.items()
                if count >= self.config.min_frequency
            })
        
        calc_time = time.time() - start_time
        self.logger.info(f"频率计算完成，耗时: {calc_time:.2f}秒，唯一字符数: {len(self.char_counter)}")
        
        return dict(self.char_counter)
    
    def get_top_characters(self, n: int = None) -> List[Tuple[str, int]]:
        """获取频次最高的前N个字符"""
        n = n or self.config.top_n
        return self.char_counter.most_common(n)
    
    def generate_analysis_report(self, chars: List[str]) -> Dict:
        """生成详细分析报告"""
        total_chars = len(chars)
        unique_chars = len(self.char_counter)
        top_chars = self.get_top_characters()
        
        # 统计分析
        frequencies = list(self.char_counter.values())
        
        report = {
            'basic_stats': {
                'total_characters': total_chars,
                'unique_characters': unique_chars,
                'coverage_ratio': unique_chars / total_chars if total_chars > 0 else 0
            },
            'frequency_stats': {
                'max_frequency': max(frequencies) if frequencies else 0,
                'min_frequency': min(frequencies) if frequencies else 0,
                'avg_frequency': sum(frequencies) / len(frequencies) if frequencies else 0
            },
            'top_characters': top_chars,
            'analysis_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.analysis_stats = report
        return report
    
    def save_results(self, report: Dict, output_dir: str = "results"):
        """保存分析结果"""
        if not self.config.save_results:
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 保存JSON格式结果
        json_file = output_path / "character_frequency_analysis.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存CSV格式结果
        csv_file = output_path / "top_characters.csv"
        df = pd.DataFrame(report['top_characters'], columns=['字符', '频次'])
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        self.logger.info(f"结果已保存到: {output_path}")
    
    def generate_visualization(self, output_dir: str = "results"):
        """生成可视化图表"""
        if not self.config.generate_charts:
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        top_chars = self.get_top_characters(20)  # 取前20个
        if not top_chars:
            self.logger.warning("没有数据可供可视化")
            return
        
        chars, frequencies = zip(*top_chars)
        
        # 柱状图
        plt.figure(figsize=(15, 8))
        bars = plt.bar(range(len(chars)), frequencies, color='skyblue', edgecolor='navy', linewidth=0.5)
        plt.xlabel('汉字', fontsize=12)
        plt.ylabel('出现频次', fontsize=12)
        plt.title('《三国演义》汉字频次统计 - 前20名', fontsize=14, fontweight='bold')
        plt.xticks(range(len(chars)), chars, fontsize=11)
        
        # 添加数值标签
        for bar, freq in zip(bars, frequencies):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(frequencies)*0.01,
                    str(freq), ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(output_path / "character_frequency_bar_chart.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 饼图（前10名）
        if len(top_chars) >= 10:
            top_10 = top_chars[:10]
            other_sum = sum(freq for _, freq in top_chars[10:])
            
            pie_chars, pie_freqs = zip(*top_10)
            if other_sum > 0:
                pie_chars += ('其他',)
                pie_freqs += (other_sum,)
            
            plt.figure(figsize=(12, 8))
            plt.pie(pie_freqs, labels=pie_chars, autopct='%1.1f%%', startangle=90)
            plt.title('《三国演义》汉字频次分布 - 前10名', fontsize=14, fontweight='bold')
            plt.axis('equal')
            plt.savefig(output_path / "character_frequency_pie_chart.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        self.logger.info(f"可视化图表已保存到: {output_path}")
    
    def analyze(self, file_path: str) -> Dict:
        """执行完整分析流程"""
        self.logger.info("开始分析《三国演义》字频统计...")
        total_start_time = time.time()
        
        try:
            # 1. 加载文本
            text = self.load_text_file(file_path)
            if not text.strip():
                raise ValueError("文件内容为空")
            
            # 2. 提取汉字
            chinese_chars = self.extract_chinese_chars(text)
            if not chinese_chars:
                raise ValueError("未找到汉字内容")
            
            # 3. 计算频率
            self.calculate_frequency(chinese_chars)
            
            # 4. 生成报告
            report = self.generate_analysis_report(chinese_chars)
            
            # 5. 保存结果
            self.save_results(report)
            
            # 6. 生成可视化
            self.generate_visualization()
            
            total_time = time.time() - total_start_time
            self.logger.info(f"分析完成！总耗时: {total_time:.2f}秒")
            
            # 输出关键结果
            top_char, top_freq = self.get_top_characters(1)[0]
            self.logger.info(f"出现频次最高的汉字是: '{top_char}' (出现 {top_freq} 次)")
            
            return report
            
        except Exception as e:
            self.logger.error(f"分析过程中出现错误: {e}")
            raise

# 使用示例
if __name__ == "__main__":
    # 配置分析参数
    config = AnalysisConfig(
        top_n=50,
        min_frequency=1,
        exclude_punctuation=True,
        save_results=True,
        generate_charts=True
    )
    
    # 创建分析器
    analyzer = CharFrequencyAnalyzer(config)
    
    # 执行分析
    try:
        # 请将 "三国演义.txt" 替换为实际文件路径
        results = analyzer.analyze("三国演义.txt")
        
        # 打印前10个最高频字符
        print("\n" + "="*50)
        print("《三国演义》汉字频次统计结果 - 前10名")
        print("="*50)
        for i, (char, freq) in enumerate(analyzer.get_top_characters(10), 1):
            print(f"{i:2d}. '{char}' - {freq:,} 次")
        print("="*50)
        
    except Exception as e:
        print(f"程序执行出错: {e}")
