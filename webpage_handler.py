# -*- coding = utf-8 -*-
# @time:2024/8/15 15:59
# Author:david yuan
# @File:web_handler.py
# @Software:VeSync

import cv2
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from llm_util import LLMUtil
from preprocess import ImagePreprocessor


class WebpageHandler:
    def __init__(self):
        self.llm_util = LLMUtil()
        self.sample_rate = 1  # 1秒采样一次
        self.preprocessor = ImagePreprocessor()

    def extract_frames(self, video_path):
        """从视频中提取帧"""
        frames = []
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * self.sample_rate)
        
        current_frame = 0
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
                
            if current_frame % frame_interval == 0:
                frames.append(frame)
            current_frame += 1
            
        video.release()
        return frames

    def detect_edges(self, frame):
        """对图片进行边缘检测"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        coordinates = []
        for contour in contours:
            for point in contour:
                x, y = point[0]
                coordinates.append({"x": int(x), "y": int(y)})
        return coordinates

    def generate_json(self, frames_data):
        """生成JSON数据"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "frames": [
                {
                    "frame_id": idx,
                    "timestamp": idx * self.sample_rate,
                    "edges": frame_data
                }
                for idx, frame_data in enumerate(frames_data)
            ]
        }
        return json.dumps(output, indent=2)

    def generate_html(self, json_data):
        """使用不同的CoT策略生成多个HTML版本"""
        
        # 解析JSON数据并创建简化版本
        data = json.loads(json_data)
        simplified_data = {
            "timestamp": data["timestamp"],
            "total_frames": len(data["frames"]),
            "sample_frame": data["frames"][0],  # 只使用第一帧作为示例
            "frame_interval": self.sample_rate
        }
        
        # 基础提示词模板
        base_template = f"""
        Generate an HTML page that visualizes edge detection data from a video.
        The data structure is as follows:
        - Total frames: {simplified_data['total_frames']}
        - Frame interval: {simplified_data['frame_interval']} seconds
        - Each frame contains edge coordinates in format: [{{"x": int, "y": int}}, ...]
        
        Sample frame data:
        {json.dumps(simplified_data['sample_frame'], indent=2)}
        
        Requirements:
        1. A visualization of the edge points
        2. Basic controls for frame navigation
        3. Responsive design
        4. The page should be able to load and parse the full JSON data from 'edges.json'
        """
        
        # 标准 Chain of Thought
        standard_cot_prompt = f"""
        {base_template}
        
        Let's approach this step by step:
        1. First, create the HTML structure and add JSON loading logic
        2. Then, implement the visualization using Canvas/SVG
        3. Add frame navigation controls
        4. Implement responsive design
        5. Add error handling and loading states
        
        Please provide your solution following these steps.
        """
        
        # Tree of Thought
        tree_of_thought_prompt = f"""
        {base_template}
        
        Let's explore multiple possible approaches:
        
        Branch A: SVG-based Visualization
        - A1: Static SVG elements
        - A2: Dynamic SVG with JavaScript
        
        Branch B: Canvas-based Visualization
        - B1: Basic Canvas drawing
        - B2: Animated Canvas
        
        Branch C: Data Management
        - C1: Streaming data loading
        - C2: Batch processing
        
        Choose and implement the most efficient approach.
        """
        
        # Graph of Thought
        graph_of_thought_prompt = f"""
        {base_template}
        
        Consider these interconnected components:
        
        Data Layer:
        - JSON loading and parsing
        - Frame data management
        
        Visualization Layer:
        - Rendering strategy
        - Performance optimization
        
        UI Layer:
        - Controls and navigation
        - Responsive design
        
        Create an implementation that optimally connects these components.
        """
        
        try:
            # 生成不同版本的HTML
            results = {
                'standard_cot': self.llm_util.native_chat(standard_cot_prompt),
                'tree_of_thought': self.llm_util.native_chat(tree_of_thought_prompt),
                'graph_of_thought': self.llm_util.native_chat(graph_of_thought_prompt)
            }
            
            # 保存不同版本
            output_dir = Path('output/html_versions')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for approach, html in results.items():
                file_path = output_dir / f'visualization_{approach}.html'
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html)
            
            # 返回所有生成的文件路径
            return {
                'standard_cot': str(output_dir / 'visualization_standard_cot.html'),
                'tree_of_thought': str(output_dir / 'visualization_tree_of_thought.html'),
                'graph_of_thought': str(output_dir / 'visualization_graph_of_thought.html')
            }
            
        except Exception as e:
            print(f"HTML生成过程中出现错误: {str(e)}")
            # 返回一个基本的错误页面路径
            error_html = """
            <html>
                <body>
                    <h1>Error Generating Visualization</h1>
                    <p>There was an error generating the visualization. Please check the logs.</p>
                </body>
            </html>
            """
            error_path = output_dir / 'visualization_error.html'
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(error_html)
            return {'error': str(error_path)}
    

    def run(self, video_path, output_dir="output"):
        """主处理流程 - 只处理第一帧，结合边缘检测和图片理解"""
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 读取视频第一帧
        video = cv2.VideoCapture(video_path)
        ret, frame = video.read()
        video.release()
        
        if not ret:
            raise Exception("无法读取视频帧")
        
        # 处理这一帧的边缘检测
        edges = self.detect_edges(frame)
        
        # 保存原始帧图像
        frame_path = f"{output_dir}/frame.jpg"
        cv2.imwrite(frame_path, frame)
        
        # 进行完整分析（包括直接分析和基于边缘的分析）
        analysis_results = self.preprocessor.combined_analysis(frame, edges)
        
        # 生成完整的JSON数据
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "frames": [
                {
                    "frame_id": 0,
                    "timestamp": 0,
                    "edges": edges,
                    "analysis": analysis_results
                }
            ]
        }
        
        # 保存JSON
        json_str = json.dumps(json_data, indent=2)
        json_path = f"{output_dir}/edges.json"
        with open(json_path, "w", encoding='utf-8') as f:
            f.write(json_str)
        
        # 生成不同版本的HTML并保存
        html_paths = self.generate_html(json_str)
        
        # 创建一个合并的HTML文件，包含所有分析结果和可视化链接
        combined_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>UI Analysis Results</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2 {{ color: #333; }}
                .section {{
                    margin: 20px 0;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .image-section {{
                    text-align: center;
                }}
                .image-section img {{
                    max-width: 100%;
                    height: auto;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .analysis-section {{
                    background: #f9f9f9;
                }}
                pre {{
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                }}
                .links {{ 
                    margin: 20px 0;
                }}
                a {{ 
                    display: inline-block;
                    margin: 10px;
                    padding: 10px 15px;
                    background: #0066cc;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                a:hover {{
                    background: #0052a3;
                }}
            </style>
        </head>
        <body>
            <h1>UI Analysis Results</h1>
            
            <div class="section image-section">
                <h2>Original Frame</h2>
                <img src="frame.jpg" alt="Original Frame">
            </div>
            
            <div class="section analysis-section">
                <h2>Direct Image Analysis</h2>
                <pre>{analysis_results['direct_analysis']}</pre>
                
                <h2>Edge-Based Analysis</h2>
                <pre>{analysis_results['edge_analysis']}</pre>
                
                <h2>Combined Analysis</h2>
                <pre>{analysis_results['synthesis']}</pre>
            </div>
            
            <div class="section">
                <h2>Visualization Versions</h2>
                <div class="links">
                    <a href="html_versions/visualization_standard_cot.html">Standard Chain of Thought</a>
                    <a href="html_versions/visualization_tree_of_thought.html">Tree of Thought</a>
                    <a href="html_versions/visualization_graph_of_thought.html">Graph of Thought</a>
                </div>
            </div>
            
            <div class="section">
                <h2>Data Files</h2>
                <p>Original frame: <a href="frame.jpg">frame.jpg</a></p>
                <p>Edge detection data: <a href="edges.json">edges.json</a></p>
            </div>
        </body>
        </html>
        """
        
        # 保存合并的HTML
        combined_html_path = f"{output_dir}/index.html"
        with open(combined_html_path, "w", encoding='utf-8') as f:
            f.write(combined_html)
        
        return {
            "frame_path": frame_path,
            "json_path": json_path,
            "html_paths": html_paths,
            "index_path": combined_html_path,
            "analysis_results": analysis_results
        }
    

    def run_ablation(self, video_path, output_dir="output/ablation"):
        """消融实验处理流程 - 对照组"""
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 读取视频第一帧
        video = cv2.VideoCapture(video_path)
        ret, frame = video.read()
        video.release()
        
        if not ret:
            raise Exception("无法读取视频帧")
        
        # 保存原始帧图像
        frame_path = f"{output_dir}/frame.jpg"
        cv2.imwrite(frame_path, frame)
        
        # 直接进行图像理解（不进行边缘检测）
        direct_analysis = self.preprocessor.direct_image_understanding(frame)
        
        # 保存分析结果
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "direct_analysis": direct_analysis,
            "method": "direct_vision_only"
        }
        
        # 保存分析结果为JSON
        analysis_path = f"{output_dir}/direct_analysis.json"
        with open(analysis_path, "w", encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        # 创建对照组HTML文件
        ablation_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Direct Vision Analysis (Ablation Study)</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px;
                }}
                h1, h2 {{ color: #333; }}
                .analysis-section {{ 
                    margin: 20px 0;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .image-section {{
                    margin: 20px 0;
                }}
                .image-section img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                pre {{ 
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                }}
                .comparison-link {{
                    margin: 20px 0;
                    padding: 10px;
                    background: #f0f0f0;
                    border-radius: 5px;
                }}
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>UI Analysis - Direct Vision Approach</h1>
            
            <div class="image-section">
                <h2>Original Frame</h2>
                <img src="frame.jpg" alt="Original Frame">
            </div>
            
            <div class="analysis-section">
                <h2>Direct Vision Analysis</h2>
                <pre>{direct_analysis}</pre>
            </div>
            
            <div class="comparison-link">
                <p>👉 <a href="../output/index.html">Compare with Edge Detection Approach</a></p>
            </div>
            
            <p>Analysis results saved as: direct_analysis.json</p>
        </body>
        </html>
        """
        
        # 保存HTML
        ablation_html_path = f"{output_dir}/index.html"
        with open(ablation_html_path, "w", encoding='utf-8') as f:
            f.write(ablation_html)
        
        return {
            "frame_path": frame_path,
            "analysis_path": analysis_path,
            "html_path": ablation_html_path
        }
