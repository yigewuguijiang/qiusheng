#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quiz题目随机性测试脚本
测试400道题目的出现概率是否相同
"""

import requests
import time
import json
from collections import defaultdict
import statistics

# 可选依赖
try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# 配置
BASE_URL = "https://www.wuguijiang.com"
QUIZ_URL = f"{BASE_URL}/quiz"
API_URL = f"{BASE_URL}/api/quiz/next"
TOTAL_TESTS = 1000  # 总测试次数（每次获取一道题）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_csrf_token(session):
    """获取CSRF token"""
    # 访问quiz页面获取CSRF token
    response = session.get(QUIZ_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to access quiz page: {response.status_code}")
    
    # 从HTML中提取CSRF token
    html = response.text
    if 'csrfToken = "' in html:
        start = html.find('csrfToken = "') + len('csrfToken = "')
        end = html.find('"', start)
        csrf_token = html[start:end]
        return csrf_token
    else:
        raise Exception("CSRF token not found in HTML")

def get_random_question(session, csrf_token, seen_ids=[]):
    """获取一道随机题目"""
    payload = {
        "username": "TestUser",
        "seen": seen_ids,
        "questionIndex": len(seen_ids)
    }
    
    headers = HEADERS.copy()
    headers.update({
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrf_token,
        'Referer': QUIZ_URL
    })
    
    response = session.post(API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('question'):
            return data['question']['id']
    elif response.status_code == 403:
        # CSRF token可能过期
        return 'CSRF_ERROR'
    
    return None

def run_probability_test():
    """运行概率测试"""
    print(f"🧪 开始Quiz题目随机性测试")
    print(f"📊 测试次数: {TOTAL_TESTS}")
    print("=" * 60)
    
    # 统计数据
    question_counts = defaultdict(int)
    failed_requests = 0
    csrf_errors = 0
    
    # 创建session
    session = requests.Session()
    
    try:
        # 获取初始CSRF token
        csrf_token = get_csrf_token(session)
        print(f"✅ 获取CSRF Token成功: {csrf_token[:10]}...")
    except Exception as e:
        print(f"❌ 获取CSRF Token失败: {e}")
        return {}, TOTAL_TESTS
    
    for i in range(TOTAL_TESTS):
        try:
            # 每50次刷新token
            if i % 50 == 0 and i > 0:
                try:
                    csrf_token = get_csrf_token(session)
                    print(f"🔄 已完成 {i}/{TOTAL_TESTS} 次测试，刷新token...")
                except:
                    pass
            
            question_id = get_random_question(session, csrf_token)
            
            if question_id == 'CSRF_ERROR':
                # CSRF错误，尝试重新获取token
                csrf_errors += 1
                try:
                    csrf_token = get_csrf_token(session)
                    # 重试请求
                    question_id = get_random_question(session, csrf_token)
                except:
                    failed_requests += 1
                    continue
            
            if question_id and question_id != 'CSRF_ERROR':
                question_counts[question_id] += 1
            else:
                failed_requests += 1
                if failed_requests <= 10:  # 只显示前10个失败
                    print(f"❌ 第 {i+1} 次请求失败")
            
            # 避免请求过快
            time.sleep(0.1)
            
        except Exception as e:
            failed_requests += 1
            if failed_requests <= 10:  # 只显示前10个异常
                print(f"❌ 第 {i+1} 次请求异常: {e}")
            time.sleep(1)  # 异常时等待更长时间
    
    print(f"\n📈 测试完成!")
    print(f"成功请求: {len(question_counts)} 道不同题目")
    print(f"失败请求: {failed_requests}")
    print(f"CSRF错误: {csrf_errors}")
    print(f"总请求数: {TOTAL_TESTS}")
    
    return question_counts, failed_requests

def analyze_results(question_counts):
    """分析测试结果"""
    if not question_counts:
        print("❌ 没有获取到任何题目数据")
        return
    
    counts = list(question_counts.values())
    total_questions = len(question_counts)
    total_requests = sum(counts)
    
    print(f"\n📊 统计分析结果:")
    print("=" * 60)
    print(f"题目总数: {total_questions}")
    print(f"有效请求总数: {total_requests}")
    print(f"平均每道题出现次数: {total_requests / total_questions:.2f}")
    print(f"理论平均值: {total_requests / 400:.2f} (假设400道题)")
    
    # 基础统计
    print(f"\n📈 出现次数统计:")
    print(f"最多出现次数: {max(counts)}")
    print(f"最少出现次数: {min(counts)}")
    print(f"标准差: {statistics.stdev(counts):.2f}")
    print(f"方差: {statistics.variance(counts):.2f}")
    
    # 分布分析
    expected_count = total_requests / total_questions
    
    print(f"\n🎯 随机性分析:")
    print(f"期望值: {expected_count:.2f}")
    
    # 计算偏差
    deviations = [abs(count - expected_count) for count in counts]
    avg_deviation = sum(deviations) / len(deviations)
    print(f"平均偏差: {avg_deviation:.2f}")
    print(f"偏差率: {(avg_deviation / expected_count) * 100:.1f}%")
    
    # 卡方检验简化版本
    chi_square = sum((count - expected_count) ** 2 / expected_count for count in counts)
    print(f"卡方统计量: {chi_square:.2f}")
    
    # 分布区间统计
    print(f"\n📋 分布区间:")
    ranges = [
        (0, expected_count * 0.5, "严重偏低"),
        (expected_count * 0.5, expected_count * 0.8, "偏低"),
        (expected_count * 0.8, expected_count * 1.2, "正常"),
        (expected_count * 1.2, expected_count * 1.5, "偏高"),
        (expected_count * 1.5, float('inf'), "严重偏高")
    ]
    
    for min_val, max_val, label in ranges:
        count_in_range = sum(1 for c in counts if min_val <= c < max_val)
        percentage = (count_in_range / total_questions) * 100
        print(f"{label}: {count_in_range} 道题 ({percentage:.1f}%)")
    
    # 找出异常题目
    print(f"\n🔍 异常题目 (偏差超过50%):")
    threshold = expected_count * 0.5
    abnormal_questions = []
    
    for qid, count in question_counts.items():
        if abs(count - expected_count) > threshold:
            deviation_pct = ((count - expected_count) / expected_count) * 100
            abnormal_questions.append((qid, count, deviation_pct))
    
    if abnormal_questions:
        abnormal_questions.sort(key=lambda x: abs(x[2]), reverse=True)
        for qid, count, dev_pct in abnormal_questions[:10]:  # 只显示前10个
            print(f"题目ID {qid}: 出现 {count} 次 (偏差 {dev_pct:+.1f}%)")
    else:
        print("✅ 没有发现严重异常的题目")

def create_visualization(question_counts):
    """创建可视化图表"""
    if not question_counts:
        return
    
    if not HAS_MATPLOTLIB:
        print("\n📊 matplotlib未安装，跳过可视化")
        print("安装命令: pip install matplotlib numpy")
        return
    
    try:
        counts = list(question_counts.values())
        total_requests = sum(counts)
        expected_count = total_requests / len(question_counts)
        
        # 创建直方图
        plt.figure(figsize=(12, 8))
        
        # 子图1: 出现次数分布直方图
        plt.subplot(2, 2, 1)
        plt.hist(counts, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(expected_count, color='red', linestyle='--', label=f'期望值: {expected_count:.1f}')
        plt.xlabel('出现次数')
        plt.ylabel('题目数量')
        plt.title('题目出现次数分布')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 子图2: 偏差分布
        plt.subplot(2, 2, 2)
        deviations = [count - expected_count for count in counts]
        plt.hist(deviations, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
        plt.axvline(0, color='red', linestyle='--', label='零偏差')
        plt.xlabel('偏差 (实际 - 期望)')
        plt.ylabel('题目数量')
        plt.title('偏差分布')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 子图3: 题目ID vs 出现次数散点图
        plt.subplot(2, 2, 3)
        question_ids = list(question_counts.keys())
        counts_for_plot = [question_counts[qid] for qid in question_ids]
        plt.scatter(range(len(question_ids)), counts_for_plot, alpha=0.6, s=20)
        plt.axhline(expected_count, color='red', linestyle='--', label=f'期望值: {expected_count:.1f}')
        plt.xlabel('题目序号')
        plt.ylabel('出现次数')
        plt.title('各题目出现次数')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 子图4: Q-Q图 (简化版)
        plt.subplot(2, 2, 4)
        sorted_counts = sorted(counts)
        if HAS_MATPLOTLIB and 'np' in globals():
            theoretical_quantiles = np.linspace(min(sorted_counts), max(sorted_counts), len(sorted_counts))
        else:
            # 简化版本，不使用numpy
            theoretical_quantiles = [min(sorted_counts) + i * (max(sorted_counts) - min(sorted_counts)) / (len(sorted_counts) - 1) for i in range(len(sorted_counts))]
        plt.scatter(theoretical_quantiles, sorted_counts, alpha=0.6, s=20)
        plt.plot([min(sorted_counts), max(sorted_counts)], [min(sorted_counts), max(sorted_counts)], 'r--', label='理想分布')
        plt.xlabel('理论分位数')
        plt.ylabel('实际分位数')
        plt.title('Q-Q图 (分布对比)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存到Windows用户目录
        output_path = 'C:/Users/user/quiz_probability_analysis.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n📊 图表已保存到: {output_path}")
        
    except Exception as e:
        print(f"\n❌ 创建图表时出错: {e}")

def main():
    """主函数"""
    print("🎯 Quiz题目随机性测试工具")
    print("测试400道题目的出现概率是否均匀分布")
    print("=" * 60)
    
    try:
        # 运行测试
        question_counts, failed_requests = run_probability_test()
        
        if not question_counts:
            print("❌ 测试失败，未获取到任何数据")
            return
        
        # 分析结果
        analyze_results(question_counts)
        
        # 创建可视化
        create_visualization(question_counts)
        
        # 保存详细数据
        results = {
            'test_config': {
                'total_tests': TOTAL_TESTS,
                'base_url': BASE_URL,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'statistics': {
                'total_questions': len(question_counts),
                'successful_requests': sum(question_counts.values()),
                'failed_requests': failed_requests,
                'question_counts': dict(question_counts)
            }
        }
        
        # 保存到Windows用户目录
        output_path = 'C:/Users/user/quiz_test_results.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细数据已保存到: {output_path}")
        
        # 结论
        counts = list(question_counts.values())
        expected = sum(counts) / len(counts)
        std_dev = statistics.stdev(counts)
        cv = (std_dev / expected) * 100  # 变异系数
        
        print(f"\n🎯 测试结论:")
        print("=" * 60)
        if cv < 20:
            print("✅ 题目分布相对均匀，随机算法表现良好")
        elif cv < 40:
            print("⚠️ 题目分布略有偏差，但在可接受范围内")
        else:
            print("❌ 题目分布不均匀，建议检查随机算法")
        
        print(f"变异系数: {cv:.1f}% (越小越均匀)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()