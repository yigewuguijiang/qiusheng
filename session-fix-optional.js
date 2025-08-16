// 可选的Session修复方案
// 如果需要生产级Session存储，可以参考这个配置

const session = require('express-session');
const RedisStore = require('connect-redis')(session);
const redis = require('redis');

// 如果有Redis URL（Render等平台提供）
const redisClient = redis.createClient({
    url: process.env.REDIS_URL // Render会自动提供
});

// Session配置（替换原有配置）
const sessionConfig = {
    store: new RedisStore({ client: redisClient }),
    secret: process.env.SESSION_SECRET || 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: process.env.NODE_ENV === 'production',
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000 // 24小时
    }
};

// 如果没有Redis，使用文件存储（比MemoryStore好）
const FileStore = require('session-file-store')(session);
const fileSessionConfig = {
    store: new FileStore({
        path: './sessions',
        ttl: 86400, // 24小时
        reapInterval: 3600 // 1小时清理一次
    }),
    secret: process.env.SESSION_SECRET || 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: process.env.NODE_ENV === 'production',
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000
    }
};

module.exports = { sessionConfig, fileSessionConfig };