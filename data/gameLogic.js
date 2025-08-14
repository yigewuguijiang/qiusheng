// 游戏逻辑模块
const crypto = require('crypto');

class GameLogic {
    // 生成随机数
    static randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    // 生成随机字符串
    static generateToken(length = 32) {
        return crypto.randomBytes(length).toString('hex');
    }

    // Quiz 游戏逻辑
    static quiz = {
        // 获取随机题目
        getRandomQuestion(questions, seenIds = []) {
            const availableQuestions = questions.filter(q => !seenIds.includes(q.id));
            if (availableQuestions.length === 0) return null;
            
            const randomIndex = GameLogic.randomInt(0, availableQuestions.length - 1);
            return availableQuestions[randomIndex];
        },

        // 验证答案
        validateAnswer(question, answerIndex, token) {
            if (!question || answerIndex < 0 || answerIndex >= question.options.length) {
                return false;
            }
            return answerIndex === question.correct;
        },

        // 计算得分
        calculateScore(answers, questions) {
            let correct = 0;
            for (const answer of answers) {
                const question = questions.find(q => q.id === answer.questionId);
                if (question && this.validateAnswer(question, answer.answerIndex)) {
                    correct++;
                }
            }
            return correct;
        }
    };

    // Slot 游戏逻辑
    static slot = {
        symbols: ['苹果', '柠檬', '樱桃', '葡萄', '钻石', '七七七', '铃铛', '星星'],
        
        // 奖品配置 - 概率越小奖品越好
        rewards: [
            { pattern: ['七七七', '七七七', '七七七'], reward: '特等奖-1000积分', probability: 0.01 },
            { pattern: ['钻石', '钻石', '钻石'], reward: '一等奖-500积分', probability: 0.02 },
            { pattern: ['星星', '星星', '星星'], reward: '二等奖-200积分', probability: 0.05 },
            { pattern: ['苹果', '苹果', '苹果'], reward: '三等奖-50积分', probability: 0.08 },
            { pattern: ['樱桃', '樱桃', '樱桃'], reward: '四等奖-20积分', probability: 0.10 },
            { pattern: ['葡萄', '葡萄', '葡萄'], reward: '五等奖-10积分', probability: 0.12 }
        ],

        spin() {
            const rand = Math.random();
            
            // 检查是否中奖
            for (const config of this.rewards) {
                if (rand < config.probability) {
                    return {
                        reels: [...config.pattern],
                        reward: config.reward,
                        isWin: true
                    };
                }
            }
            
            // 不中奖，生成随机结果
            const reels = [
                this.symbols[GameLogic.randomInt(0, this.symbols.length - 1)],
                this.symbols[GameLogic.randomInt(0, this.symbols.length - 1)],
                this.symbols[GameLogic.randomInt(0, this.symbols.length - 1)]
            ];
            
            // 确保不是意外中奖
            const reelString = reels.join(',');
            const isAccidentalWin = this.rewards.some(config => 
                config.pattern.join(',') === reelString
            );
            
            if (isAccidentalWin) {
                // 修改一个轮子避免意外中奖
                reels[2] = this.symbols[GameLogic.randomInt(0, this.symbols.length - 1)];
            }
            
            return {
                reels: reels,
                reward: '谢谢惠顾',
                isWin: false
            };
        }
    };

    // Scratch 刮刮卡游戏逻辑
    static scratch = {
        // 生成刮刮卡
        generateCard() {
            // 生成5个中奖号码
            const winningNumbers = [];
            while (winningNumbers.length < 5) {
                const num = GameLogic.randomInt(1, 99);
                if (!winningNumbers.includes(num)) {
                    winningNumbers.push(num);
                }
            }
            
            // 生成20个玩家号码槽
            const slots = [];
            const prizes = ['10积分', '20积分', '50积分', '100积分', '200积分'];
            
            for (let i = 0; i < 20; i++) {
                const num = GameLogic.randomInt(1, 99);
                let prize = null;
                
                // 30% 概率中奖，但只有匹配中奖号码才真正中奖
                if (Math.random() < 0.3 && winningNumbers.includes(num)) {
                    prize = prizes[GameLogic.randomInt(0, prizes.length - 1)];
                }
                
                slots.push({ num, prize });
            }
            
            return {
                winningNumbers,
                slots
            };
        }
    };

    // Spin 转盘游戏逻辑
    static spin = {
        prizes: [
            { name: "-5元优惠", probability: 0.15, angle: 0 },
            { name: "免费一局", probability: 0.20, angle: 60 },
            { name: "再来一次", probability: 0.25, angle: 120 },
            { name: "9折优惠", probability: 0.10, angle: 180 },
            { name: "当天免费", probability: 0.05, angle: 240 },
            { name: "谢谢参与", probability: 0.25, angle: 300 }
        ],

        spin() {
            const rand = Math.random();
            let cumulativeProbability = 0;
            
            for (const prize of this.prizes) {
                cumulativeProbability += prize.probability;
                if (rand <= cumulativeProbability) {
                    return {
                        prize: prize.name,
                        angle: prize.angle + GameLogic.randomInt(-25, 25) // 添加随机偏差
                    };
                }
            }
            
            // 默认返回谢谢参与
            return {
                prize: "谢谢参与",
                angle: 300 + GameLogic.randomInt(-25, 25)
            };
        }
    };
}

module.exports = GameLogic;