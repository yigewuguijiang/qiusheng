// 游戏逻辑模块
const crypto = require('crypto');

class GameLogic {
    // 生成随机数（使用crypto真随机）
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

    // 生成随机字符串
    static generateToken(length = 32) {
        return crypto.randomBytes(length).toString('hex');
    }

    // Quiz 游戏逻辑
    static quiz = {
        // 前6题必选类别
        requiredCategories: ['常识', '英语', '数学', '语文', '音乐', '体育'],
        
        // 获取随机题目
        getRandomQuestion(questions, seenIds = [], questionIndex = 0) {
            const availableQuestions = questions.filter(q => !seenIds.includes(q.id));
            if (availableQuestions.length === 0) return null;
            
            // 前6题确保各类别各一道
            if (questionIndex < 6) {
                const requiredCategory = this.requiredCategories[questionIndex];
                const categoryQuestions = availableQuestions.filter(q => q.category === requiredCategory);
                
                if (categoryQuestions.length > 0) {
                    const randomIndex = GameLogic.randomInt(0, categoryQuestions.length - 1);
                    return categoryQuestions[randomIndex];
                }
            }
            
            // 第7题及以后完全随机
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

    // Slot 游戏逻辑 - 新的金额概率系统
    static slot = {
        spin() {
            const rand = Math.random();
            let reward = '0';
            
            // 10%概率加20 20%概率加10 20概率减10 10概率减20 40概率3个图案不一样就啥也没有
            if (rand < 0.1) {
                reward = '+20';
            } else if (rand < 0.3) {  // 0.1-0.3 = 20%
                reward = '+10';
            } else if (rand < 0.5) {  // 0.3-0.5 = 20%
                reward = '-10';
            } else if (rand < 0.6) {  // 0.5-0.6 = 10%
                reward = '-20';
            } else {
                reward = '0';  // 60%-100% = 40%
            }
            
            // 生成显示用的转轮
            const amounts = ['+20', '+10', '-10', '-20', '0'];
            let reels;
            
            if (reward === '0') {
                // 40%概率：3个图案不一样就啥也没有
                do {
                    reels = [
                        amounts[GameLogic.randomInt(0, amounts.length - 1)],
                        amounts[GameLogic.randomInt(0, amounts.length - 1)],
                        amounts[GameLogic.randomInt(0, amounts.length - 1)]
                    ];
                } while (reels[0] === reels[1] || reels[1] === reels[2] || reels[0] === reels[2]);
            } else {
                // 有奖时：显示对应的金额
                reels = [reward, reward, reward];
            }
            
            return {
                reels,
                reward,
                isWin: reward !== '0'
            };
        }
    };

    // Scratch 刮刮卡游戏逻辑 - 新的金额系统
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
            
            // 生成20个玩家号码槽，每个都有金额
            const slots = [];
            
            for (let i = 0; i < 20; i++) {
                const num = GameLogic.randomInt(1, 99);
                
                // 每个号码都有一个金额 - 根据概率分配
                const rand = Math.random();
                let amount;
                if (rand < 0.1) {
                    amount = '+30';  // 10%概率
                } else if (rand < 0.3) {
                    amount = '+20';  // 20%概率
                } else if (rand < 0.6) {
                    amount = '+10';  // 30%概率
                } else {
                    amount = '0';    // 40%概率无奖
                }
                
                // 只有匹配中奖号码才能获得奖励
                const isWinningNumber = winningNumbers.includes(num);
                const finalAmount = isWinningNumber ? amount : '0';
                
                slots.push({ 
                    num, 
                    amount: amount,  // 显示的金额
                    prize: finalAmount === '0' ? null : finalAmount  // 实际奖励
                });
            }
            
            return {
                winningNumbers,
                slots
            };
        }
    };

    // Spin 转盘游戏逻辑 - 生存直播挑战版
    static spin = {
        challenges: [
            '2元买吃的',
            'Quiz',
            'Scratch', 
            'Slot',
            '集体10个深蹲',
            '和路人美女要微信',
            '和路人美女合照',
            '给路人吉他唱歌打分',
            '集体热舞1分钟',
            '集体10个俯卧撑',
            '公主抱下蹲5个',
            '要路人帅哥微信',
            '找路人要吃的',
            '和路人音准比拼',
            '和路人歌手battle',
            '找路人妹妹合唱',
            '回答队友真心话',
            '连续夸赞路人美女30秒',
            '人群中大声清唱10秒',
            '转盘次数+2'
        ],
        
        // 权重数组：Quiz权重为3，其他为1
        weights: [
            1, // 2元买吃的
            3, // Quiz (3倍概率)
            1, // Scratch
            1, // Slot
            1, // 集体10个深蹲
            1, // 和路人美女要微信
            1, // 和路人美女合照
            1, // 给路人吉他唱歌打分
            1, // 集体热舞1分钟
            1, // 集体10个俯卧撑
            1, // 公主抱下蹲5个
            1, // 要路人帅哥微信
            1, // 找路人要吃的
            1, // 和路人音准比拼
            1, // 和路人歌手battle
            1, // 找路人妹妹合唱
            1, // 回答队友真心话
            1, // 连续夸赞路人美女30秒
            1, // 人群中大声清唱10秒
            1  // 转盘次数+2
        ],
        
        names: ['乌龟', '麻瓜', '大彪'],
        
        // 集体任务不需要加名字
        groupTasks: ['集体10个深蹲', '集体热舞1分钟', '集体10个俯卧撑', '公主抱下蹲5个', '转盘次数+2'],

        // 根据权重随机选择挑战（使用crypto真随机）
        getWeightedRandomChallenge() {
            const totalWeight = this.weights.reduce((sum, weight) => sum + weight, 0);
            // 使用crypto生成0到1之间的随机数
            const randomBytes = crypto.randomBytes(4);
            const randomValue = randomBytes.readUInt32BE(0) / 0xFFFFFFFF;
            let random = randomValue * totalWeight;
            
            for (let i = 0; i < this.weights.length; i++) {
                random -= this.weights[i];
                if (random <= 0) {
                    return i;
                }
            }
            return 0; // fallback
        },

        spin() {
            // 使用权重随机选择实际的挑战
            const actualChallengeIndex = this.getWeightedRandomChallenge();
            let challenge = this.challenges[actualChallengeIndex];
            
            // 如果不是集体任务，随机加上一个人名
            if (!this.groupTasks.includes(challenge)) {
                const randomName = this.names[GameLogic.randomInt(0, this.names.length - 1)];
                challenge = `${randomName}: ${challenge}`;
            }
            
            // 计算显示角度（基于实际选择的挑战）
            const segmentAngle = 360 / this.challenges.length;  // 20个任务，每个18度
            const centerAngle = actualChallengeIndex * segmentAngle + segmentAngle / 2;
            const randomOffset = GameLogic.randomInt(-6, 6);  // ±6度偏移，确保在扇形内
            const angle = (centerAngle + randomOffset) % 360;
            
            return {
                prize: challenge,
                angle,
                success: true
            };
        }
    };
}

module.exports = GameLogic;