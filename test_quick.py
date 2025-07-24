#!/usr/bin/env python3
import sys
import os
import tempfile
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from char_frequency_analyzer import CharFrequencyAnalyzer, AnalysisConfig

def main():
    print("🎯 快速测试分析器...")
    
    demo_text = "三国演义是中国古典四大名著之一。三国演义描述了从东汉末年到西晋初年之间近百年的历史风云。" * 20
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(demo_text)
        temp_path = f.name
    
    try:
        config = AnalysisConfig(top_n=10, save_results=True, generate_charts=True)
        analyzer = CharFrequencyAnalyzer(config)
        results = analyzer.analyze(temp_path)
        
        print(f"\n✅ 测试成功！")
        print(f"总字符数: {results['basic_stats']['total_characters']}")
        print(f"最高频字符: '{results['top_characters'][0][0]}' ({results['top_characters'][0][1]} 次)")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    main()
