#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查题库的实际情况
"""

import requests
import json
from collections import defaultdict, Counter

# 配置
BASE_URL = "https://www.wuguijiang.com"
API_URL = f"{BASE_URL}/api/quiz/next"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

def get_csrf_token(session):
    """获取CSRF token"""
    # 访问quiz页面获取CSRF token
    response = session.get(f"{BASE_URL}/quiz", headers=HEADERS)
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

def test_different_scenarios():
    """测试不同的请求场景"""
    
    scenarios = [
        {
            "name": "空seen数组",
            "payload": {"username": "TestUser", "seen": [], "questionIndex": 0}
        },
        {
            "name": "不传seen参数",
            "payload": {"username": "TestUser", "questionIndex": 0}
        },
        {
            "name": "seen有很多ID",
            "payload": {"username": "TestUser", "seen": list(range(1, 101)), "questionIndex": 100}
        },
        {
            "name": "questionIndex为0",
            "payload": {"username": "TestUser", "seen": [], "questionIndex": 0}
        },
        {
            "name": "questionIndex递增",
            "payload": {"username": "TestUser", "seen": [], "questionIndex": 5}
        }
    ]
    
    print("🔍 测试不同请求场景:")
    print("=" * 60)
    
    # 创建session并获取CSRF token
    session = requests.Session()
    try:
        csrf_token = get_csrf_token(session)
        print(f"✅ 获取CSRF Token成功")
    except Exception as e:
        print(f"❌ 获取CSRF Token失败: {e}")
        return
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}:")
        
        # 测试多次获取同样的参数
        question_ids = set()
        for i in range(20):
            try:
                headers = HEADERS.copy()
                headers['X-CSRF-Token'] = csrf_token
                
                response = session.post(API_URL, json=scenario['payload'], headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('question'):
                        question_ids.add(data['question']['id'])
                else:
                    print(f"  ❌ HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ 异常: {e}")
        
        print(f"  📊 获得了 {len(question_ids)} 道不同题目")
        if len(question_ids) <= 10:
            print(f"  📝 题目ID: {sorted(question_ids)}")

def exhaustive_search():
    """穷尽搜索，尝试获取所有可能的题目"""
    print(f"\n🔎 穷尽搜索所有题目:")
    print("=" * 60)
    
    all_questions = set()
    seen_combinations = [
        [],  # 空seen
        list(range(1, 51)),  # seen前50个
        list(range(51, 101)),  # seen 51-100
        list(range(101, 151)), # seen 101-150
    ]
    
    # 创建session并获取CSRF token
    session = requests.Session()
    try:
        csrf_token = get_csrf_token(session)
        print(f"✅ 获取CSRF Token成功")
    except Exception as e:
        print(f"❌ 获取CSRF Token失败: {e}")
        return set()
    
    for seen in seen_combinations:
        print(f"\n🔄 测试seen={len(seen)}个题目的情况...")
        
        # 每种seen组合测试100次
        for i in range(100):
            try:
                # 每25次刷新token
                if i % 25 == 0 and i > 0:
                    try:
                        csrf_token = get_csrf_token(session)
                    except:
                        pass
                
                payload = {
                    "username": f"TestUser{i}",
                    "seen": seen,
                    "questionIndex": len(seen)
                }
                
                headers = HEADERS.copy()
                headers['X-CSRF-Token'] = csrf_token
                
                response = session.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('question'):
                        all_questions.add(data['question']['id'])
                
            except Exception as e:
                continue
    
    print(f"\n📊 总共发现 {len(all_questions)} 道不同题目")
    
    if len(all_questions) > 0:
        print(f"📏 题目ID范围: {min(all_questions)} - {max(all_questions)}")
        
        # 检查ID的连续性
        sorted_ids = sorted(all_questions)
        gaps = []
        for i in range(len(sorted_ids) - 1):
            if sorted_ids[i+1] - sorted_ids[i] > 1:
                gaps.append((sorted_ids[i], sorted_ids[i+1]))
        
        if gaps:
            print(f"🔍 ID间隙: {gaps[:10]}")  # 只显示前10个间隙
        else:
            print("✅ ID连续无间隙")
    
    return all_questions

def analyze_id_distribution(question_ids):
    """分析题目ID的分布"""
    if not question_ids:
        return
    
    print(f"\n📈 题目ID分布分析:")
    print("=" * 60)
    
    sorted_ids = sorted(question_ids)
    
    # ID范围分析
    print(f"最小ID: {min(sorted_ids)}")
    print(f"最大ID: {max(sorted_ids)}")
    print(f"ID跨度: {max(sorted_ids) - min(sorted_ids) + 1}")
    print(f"实际题目数: {len(sorted_ids)}")
    print(f"缺失题目数: {max(sorted_ids) - min(sorted_ids) + 1 - len(sorted_ids)}")
    
    # 分段统计
    ranges = [
        (1, 100, "1-100"),
        (101, 200, "101-200"),
        (201, 300, "201-300"),
        (301, 400, "301-400"),
        (401, 500, "401-500"),
    ]
    
    print(f"\n📊 ID分段分布:")
    for start, end, label in ranges:
        count = sum(1 for qid in sorted_ids if start <= qid <= end)
        if count > 0:
            print(f"{label}: {count} 道题")

def main():
    print("🧪 Quiz题库检查工具")
    print("检查实际题库大小和题目分布")
    print("=" * 60)
    
    # 测试不同场景
    test_different_scenarios()
    
    # 穷尽搜索
    all_questions = exhaustive_search()
    
    # 分析分布
    analyze_id_distribution(all_questions)
    
    # 保存结果
    if all_questions:
        result = {
            "total_questions": len(all_questions),
            "question_ids": sorted(all_questions),
            "min_id": min(all_questions),
            "max_id": max(all_questions)
        }
        
        with open('C:/Users/user/question_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细数据已保存到: C:/Users/user/question_analysis.json")
    
    print(f"\n🎯 结论:")
    print("=" * 60)
    if len(all_questions) < 400:
        print(f"⚠️ 实际题库只有 {len(all_questions)} 道题，不是400道")
        print("可能原因：")
        print("1. 题库文件本身就不足400道")
        print("2. 随机算法有偏向性")
        print("3. 某些题目无法被随机选中")
    else:
        print(f"✅ 题库确实有 {len(all_questions)} 道题")

if __name__ == "__main__":
    main()