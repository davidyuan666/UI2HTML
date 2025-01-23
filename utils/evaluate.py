import difflib
from bs4 import BeautifulSoup
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from zss import simple_distance, Node

'''
pip install beautifulsoup4 numpy scikit-learn zss
'''
class HTMLEvaluator:
    def __init__(self):
        self.weights = {
            'text_similarity': 0.25,
            'tag_similarity': 0.25,
            'tree_distance': 0.25,
            'vector_similarity': 0.25
        }
    
    def calculate_text_similarity(self, html1, html2):
        """计算文本相似度"""
        # 使用difflib计算文本相似度
        similarity = difflib.SequenceMatcher(None, html1, html2).ratio()
        return similarity
    
    def calculate_tag_similarity(self, html1, html2):
        """计算HTML标签相似度"""
        soup1 = BeautifulSoup(html1, 'html.parser')
        soup2 = BeautifulSoup(html2, 'html.parser')
        
        # 获取所有标签
        tags1 = [tag.name for tag in soup1.find_all()]
        tags2 = [tag.name for tag in soup2.find_all()]
        
        # 计算标签集合的Jaccard相似度
        intersection = len(set(tags1) & set(tags2))
        union = len(set(tags1) | set(tags2))
        
        return intersection / union if union > 0 else 0
    
    def html_to_tree(self, html):
        """将HTML转换为树结构"""
        soup = BeautifulSoup(html, 'html.parser')
        
        def create_tree(element):
            if element.name is None:
                return Node(element.string or '')
            children = [create_tree(child) for child in element.children if child.name is not None]
            return Node(element.name, children)
        
        return create_tree(soup)
    
    def calculate_tree_distance(self, html1, html2):
        """计算树编辑距离"""
        tree1 = self.html_to_tree(html1)
        tree2 = self.html_to_tree(html2)
        
        distance = simple_distance(tree1, tree2)
        # 归一化距离值到0-1范围
        max_nodes = max(len(BeautifulSoup(html1, 'html.parser').find_all()),
                       len(BeautifulSoup(html2, 'html.parser').find_all()))
        normalized_distance = 1 - (distance / (max_nodes * 2))
        
        return normalized_distance
    
    def calculate_vector_similarity(self, html1, html2):
        """计算向量相似度"""
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([html1, html2])
        
        # 计算余弦相似度
        # 修改这里：使用 toarray() 替代 A
        similarity = (tfidf_matrix * tfidf_matrix.T).toarray()[0,1]
        return similarity
    
    def evaluate(self, html1, html2):
        """综合评估HTML相似度"""
        # 计算各个指标
        metrics = {
            'text_similarity': self.calculate_text_similarity(html1, html2),
            'tag_similarity': self.calculate_tag_similarity(html1, html2),
            'tree_distance': self.calculate_tree_distance(html1, html2),
            'vector_similarity': self.calculate_vector_similarity(html1, html2)
        }
        
        # 计算加权平均分数
        weighted_sum = sum(score * self.weights[metric] for metric, score in metrics.items())
        total_weight = sum(self.weights.values())
        overall_score = weighted_sum / total_weight
        
        return {
            'metrics': metrics,
            'overall_score': overall_score
        }
    
    def generate_report(self, html1, html2):
        """生成详细的评估报告"""
        results = self.evaluate(html1, html2)
        
        report = {
            'detailed_metrics': {
                'HTML Text Similarity Score': results['metrics']['text_similarity'],
                'HTML Tag Similarity Score': results['metrics']['tag_similarity'],
                'HTML Tree Distance Score': results['metrics']['tree_distance'],
                'HTML Vector Similarity Score': results['metrics']['vector_similarity']
            },
            'overall_score': results['overall_score'],
            'weights_used': self.weights
        }
        
        return report
