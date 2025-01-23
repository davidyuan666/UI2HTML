import cv2
import numpy as np
from llm_util import LLMUtil
import base64

class ImagePreprocessor:
    def __init__(self):
        self.llm_util = LLMUtil()

    def encode_image_base64(self, image):
        """将图片编码为base64，并添加正确的数据URI前缀"""
        _, buffer = cv2.imencode('.jpg', image)
        base64_string = base64.b64encode(buffer).decode('utf-8')
        return base64_string
    

    def direct_image_understanding(self, image):
        """直接对原始图片进行理解"""
        image_base64 = self.encode_image_base64(image)
        
        prompt = f"""
        Please analyze this UI image and describe:
        1. The main UI components and their layout
        2. Any text content visible
        3. The overall structure and purpose of this interface
        4. Interactive elements (buttons, input fields, etc.)
        5. Color scheme and visual hierarchy
        
        Provide a structured analysis that could be used for UI reconstruction.
        """
        
        return self.llm_util.analyze_image_base64(prompt,image_base64)


    def edge_based_understanding(self, image, edges):
        """基于边缘检测结果进行理解"""
        # 创建可视化图像
        visualization = image.copy()
        for edge in edges:
            cv2.circle(visualization, (edge['x'], edge['y']), 2, (0, 255, 0), -1)
        
        image_base64 = self.encode_image_base64(visualization)
        
        prompt = f"""
        Analyzing this UI image with edge detection overlay:
        1. Identify UI components based on edge patterns
        2. Detect potential interactive elements from edge clusters
        3. Infer layout structure from edge distribution
        4. Recognize possible text areas from edge density
        5. Suggest component boundaries and groupings
        
        Edge coordinates are provided for reference. Please provide a structured analysis.
        """
        
        return self.llm_util.analyze_image_base64(prompt,image_base64)


    def combined_analysis(self, image, edges):
        """结合两种方法的分析结果"""
        direct_result = self.direct_image_understanding(image)
        edge_result = self.edge_based_understanding(image, edges)
        
        return {
            "direct_analysis": direct_result,
            "edge_analysis": edge_result
        }