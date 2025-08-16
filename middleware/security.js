const rateLimit = require('express-rate-limit');
const crypto = require('crypto');

// 存储用户行为数据
const userBehavior = new Map();
const ipBlacklist = new Set();
const suspiciousPatterns = new Map();

// 生成设备指纹
function generateFingerprint(req) {
    const components = [
        req.headers['user-agent'] || '',
        req.headers['accept-language'] || '',
        req.headers['accept-encoding'] || '',
        req.headers['accept'] || '',
        req.connection.remoteAddress || req.ip
    ];
    return crypto.createHash('md5').update(components.join('|')).digest('hex');
}

// IP黑名单检查
function checkBlacklist(req, res, next) {
    const ip = req.ip || req.connection.remoteAddress;
    
    if (ipBlacklist.has(ip)) {
        return res.status(403).json({
            success: false,
            message: '访问被拒绝',
            code: 'BLACKLISTED'
        });
    }
    
    next();
}

// 设备指纹验证
function deviceFingerprint(req, res, next) {
    const fingerprint = generateFingerprint(req);
    req.fingerprint = fingerprint;
    
    // 检查指纹变化频率
    const fpHistory = suspiciousPatterns.get(req.ip) || { fingerprints: new Set(), lastChange: 0 };
    fpHistory.fingerprints.add(fingerprint);
    
    // 如果一个IP在短时间内有多个指纹，可能是脚本
    if (fpHistory.fingerprints.size > 3 && Date.now() - fpHistory.lastChange < 300000) { // 5分钟内超过3个指纹
        ipBlacklist.add(req.ip);
        return res.status(403).json({
            success: false,
            message: '异常行为检测',
            code: 'SUSPICIOUS_ACTIVITY'
        });
    }
    
    fpHistory.lastChange = Date.now();
    suspiciousPatterns.set(req.ip, fpHistory);
    
    next();
}

// 行为分析中间件
function behaviorAnalysis(req, res, next) {
    const ip = req.ip || req.connection.remoteAddress;
    const now = Date.now();
    
    // 获取或创建用户行为记录
    let behavior = userBehavior.get(ip) || {
        requests: [],
        firstSeen: now,
        totalRequests: 0,
        suspicionScore: 0,
        lastRequestTime: 0,
        patterns: {
            avgInterval: 0,
            minInterval: Infinity,
            consistency: 0
        }
    };
    
    // 记录请求时间
    behavior.requests.push(now);
    behavior.totalRequests++;
    
    // 只保留最近100次请求
    if (behavior.requests.length > 100) {
        behavior.requests.shift();
    }
    
    // 分析请求模式
    if (behavior.requests.length > 5) {
        const intervals = [];
        for (let i = 1; i < behavior.requests.length; i++) {
            intervals.push(behavior.requests[i] - behavior.requests[i-1]);
        }
        
        const avgInterval = intervals.reduce((a, b) => a + b) / intervals.length;
        const minInterval = Math.min(...intervals);
        const variance = intervals.reduce((sum, interval) => sum + Math.pow(interval - avgInterval, 2), 0) / intervals.length;
        const stdDev = Math.sqrt(variance);
        
        // 更新模式数据
        behavior.patterns.avgInterval = avgInterval;
        behavior.patterns.minInterval = minInterval;
        behavior.patterns.consistency = stdDev / avgInterval; // 越小越一致
        
        // 计算可疑分数
        let suspicionScore = 0;
        
        // 请求间隔太一致（可能是定时脚本）
        if (behavior.patterns.consistency < 0.1 && behavior.requests.length > 20) {
            suspicionScore += 30;
        }
        
        // 请求间隔太短
        if (minInterval < 100) { // 小于100ms
            suspicionScore += 40;
        }
        
        // 平均间隔太短
        if (avgInterval < 1000 && behavior.requests.length > 30) { // 平均小于1秒
            suspicionScore += 20;
        }
        
        // 请求量异常
        if (behavior.totalRequests > 1000 && (now - behavior.firstSeen) < 3600000) { // 1小时内超过1000次
            suspicionScore += 30;
        }
        
        behavior.suspicionScore = suspicionScore;
        
        // 如果可疑分数太高，加入黑名单
        if (suspicionScore >= 70) {
            ipBlacklist.add(ip);
            return res.status(403).json({
                success: false,
                message: '检测到异常访问模式',
                code: 'ABNORMAL_PATTERN'
            });
        }
    }
    
    behavior.lastRequestTime = now;
    userBehavior.set(ip, behavior);
    
    // 传递行为数据供后续使用
    req.userBehavior = behavior;
    
    next();
}

