# 三国演义字频统计系统

基于Python的文本分析系统，统计《三国演义》中汉字出现频率。

## 项目结构

```
sanguo-char-frequency/
├── src/
│   ├── char_frequency_analyzer.py  # 分析引擎
│   └── web_app.py                  # Flask Web应用
├── templates/index.html            # Web界面
├── results/                        # 输出结果
├── run_web.py                     # 启动脚本
├── test_quick.py                  # 测试脚本
└── requirements.txt               # 依赖
```

## 核心模块

### CharFrequencyAnalyzer
- 汉字提取与频率统计
- 智能编码检测 (UTF-8/GBK/GB2312)
- 大文件分块处理 (50MB+)
- 输出: JSON报告、CSV数据、可视化图表

### WebApp
- RESTful API: `POST /api/analyze`, `GET /api/demo`
- 文件大小限制: 16MB

## 技术栈

- Python 3.13 + Flask 3.1.1
- pandas 2.3.1 + numpy 2.3.1
- matplotlib 3.10.3
- chardet 5.2.0

## 快速开始

```bash
pip install -r requirements.txt
python run_web.py
```

访问: http://localhost:5000

## 核心算法

### 汉字提取
```python
chinese_pattern = r'[\u4e00-\u9fff]'
chinese_chars = re.findall(chinese_pattern, text)
```

### 频率统计
```python
char_counter = Counter(chars)
top_chars = char_counter.most_common(n)
```

### 大文件处理
```python
chunk_size = 1024 * 1024  # 1MB
while True:
    chunk = f.read(chunk_size)
    if not chunk: break
    content_parts.append(chunk)
```

## 性能特性

- 内存优化: 分块处理大文件
- 编码兼容: 多编码自动检测
- 异常恢复: 多层异常处理

## 输出格式

### JSON报告
```json
{
  "basic_stats": {"total_characters": 1000000, "unique_characters": 5000},
  "top_characters": [["的", 15000], ["了", 12000]],
  "analysis_time": "2024-01-15 10:30:00"
}
```

## 工程化状态

### 已实现
- ✅ 边界条件处理
- ✅ 性能优化
- ✅ 异常恢复机制
- ✅ 模块化设计

### 待优化
- ⚠️ 并发安全性
- ⚠️ 监控系统
- ⚠️ 配置管理
- ⚠️ 资源管理 