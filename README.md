# UI2HTML

Implementing UI2HTML: Leveraging Chain of Thought in LLM Agents for Converting UI Designs into HTML Code

## 项目概述

UI2HTML 是一个创新的工具，用于将UI设计（视频或图像）自动转换为HTML代码。本项目利用大语言模型(LLM)的思维链（Chain of Thought）能力，实现了高质量的UI到HTML的转换。

## 主要特性

- **多模态分析**: 结合边缘检测和视觉分析进行UI理解
- **多种思维链策略**: 实现了标准CoT、树形思维和图形思维三种策略
- **自动化评估**: 包含完整的评估框架，支持多维度比较
- **可视化输出**: 生成多个版本的HTML实现，便于比较和选择

## 项目结构

UI2HTML/
├── run_main.py # 主运行脚本
├── webpage_handler.py # 网页处理核心类
├── evaluate.py # 评估工具
├── llm_util.py # LLM工具类
├── preprocess.py # 图像预处理工具
└── ui_dataset/ # 测试数据集



## 安装依赖
```python
pip install -r requirements.txt
```

## 使用方法

### 基本用法
```python
python run_main.py --video path/to/video.mp4 --output output_dir
```

### 参数说明

- `--video, -v`: 输入视频文件路径
- `--output, -o`: 输出目录路径
- `--sample-rate, -s`: 视频采样率（秒）
- `--mode, -m`: 运行模式（full/ablation/both）

### 运行模式

1. **完整分析 (full)**
   - 使用边缘检测和视觉分析
   - 生成多个HTML版本
   - 输出详细的分析结果

2. **消融实验 (ablation)**
   - 仅使用视觉分析
   - 生成基准HTML版本
   - 用于对比研究

3. **完整评估 (both)**
   - 运行两种模式并比较结果
   - 生成详细的评估报告

## 输出说明

### 目录结构

output/
├── html_versions/ # 不同策略生成的HTML
│ ├── visualization_standard_cot.html
│ ├── visualization_tree_of_thought.html
│ └── visualization_graph_of_thought.html
├── ablation/ # 消融实验结果
│ └── index.html
└── evaluation_results/ # 评估报告
├── evaluation_.json # 详细评估结果
└── evaluation_summary.json


### 评估指标

- 文本相似度
- HTML标签相似度
- 树结构距离
- 向量相似度

## 实现细节

### 思维链策略

1. **标准Chain of Thought**
   - 线性思维过程
   - 基于直接分析结果

2. **Tree of Thought**
   - 树状决策过程
   - 考虑多个可能的实现方案

3. **Graph of Thought**
   - 图形化思维模式
   - 关注组件间的关系

### 评估框架

- 多维度比较机制
- 自动化评分系统
- 详细的对比报告生成

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。请确保：

1. Fork 项目并创建新分支
2. 遵循现有的代码风格
3. 提供清晰的提交信息
4. 更新相关文档

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 作者：David Yuan
- GitHub：[davidyuan666](https://github.com/davidyuan666)

## 致谢

感谢所有为本项目提供帮助和建议的贡献者。