// 基础速率限制
const basicRateLimit = rateLimit({
    windowMs: 60 * 1000, // 1分钟
    max: 30, // 最多30次
    message: '请求过于频繁，请稍后再试',
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
        // 记录过度请求的IP
        const ip = req.ip || req.connection.remoteAddress;
        const behavior = userBehavior.get(ip) || {};
        behavior.suspicionScore = (behavior.suspicionScore || 0) + 10;
        userBehavior.set(ip, behavior);
        
        res.status(429).json({
            success: false,
            message: '请求过于频繁，请稍后再试',
            retryAfter: req.rateLimit.resetTime
        });
    }
});

// 严格速率限制（用于API）
const strictRateLimit = rateLimit({
    windowMs: 15 * 60 * 1000, // 15分钟
    max: 100, // 最多100次
    skipSuccessfulRequests: false,
    standardHeaders: true,
    legacyHeaders: false
});

// 动态速率限制（基于用户行为）
function dynamicRateLimit(req, res, next) {
    const behavior = req.userBehavior || {};
    
    // 根据可疑分数调整限制
    if (behavior.suspicionScore > 50) {
        // 高度可疑用户，强制冷却
        const lastRequest = behavior.lastRequestTime || 0;
        const cooldown = 10000; // 10秒冷却
        
        if (Date.now() - lastRequest < cooldown) {
            return res.status(429).json({
                success: false,
                message: '请求过快，请等待',
                cooldownRemaining: cooldown - (Date.now() - lastRequest)
            });
        }
    }
    
    next();
}

// Session验证
function requireSession(req, res, next) {
    if (!req.session || !req.session.initialized) {
        return res.status(403).json({
            success: false,
            message: '请先访问页面',
            code: 'NO_SESSION'
        });
    }
    
    // 检查session年龄
    const sessionAge = Date.now() - (req.session.createdAt || 0);
    if (sessionAge > 24 * 60 * 60 * 1000) { // 24小时
        req.session.destroy();
        return res.status(403).json({
            success: false,
            message: 'Session已过期',
            code: 'SESSION_EXPIRED'
        });
    }
    
    next();
}

// CSRF保护
function csrfProtection(req, res, next) {
    if (req.method === 'POST') {
        const token = req.headers['x-csrf-token'] || req.body.csrfToken;
        const sessionToken = req.session?.csrfToken;
        
        if (!token || token !== sessionToken) {
            return res.status(403).json({
                success: false,
                message: '无效的请求',
                code: 'CSRF_FAILED'
            });
        }
    }
    
    next();
}

// 清理过期数据（定期执行）
function cleanupOldData() {
    const now = Date.now();
    const maxAge = 24 * 60 * 60 * 1000; // 24小时
    
    // 清理用户行为数据
    for (const [ip, behavior] of userBehavior.entries()) {
        if (now - behavior.lastRequestTime > maxAge) {
            userBehavior.delete(ip);
        }
    }
    
    // 清理可疑模式数据
    for (const [ip, pattern] of suspiciousPatterns.entries()) {
        if (now - pattern.lastChange > maxAge) {
            suspiciousPatterns.delete(ip);
        }
    }
    
    // 定期清理黑名单（可选）
    // ipBlacklist.clear();
}

// 每小时清理一次
setInterval(cleanupOldData, 60 * 60 * 1000);

// 导出中间件
module.exports = {
    checkBlacklist,
    deviceFingerprint,
    behaviorAnalysis,
    basicRateLimit,
    strictRateLimit,
    dynamicRateLimit,
    requireSession,
    csrfProtection,
    generateFingerprint,
    
    // 工具函数
    addToBlacklist: (ip) => ipBlacklist.add(ip),
    removeFromBlacklist: (ip) => ipBlacklist.delete(ip),
    getBlacklist: () => Array.from(ipBlacklist),
    getUserBehavior: (ip) => userBehavior.get(ip),
    clearUserBehavior: (ip) => userBehavior.delete(ip)
};