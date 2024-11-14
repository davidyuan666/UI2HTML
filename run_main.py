import argparse
from webpage_handler import WebpageHandler
from pathlib import Path
import os

DEFAULT_VIDEO_PATH = os.path.join(os.getcwd(),'ui_dataset','VID_20241114_153252.mp4')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='视频UI分析工具')
    parser.add_argument('--video', '-v', type=str, default=DEFAULT_VIDEO_PATH,
                      help=f'输入视频文件的路径 (默认: {DEFAULT_VIDEO_PATH})')
    parser.add_argument('--output', '-o', type=str, default='output',
                      help='输出目录路径 (默认: output)')
    parser.add_argument('--sample-rate', '-s', type=float, default=5.0,
                      help='视频采样率，单位为秒 (默认: 5.0)')
    parser.add_argument('--mode', '-m', type=str, choices=['full', 'ablation', 'both','evaluate'],
                      default='evaluate', help='运行模式: full(完整分析), ablation(消融实验), both(两者都运行) (默认: both)')
    return parser.parse_args()

def run_full_analysis(handler, video_path, output_dir):
    """运行完整分析"""
    print("\n=== 运行完整分析（边缘检测 + 视觉分析）===")
    result = handler.run(str(video_path), output_dir)
    
    print("处理完成!")
    print(f"原始帧保存至: {result['frame_path']}")
    print(f"JSON数据保存至: {result['json_path']}")
    print("\n各版本可视化:")
    for approach, path in result['html_paths'].items():
        print(f"- {approach}: {path}")
    
    return result

def run_ablation_study(handler, video_path, output_dir):
    """运行消融实验"""
    print("\n=== 运行消融实验（仅视觉分析）===")
    result = handler.run_ablation(str(video_path), output_dir)
    
    print("处理完成!")
    print(f"原始帧保存至: {result['frame_path']}")
    print(f"分析结果保存至: {result['analysis_path']}")
    print(f"可视化页面: {result['html_path']}")
    
    return result



def run_evaluate(handler, output_dir):
    """评估不同方法生成的HTML结果差异"""
    print("\n=== 评估分析结果 ===")
    
    # 获取完整分析的HTML文件
    full_html_path = os.path.join(output_dir, 'html_versions/visualization_standard_cot.html')
    with open(full_html_path, 'r', encoding='utf-8') as f:
        full_html = f.read()
    
    # 获取消融实验的HTML文件
    ablation_html_path = os.path.join(output_dir, 'ablation/index.html')
    with open(ablation_html_path, 'r', encoding='utf-8') as f:
        ablation_html = f.read()
    
    # 运行评估
    report = handler.run_evaluate(ablation_html, full_html)
    
    print("\n评估完成!")
    print(f"评估报告已保存至: {os.path.join(output_dir, 'evaluation_report.json')}")
    
    # 打印主要评估结果
    if isinstance(report, dict):
        print("\n主要评估指标:")
        for key, value in report.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    
    return report


    



def main():
    """主函数"""
    args = parse_args()
    
    # 验证输入文件是否存在
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"错误: 视频文件 '{video_path}' 不存在")
        return
    
    try:
        # 初始化处理器
        handler = WebpageHandler()
        handler.sample_rate = args.sample_rate
        
        print(f"开始处理视频: {video_path}")
        print(f"采样率: {args.sample_rate}秒")
        
        results = {}
        
        # 根据模式运行相应的分析
        if args.mode in ['full', 'both']:
            results['full'] = run_full_analysis(handler, video_path, args.output)
            
        if args.mode in ['ablation', 'both']:
            ablation_output = os.path.join(args.output, 'ablation')
            results['ablation'] = run_ablation_study(handler, video_path, ablation_output)
        
        # 在both模式下运行评估
        if args.mode == 'evaluate':
            results['evaluate'] = run_evaluate(handler, args.output)
            
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()