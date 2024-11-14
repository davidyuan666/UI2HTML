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
        frame_data = data["frames"][0]
        
        # 基础提示词模板
        base_template = f"""
        Generate a complete, runnable HTML page that visualizes UI analysis results. 
        Output ONLY the full HTML code without any explanations or markdown.
        
        Use the following analysis data:
        
        DIRECT_ANALYSIS = `{frame_data["analysis"]["direct_analysis"]}`
        EDGE_ANALYSIS = `{frame_data["analysis"]["edge_analysis"]}`

        Technical Requirements:
        1. Use Tailwind CSS (include CDN)
        2. Include Alpine.js for interactivity (include CDN)
        3. Create a responsive layout with:
        - Navigation/tabs for switching between analyses
        - Cards for displaying analysis sections
        - Interactive UI component visualization
        4. Include the original image (use 'frame.jpg' as src)
        5. Implement dark/light mode toggle
        6. Add loading states and transitions
        7. Ensure all interactive elements have hover states
        8. Include proper meta tags and viewport settings

        The complete HTML should:
        - Start with <!DOCTYPE html>
        - Include all necessary CDN links
        - Contain all CSS and JavaScript inline
        - Be properly formatted and indented
        - Include error handling
        - Have all interactive features fully implemented
        - Be fully responsive
        
        IMPORTANT: Output ONLY the complete HTML code, nothing else.
        """
        
        # 标准 Chain of Thought
        standard_cot_prompt = f"""
        {base_template}
        
        Structure the HTML as follows:
        1. Document head with meta tags and CDN links
        2. Navigation bar with analysis toggles
        3. Main content area with:
        - Original image section
        - Analysis results in cards
        - Interactive visualization
        4. Footer with additional information
        
        IMPORTANT: Output ONLY the complete HTML code, nothing else.
        """
        
        # Tree of Thought
        tree_of_thought_prompt = f"""
        {base_template}
        
        Implement the following features:
        1. Header:
        - Responsive navigation
        - Theme toggle
        - Analysis type selector
        2. Main Content:
        - Image viewer with zoom
        - Analysis cards with expandable sections
        - Interactive component map
        3. Sidebar:
        - Quick navigation
        - Analysis summary
        - Control panel
        
        IMPORTANT: Output ONLY the complete HTML code, nothing else.
        """
        
        # Graph of Thought
        graph_of_thought_prompt = f"""
        {base_template}
        
        Create a single-page application with:
        1. Layout:
        - Fixed header with controls
        - Scrollable main content
        - Floating action buttons
        2. Components:
        - Image comparison tool
        - Analysis viewer
        - Interactive overlay
        3. Features:
        - Smooth transitions
        - Responsive grid
        - Touch support
        
        IMPORTANT: Output ONLY the complete HTML code, nothing else.
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
                # 确保结果是纯HTML代码
                if not html.strip().startswith('<!DOCTYPE html>'):
                    html = f"""<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>UI Analysis - {approach}</title>
                        {html}
                    </head>
                    <body>
                        {html}
                    </body>
                    </html>"""
                
                file_path = output_dir / f'visualization_{approach}.html'
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html)
            
            return {
                'standard_cot': str(output_dir / 'visualization_standard_cot.html'),
                'tree_of_thought': str(output_dir / 'visualization_tree_of_thought.html'),
                'graph_of_thought': str(output_dir / 'visualization_graph_of_thought.html')
            }
            
        except Exception as e:
            print(f"HTML生成过程中出现错误: {str(e)}")
            return {
                'error': str(e)
            }
    

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

        
        return {
            "frame_path": frame_path,
            "json_path": json_path,
            "html_paths": html_paths,
            "analysis_results": analysis_results
        }
    

    def run_ablation(self, video_path, output_dir="output/ablation"):
        """消融实验处理流程 - 仅使用视觉分析"""
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
        
        # 生成HTML的提示词
        prompt = f"""
        Generate an HTML page based on the UI image analysis results below. 
        The page should visualize and structure the analysis in an interactive and user-friendly way.

        Analysis Results:
        {direct_analysis}

        Requirements:
        1. Create a modern, responsive web interface
        2. Include the following sections:
        - Original image display (use 'frame.jpg' as the image source)
        - Structured analysis results
        - Interactive UI component visualization
        3. Use appropriate styling and layout
        4. Implement any relevant interactive features
        5. Follow web accessibility guidelines

        Please provide only the complete HTML code (including CSS and JavaScript) without any additional explanation.
        The code should be ready to use and well-formatted.
        """
        
        html_result = self.llm_util.native_chat(prompt)
        
        # 保存HTML
        ablation_html_path = f"{output_dir}/index.html"
        with open(ablation_html_path, "w", encoding='utf-8') as f:
            f.write(html_result)
        
        return {
            "frame_path": frame_path,
            "analysis_path": analysis_path,
            "html_path": ablation_html_path
        }