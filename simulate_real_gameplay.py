#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟真实游戏体验 - 每次15道题的完整游戏流程
"""

import requests
import time
from collections import defaultdict

# 配置
BASE_URL = "https://www.wuguijiang.com"
QUIZ_URL = f"{BASE_URL}/quiz"
API_URL = f"{BASE_URL}/api/quiz/next"
GAMES_COUNT = 100  # 模拟100局游戏
QUESTIONS_PER_GAME = 15  # 每局15道题

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

def get_csrf_token(session):
    """获取CSRF token"""
    response = session.get(QUIZ_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to access quiz page: {response.status_code}")
    
    html = response.text
    if 'csrfToken = "' in html:
        start = html.find('csrfToken = "') + len('csrfToken = "')
        end = html.find('"', start)
        return html[start:end]
    else:
        raise Exception("CSRF token not found in HTML")

def play_one_game(session, csrf_token, game_number):
    """模拟一局完整的游戏"""
    seen_ids = []  # 每局游戏的已见题目
    questions_in_game = []
    
    print(f"🎮 开始第 {game_number} 局游戏...")
    
    for question_index in range(QUESTIONS_PER_GAME):
        try:
            payload = {
                "username": f"Player{game_number}",
                "seen": seen_ids,
                "questionIndex": question_index
            }
            
            headers = HEADERS.copy()
            headers['X-CSRF-Token'] = csrf_token
            
            response = session.post(API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('question'):
                    question_id = data['question']['id']
                    questions_in_game.append(question_id)
                    seen_ids.append(question_id)  # 模拟网页端的行为
                else:
                    print(f"  ❌ 第 {question_index+1} 题获取失败")
                    break
            else:
                print(f"  ❌ HTTP {response.status_code}")
                break
                
            time.sleep(0.05)  # 避免请求过快
            
        except Exception as e:
            print(f"  ❌ 第 {question_index+1} 题异常: {e}")
            break
    
    print(f"  ✅ 完成，获得 {len(questions_in_game)} 道题: {questions_in_game}")
    return questions_in_game

def main():
    print("🎯 模拟真实游戏体验测试")
    print(f"🎮 游戏局数: {GAMES_COUNT}")
    print(f"📝 每局题数: {QUESTIONS_PER_GAME}")
    print("=" * 60)
    
    # 统计数据
    all_questions_seen = set()
    question_frequency = defaultdict(int)
    successful_games = 0
    
    session = requests.Session()
    
    try:
        csrf_token = get_csrf_token(session)
        print(f"✅ 获取CSRF Token成功")
    except Exception as e:
        print(f"❌ 获取CSRF Token失败: {e}")
        return
    
    for game_num in range(1, GAMES_COUNT + 1):
        try:
            # 每20局刷新token
            if game_num % 20 == 0:
                try:
                    csrf_token = get_csrf_token(session)
                    print(f"🔄 已完成 {game_num}/{GAMES_COUNT} 局，刷新token...")
                except:
                    pass
            
            questions = play_one_game(session, csrf_token, game_num)
            
            if questions:
                successful_games += 1
                for qid in questions:
                    all_questions_seen.add(qid)
                    question_frequency[qid] += 1
            
            time.sleep(0.1)  # 游戏间隔
            
        except Exception as e:
            print(f"❌ 第 {game_num} 局游戏异常: {e}")
            continue
    
    # 分析结果
    print(f"\n📊 游戏体验分析:")
    print("=" * 60)
    print(f"成功游戏局数: {successful_games}")
    print(f"遇到的不同题目总数: {len(all_questions_seen)}")
    print(f"题目总出现次数: {sum(question_frequency.values())}")
    print(f"平均每道题出现次数: {sum(question_frequency.values()) / len(question_frequency):.2f}")
    
    # 出现频率统计
    frequency_counts = defaultdict(int)
    for count in question_frequency.values():
        frequency_counts[count] += 1
    
    print(f"\n📈 题目出现频率分布:")
    for freq in sorted(frequency_counts.keys()):
        print(f"出现 {freq} 次的题目: {frequency_counts[freq]} 道")
    
    # 最高频和最低频题目
    if question_frequency:
        max_freq = max(question_frequency.values())
        min_freq = min(question_frequency.values())
        
        print(f"\n🔥 出现最多的题目 ({max_freq} 次):")
        max_questions = [qid for qid, freq in question_frequency.items() if freq == max_freq]
        print(f"题目ID: {max_questions[:10]}")  # 只显示前10个
        
        print(f"\n🆕 出现最少的题目 ({min_freq} 次):")
        min_questions = [qid for qid, freq in question_frequency.items() if freq == min_freq]
        print(f"题目ID: {min_questions[:10]}")  # 只显示前10个
    
    # 覆盖率分析
    total_expected_questions = 400  # 假设总题库400道
    coverage_rate = len(all_questions_seen) / total_expected_questions * 100
    
    print(f"\n🎯 题库覆盖分析:")
    print(f"题库覆盖率: {coverage_rate:.1f}% ({len(all_questions_seen)}/{total_expected_questions})")
    
    if len(all_questions_seen) < 200:
        print("⚠️ 覆盖率较低，可能的原因:")
        print("1. 某些题目被选中的概率更高")
        print("2. 随机算法存在偏向性")
        print("3. 题目数量不足400道")
    elif len(all_questions_seen) > 300:
        print("✅ 覆盖率较高，随机算法表现良好")
    else:
        print("📊 覆盖率中等，符合随机分布预期")
    
    # 保存结果
    result = {
        "games_played": successful_games,
        "unique_questions": len(all_questions_seen),
        "question_frequency": dict(question_frequency),
        "coverage_rate": coverage_rate,
        "question_ids": sorted(all_questions_seen)
    }
    
    import json
    with open('C:/Users/user/real_gameplay_simulation.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 详细数据已保存到: C:/Users/user/real_gameplay_simulation.json")

if __name__ == "__main__":
    main()