const express = require('express');
const path = require('path');

// 导入本地游戏数据和逻辑
const questions = require('./data/questions');
const GameLogic = require('./data/gameLogic');

const app = express();
const PORT = process.env.PORT || 3000;

// 视图引擎设置
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// 中间件
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 安全头
app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    next();
});

// 生成随机用户名
function generateUsername() {
    const adjectives = ['快乐', '幸运', '聪明', '勇敢', '神秘', '酷炫', '超级', '无敌'];
    const nouns = ['玩家', '高手', '大师', '英雄', '冠军', '传奇', '战士', '天才'];
    const adj = adjectives[Math.floor(Math.random() * adjectives.length)];
    const noun = nouns[Math.floor(Math.random() * nouns.length)];
    const num = Math.floor(Math.random() * 9999);
    return `${adj}${noun}${num}`;
}

// 存储用户会话数据 (简单内存存储)
const userSessions = new Map();

// 路由
app.get('/', (req, res) => {
    res.render('index');
});

app.get('/quiz', (req, res) => {
    const username = generateUsername();
    res.render('quiz', { username });
});

app.get('/slot', (req, res) => {
    const username = generateUsername();
    res.render('slot', { username });
});

app.get('/scratch', (req, res) => {
    const username = generateUsername();
    res.render('scratch', { username });
});

app.get('/spin', (req, res) => {
    const username = generateUsername();
    res.render('spin', { username });
});

// Quiz API 路由
app.get('/api/user-info', (req, res) => {
    const username = generateUsername();
    res.json({ success: true, username });
});

app.post('/api/quiz/next', (req, res) => {
    try {
        const { username, seen = [] } = req.body;
        
        const question = GameLogic.quiz.getRandomQuestion(questions, seen);
        if (!question) {
            return res.json({ success: false, message: '没有更多题目了' });
        }
        
        const token = GameLogic.generateToken(16);
        const signature = GameLogic.generateToken(16);
        
        // 存储问题信息
        if (!userSessions.has(username)) {
            userSessions.set(username, {});
        }
        userSessions.get(username)[token] = {
            questionId: question.id,
            timestamp: Date.now()
        };
        
        res.json({
            success: true,
            question: {
                id: question.id,
                question: question.question,
                options: question.options
            },
            token,
            signature
        });
    } catch (error) {
        console.error('Quiz next error:', error);
        res.status(500).json({ success: false, message: '服务器错误' });
    }
});

app.post('/api/quiz/submit', (req, res) => {
    try {
        const { username, answers = [] } = req.body;
        
        let correctCount = 0;
        const userSession = userSessions.get(username) || {};
        
        for (const answer of answers) {
            const sessionData = userSession[answer.token];
            if (sessionData) {
                const question = questions.find(q => q.id === sessionData.questionId);
                if (question && GameLogic.quiz.validateAnswer(question, answer.answerIndex)) {
                    correctCount++;
                }
            }
        }
        
        // 清理用户会话
        userSessions.delete(username);
        
        res.json({
            success: true,
            score: correctCount,
            total: answers.length,
            proof: GameLogic.generateToken(8)
        });
    } catch (error) {
        console.error('Quiz submit error:', error);
        res.status(500).json({ success: false, message: '提交失败' });
    }
});

// Slot API 路由
app.post('/api/slot/spin', (req, res) => {
    try {
        const result = GameLogic.slot.spin();
        res.json({
            success: true,
            reels: result.reels,
            reward: result.reward
        });
    } catch (error) {
        console.error('Slot error:', error);
        res.status(500).json({ success: false, message: '老虎机故障' });
    }
});

// Scratch API 路由
app.post('/api/scratch', (req, res) => {
    try {
        const card = GameLogic.scratch.generateCard();
        res.json({
            success: true,
            winningNumbers: card.winningNumbers,
            slots: card.slots
        });
    } catch (error) {
        console.error('Scratch error:', error);
        res.status(500).json({ success: false, message: '刮刮卡生成失败' });
    }
});

// Spin API 路由
app.post('/api/spin', (req, res) => {
    try {
        const result = GameLogic.spin.spin();
        res.json({
            success: true,
            prize: result.prize,
            angle: result.angle
        });
    } catch (error) {
        console.error('Spin error:', error);
        res.status(500).json({ success: false, message: '转盘故障' });
    }
});

// 健康检查
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        games: ['quiz', 'slot', 'scratch', 'spin'],
        questions: questions.length
    });
});

// 404 处理
app.use('*', (req, res) => {
    res.redirect('/');
});

// 错误处理
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).redirect('/');
});

app.listen(PORT, () => {
    console.log(`🎮 游戏服务器运行在端口 ${PORT}`);
    console.log(`📚 题库包含 ${questions.length} 道题目`);
    console.log(`🌐 访问 http://localhost:${PORT} 开始游戏`);
});