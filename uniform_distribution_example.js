// 如果需要完美均匀分布的替代方案
class UniformDistribution {
    static shuffledQuestions = [];
    static currentIndex = 0;
    
    // 洗牌算法 - 确保每道题只出现一次
    static shuffle(questions) {
        const shuffled = [...questions];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = GameLogic.randomInt(0, i);
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }
    
    // 均匀分布的题目选择
    static getUniformQuestion(questions) {
        // 如果用完了所有题目，重新洗牌
        if (this.currentIndex >= this.shuffledQuestions.length) {
            this.shuffledQuestions = this.shuffle(questions);
            this.currentIndex = 0;
        }
        
        return this.shuffledQuestions[this.currentIndex++];
    }
}

// 对比两种方法：
// 1. 真随机（当前方法）：GameLogic.quiz.getRandomQuestion()
//    - 符合自然随机分布
//    - 有些题目可能多次出现，有些可能不出现
//    - 变异系数通常30-60%
//
// 2. 洗牌算法：UniformDistribution.getUniformQuestion()
//    - 完美均匀分布
//    - 每道题恰好出现一次（在一轮中）
//    - 变异系数接近0%