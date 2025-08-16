#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证GameLogic.randomInt的随机性
直接测试随机函数的分布
"""

import subprocess
import json
from collections import defaultdict
import statistics
import math

def test_random_int(min_val, max_val, samples=10000):
    """测试randomInt函数的分布"""
    # 创建测试脚本
    test_script = f"""
const GameLogic = require('./data/gameLogic.js');

const results = [];
for (let i = 0; i < {samples}; i++) {{
    results.push(GameLogic.randomInt({min_val}, {max_val}));
}}
console.log(JSON.stringify(results));
"""
    
    # 写入临时文件
    with open('test_random.js', 'w') as f:
        f.write(test_script)
    
    # 执行测试
    result = subprocess.run(['node', 'test_random.js'], capture_output=True, text=True)
    
    # 清理临时文件
    subprocess.run(['rm', 'test_random.js'])
    
    # 解析结果
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print(f"错误: {result.stderr}")
        return None

def analyze_distribution(data, min_val, max_val):
    """分析分布情况"""
    if not data:
        return
    
    # 统计每个值出现的次数
    counts = defaultdict(int)
    for val in data:
        counts[val] += 1
    
    # 期望每个值出现的次数
    total_values = max_val - min_val + 1
    expected_count = len(data) / total_values
    
    print(f"\n📊 分布分析 (范围: {min_val}-{max_val}, 样本: {len(data)})")
    print("=" * 60)
    print(f"期望每个值出现次数: {expected_count:.2f}")
    
    # 计算统计指标
    actual_counts = [counts.get(i, 0) for i in range(min_val, max_val + 1)]
    
    mean = statistics.mean(actual_counts)
    stdev = statistics.stdev(actual_counts)
    cv = (stdev / mean) * 100
    
    print(f"实际平均出现次数: {mean:.2f}")
    print(f"标准差: {stdev:.2f}")
    print(f"变异系数: {cv:.1f}%")
    
    # 卡方检验
    chi_square = sum((count - expected_count) ** 2 / expected_count for count in actual_counts)
    degrees_of_freedom = total_values - 1
    
    print(f"\n卡方统计量: {chi_square:.2f}")
    print(f"自由度: {degrees_of_freedom}")
    
    # 简单的临界值判断（95%置信度）
    # 对于大自由度，可以用近似公式
    critical_value = degrees_of_freedom + 2 * math.sqrt(2 * degrees_of_freedom)
    print(f"临界值(95%): {critical_value:.2f}")
    
    if chi_square < critical_value:
        print("✅ 通过卡方检验，分布均匀")
    else:
        print("❌ 未通过卡方检验，分布可能不均匀")
    
    # 显示极值
    min_count = min(actual_counts)
    max_count = max(actual_counts)
    print(f"\n最少出现次数: {min_count}")
    print(f"最多出现次数: {max_count}")
    print(f"极差: {max_count - min_count}")
    
    # 显示分布直方图（简化版）
    print("\n分布直方图:")
    bucket_size = 10
    for i in range(0, total_values, bucket_size):
        bucket_counts = actual_counts[i:i+bucket_size]
        avg = sum(bucket_counts) / len(bucket_counts) if bucket_counts else 0
        bar_length = int(avg / expected_count * 30)
        print(f"{min_val+i:3d}-{min(min_val+i+bucket_size-1, max_val):3d}: {'█' * bar_length} {avg:.1f}")

def test_question_selection():
    """测试题目选择的随机性"""
    print("\n🎯 测试题目选择随机性")
    print("=" * 60)
    
    # 模拟400道题的选择
    print("\n1. 测试 randomInt(0, 399) - 模拟400道题")
    data = test_random_int(0, 399, 10000)
    if data:
        analyze_distribution(data, 0, 399)
    
    # 测试较小范围
    print("\n2. 测试 randomInt(0, 9) - 验证小范围随机性")
    data = test_random_int(0, 9, 10000)
    if data:
        analyze_distribution(data, 0, 9)
    
    # 测试大范围
    print("\n3. 测试 randomInt(0, 999) - 验证大范围随机性")
    data = test_random_int(0, 999, 10000)
    if data:
        analyze_distribution(data, 0, 999)

def calculate_expected_distribution(total_questions=400, samples=1000):
    """计算理论分布"""
    print("\n📈 理论分布计算")
    print("=" * 60)
    print(f"题目总数: {total_questions}")
    print(f"采样次数: {samples}")
    
    expected = samples / total_questions
    print(f"\n每道题期望出现次数: {expected:.2f}")
    
    # 使用泊松分布计算概率
    print("\n泊松分布概率:")
    for k in range(0, 8):
        # 泊松分布概率公式
        prob = (math.exp(-expected) * (expected ** k)) / math.factorial(k)
        expected_questions = prob * total_questions
        print(f"出现{k}次的题目数期望: {expected_questions:.1f} ({prob*100:.1f}%)")
    
    # 计算置信区间
    std_dev = math.sqrt(expected)
    print(f"\n标准差: {std_dev:.2f}")
    print(f"95%置信区间: [{expected - 2*std_dev:.2f}, {expected + 2*std_dev:.2f}]")
    print(f"99%置信区间: [{expected - 3*std_dev:.2f}, {expected + 3*std_dev:.2f}]")

def main():
    """主函数"""
    print("🔬 Quiz随机性深度分析")
    print("验证GameLogic.randomInt函数的随机性")
    print("=" * 60)
    
    try:
        # 计算理论分布
        calculate_expected_distribution()
        
        # 测试随机函数
        test_question_selection()
        
        print("\n🎯 结论:")
        print("=" * 60)
        print("如果上述测试都通过，说明:")
        print("1. GameLogic.randomInt 函数产生的是真随机数")
        print("2. 题目分布不均匀是正常的随机现象")
        print("3. 1000次采样对400道题来说样本量偏小")
        print("4. 建议增加采样次数到4000-10000次以获得更均匀的分布")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()