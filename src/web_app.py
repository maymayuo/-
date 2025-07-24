#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import os
import tempfile
import sys
import traceback

# 确保可以导入分析器
sys.path.append(os.path.dirname(__file__))
from char_frequency_analyzer import CharFrequencyAnalyzer, AnalysisConfig

# 创建Flask应用，指定template目录
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            content = file.read().decode('utf-8')
            f.write(content)
            temp_path = f.name
        
        try:
            config = AnalysisConfig(top_n=50, save_results=False, generate_charts=False)
            analyzer = CharFrequencyAnalyzer(config)
            results = analyzer.analyze(temp_path)
            return jsonify({'success': True, 'results': results})
        finally:
            os.unlink(temp_path)
        
    except Exception as e:
        print(f"分析错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo')
def demo_analysis():
    try:
        # demo_text = """
        # 话说天下大势，分久必合，合久必分。周末七国分争，并入于秦。
        # 及秦灭后，楚、汉分争，又并入于汉。汉朝自高祖斩白蛇而起义，
        # 一统天下，后来光武中兴，传至献帝，遂分为三国。推其致乱之由，
        # 殆始于桓、灵二帝。桓帝禁锢善类，崇信阉宦。及桓帝崩，灵帝即位，
        # 大将军窦武、太傅陈蕃共相辅佐。时有宦官曹节等弄权，窦武、陈蕃谋诛之，
        # 机事不密，反为所害，中涓自此愈横。建宁二年四月望日，帝御温德殿。
        # 方升座，殿角狂风骤起。只见一条大青蛇，从梁上飞将下来，蟠于椅上。
        # 帝惊倒，左右急救入宫，百官俱奔避。须臾，蛇不见了。忽然大雷大雨，
        # 加以冰雹，落到半夜方止，坏却宫殿门窗。中平元年，张角自称天公将军，
        # 其弟张宝称地公将军，张梁称人公将军。角以太平道为名，私造谶书。
        # """ * 50

        demo_text = """
        今今天是星期三
        """* 50
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(demo_text)
            temp_path = f.name
        
        try:
            config = AnalysisConfig(top_n=20, save_results=False, generate_charts=False)
            analyzer = CharFrequencyAnalyzer(config)
            results = analyzer.analyze(temp_path)
            return jsonify({'success': True, 'results': results})
        finally:
            os.unlink(temp_path)
        
    except Exception as e:
        print(f"演示错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print(f"Template目录: {template_dir}")
    app.run(host='127.0.0.1', port=5000, debug=True)