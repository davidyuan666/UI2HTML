import argparse
from webpage_handler import WebpageHandler
from pathlib import Path
import os
import json
from datetime import datetime

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
    
    # 获取html_versions目录下的所有HTML文件
    html_versions_dir = os.path.join(output_dir, 'html_versions')
    html_files = [f for f in os.listdir(html_versions_dir) if f.endswith('.html')]
    
    if not html_files:
        raise Exception("未找到HTML文件在目录: " + html_versions_dir)
    
    # 读取所有HTML文件
    html_contents = {}
    for filename in html_files:
        file_path = os.path.join(html_versions_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            html_contents[filename] = {
                'path': file_path,
                'content': f.read()
            }
    
    # 获取消融实验的HTML文件
    ablation_html_path = os.path.join(output_dir, 'ablation/index.html')
    with open(ablation_html_path, 'r', encoding='utf-8') as f:
        ablation_html = f.read()
    
    # 创建评估结果目录
    eval_output_dir = os.path.join(output_dir, 'evaluation_results')
    os.makedirs(eval_output_dir, exist_ok=True)
    
    # 对每个HTML版本进行评估
    reports = {}
    for filename, html_data in html_contents.items():
        print(f"\n评估 {filename} vs ablation:")
        report = handler.run_evaluate(ablation_html, html_data['content'])
        
        # 添加文件信息
        report['file_info'] = {
            'full_analysis_file': html_data['path'],
            'ablation_file': ablation_html_path
        }
        
        # 保存详细的评估结果
        eval_filename = f'evaluation_{os.path.splitext(filename)[0]}.json'
        eval_path = os.path.join(eval_output_dir, eval_filename)
        with open(eval_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        reports[filename] = report
        
        # 打印当前评估结果
        print(f"\n=== 评估文件 ===")
        print(f"完整分析文件: {html_data['path']}")
        print(f"消融实验文件: {ablation_html_path}")
        print(f"评估报告保存至: {eval_path}")
        print("\n=== 主要评估指标 ===")
        for key, value in report.items():
            if key == 'file_info':
                continue
            if isinstance(value, dict):
                print(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    
    # 保存汇总报告
    summary_path = os.path.join(eval_output_dir, 'evaluation_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'ablation_file': ablation_html_path,
            'evaluations': reports
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n汇总报告已保存至: {summary_path}")
    
    return reports


    



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