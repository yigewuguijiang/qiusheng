#!/bin/bash
# Quiz题目随机性测试运行脚本

echo "🧪 Quiz题目随机性测试"
echo "===================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import requests" 2>/dev/null || { echo "❌ requests 未安装，请运行: pip install requests"; exit 1; }
python3 -c "import matplotlib" 2>/dev/null || echo "⚠️ matplotlib 未安装，将跳过图表生成。安装命令: pip install matplotlib"
python3 -c "import numpy" 2>/dev/null || echo "⚠️ numpy 未安装，将跳过部分分析。安装命令: pip install numpy"

echo "✅ 依赖检查完成"
echo ""

# 运行测试
echo "🚀 开始运行测试..."
python3 test_quiz_probability.py

echo ""
echo "📋 测试完成！生成的文件:"
echo "   - quiz_test_results.json (详细数据)"
echo "   - quiz_probability_analysis.png (可视化图表)"