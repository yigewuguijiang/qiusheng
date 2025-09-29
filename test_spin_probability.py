#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试转盘概率分布 - 1000次测试，50线程
"""

import requests
import time
import concurrent.futures
from collections import Counter
import threading
import json

# 配置
BASE_URL = "https://www.wuguijiang.com"  # 使用实际部署的网址
SPIN_URL = f"{BASE_URL}/api/spin"
TOTAL_SPINS = 1000
THREAD_COUNT = 50
SPINS_PER_THREAD = TOTAL_SPINS // THREAD_COUNT

# 线程安全的计数器
result_counter = Counter()
counter_lock = threading.Lock()
success_count = 0
fail_count = 0

def get_csrf_token(session):
    """获取CSRF token"""
    try:
        response = session.get(BASE_URL + "/spin")
        html = response.text
        if 'csrfToken = "' in html:
            start = html.find('csrfToken = "') + len('csrfToken = "')
            end = html.find('"', start)
            return html[start:end]
        return None
    except:
        return None

def generate_nonce(length=16):
    """生成随机nonce"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def spin_worker(thread_id, spins_count):
    """单个线程的工作函数"""
    global success_count, fail_count
    
    session = requests.Session()
    csrf_token = get_csrf_token(session)
    
    if not csrf_token:
        print(f"线程 {thread_id}: 无法获取CSRF token")
        return
    
    local_results = []
    
    for i in range(spins_count):
        try:
            timestamp = int(time.time())
            nonce = generate_nonce()
            
            response = session.post(SPIN_URL, 
                json={
                    "username": f"TestUser{thread_id}",
                    "timestamp": timestamp,
                    "nonce": nonce
                },
                headers={
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrf_token
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    prize = data.get('prize', '')
                    # 去除玩家名字前缀，只保留任务名
                    if ': ' in prize:
                        prize = prize.split(': ', 1)[1]
                    local_results.append(prize)
                    
                    with counter_lock:
                        success_count += 1
                else:
                    with counter_lock:
                        fail_count += 1
            else:
                with counter_lock:
                    fail_count += 1
                    
            # 避免请求过快
            time.sleep(0.01)
            
        except Exception as e:
            with counter_lock:
                fail_count += 1
            print(f"线程 {thread_id} 错误: {e}")
    
    # 更新全局计数器
    with counter_lock:
        for result in local_results:
            result_counter[result] += 1
    
    print(f"线程 {thread_id} 完成，成功 {len(local_results)} 次")

def main():
    print(f"🎯 转盘概率测试")
    print(f"总次数: {TOTAL_SPINS}")
    print(f"线程数: {THREAD_COUNT}")
    print(f"每线程: {SPINS_PER_THREAD} 次")
    print("=" * 60)
    
    start_time = time.time()
    
    # 使用线程池执行
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = []
        for i in range(THREAD_COUNT):
            future = executor.submit(spin_worker, i+1, SPINS_PER_THREAD)
            futures.append(future)
        
        # 等待所有线程完成
        concurrent.futures.wait(futures)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 输出结果
    print(f"\n✅ 测试完成!")
    print(f"耗时: {duration:.2f} 秒")
    print(f"成功: {success_count} 次")
    print(f"失败: {fail_count} 次")
    print(f"成功率: {success_count/TOTAL_SPINS*100:.1f}%")
    
    print(f"\n📊 转盘结果分布:")
    print("=" * 60)
    
    # 按出现次数排序
    sorted_results = sorted(result_counter.items(), key=lambda x: x[1], reverse=True)
    
    # 期望的任务列表（30个）
    expected_tasks = [
        '2加币买吃的', 'Quiz', 'Scratch', 'Slot', '集体10个深蹲',
        '和路人美女要微信', '和路人美女合照', '给路人吉他唱歌打分',
        '集体热舞1分钟', '集体10个俯卧撑', '公主抱下蹲5个',
        '要路人帅哥微信', '找路人要吃的', '和路人音准比拼',
        '找到一名路人猜歌', '找路人妹妹合唱', '回答队友真心话',
        '连续夸赞路人美女30秒', '人群中大声清唱10秒', '转盘次数+2',
        '和路人帅哥合照', '集体反方向走一分钟', '和路人石头剪刀布',
        '让路人B站关注一个乌龟酱', '找一名路人猜年龄', '浏览器记录',
        '手拉手走一分钟', '垃圾清洁工', '含水对视', '背起走路'
    ]
    
    # 理论概率（均等）
    expected_probability = 1 / len(expected_tasks) * 100
    expected_count = TOTAL_SPINS / len(expected_tasks)
    
    print(f"理论概率: {expected_probability:.2f}% (每项约 {expected_count:.1f} 次)")
    print("-" * 60)
    
    # 显示实际结果
    for task, count in sorted_results:
        probability = count / success_count * 100 if success_count > 0 else 0
        deviation = probability - expected_probability
        print(f"{task:<25} {count:>4} 次 ({probability:>5.2f}%) 偏差: {deviation:+.2f}%")
    
    # 检查是否有缺失的任务
    appeared_tasks = set(result_counter.keys())
    all_tasks_set = set(expected_tasks)
    missing_tasks = all_tasks_set - appeared_tasks
    
    if missing_tasks:
        print(f"\n⚠️ 未出现的任务 ({len(missing_tasks)} 个):")
        for task in missing_tasks:
            print(f"  - {task}")
    
    # 统计分析
    if success_count > 0:
        counts = list(result_counter.values())
        avg_count = sum(counts) / len(counts)
        max_count = max(counts)
        min_count = min(counts)
        
        print(f"\n📈 统计分析:")
        print(f"平均出现次数: {avg_count:.1f}")
        print(f"最高出现次数: {max_count}")
        print(f"最低出现次数: {min_count}")
        print(f"标准差: {(sum((x - avg_count)**2 for x in counts) / len(counts))**0.5:.2f}")
    
    # 保存详细结果
    result_data = {
        "total_spins": TOTAL_SPINS,
        "success_count": success_count,
        "fail_count": fail_count,
        "duration_seconds": duration,
        "thread_count": THREAD_COUNT,
        "results": dict(result_counter),
        "missing_tasks": list(missing_tasks) if missing_tasks else []
    }
    
    with open('spin_probability_test.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 详细结果已保存到: spin_probability_test.json")

if __name__ == "__main__":
    main()