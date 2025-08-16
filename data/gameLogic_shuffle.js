// 使用洗牌算法的版本，保证更均匀的题目分布
const crypto = require('crypto');

class GameLogicShuffle {
    // Fisher-Yates 洗牌算法
    static shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = this.randomInt(0, i);
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }
    
    // Quiz 游戏逻辑 - 洗牌版本
    static quiz = {
        // 存储每个用户的题目队列
        userQueues: new Map(),
        
        // 获取随机题目（洗牌版本）
        getRandomQuestion(questions, seenIds = [], questionIndex = 0, username = 'default') {
            // 如果是新用户或队列为空，创建新的洗牌队列
            if (!this.userQueues.has(username) || this.userQueues.get(username).length === 0) {
                const shuffled = GameLogicShuffle.shuffleArray(questions);
                this.userQueues.set(username, shuffled);
            }
            
            const queue = this.userQueues.get(username);
            const availableQuestions = queue.filter(q => !seenIds.includes(q.id));
            
            if (availableQuestions.length === 0) {
                // 所有题目都用完了，重新洗牌
                const shuffled = GameLogicShuffle.shuffleArray(questions);
                this.userQueues.set(username, shuffled);
                return shuffled[0];
            }
            
            // 返回队列中的第一个可用题目
            return availableQuestions[0];
        },
        
        // 清理用户队列（可选，用于释放内存）
        clearUserQueue(username) {
            this.userQueues.delete(username);
        }
    };
    
    // 原始的randomInt函数保持不变
    static randomInt(min, max) {
        const range = max - min + 1;
        const bytesNeeded = Math.ceil(Math.log2(range) / 8);
        const maxValue = Math.pow(2, bytesNeeded * 8);
        
        let randomValue;
        do {
            randomValue = crypto.randomBytes(bytesNeeded).readUIntBE(0, bytesNeeded);
        } while (randomValue >= maxValue - (maxValue % range));
        
        return min + (randomValue % range);
    }
}

// 使用示例：
// 这种方法保证在400次请求内，每道题都会被选中恰好一次
// 然后重新洗牌，开始新的循环

module.exports = GameLogicShuffle;