import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'central-settlement-secret-key-2025';

export function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ code: 401, msg: '请先登录' });
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch {
    return res.status(401).json({ code: 401, msg: '登录已过期，请重新登录' });
  }
}

export function adminMiddleware(req, res, next) {
  if (req.user.role !== 'admin') {
    return res.status(403).json({ code: 403, msg: '无权限访问' });
  }
  next();
}

export { JWT_SECRET };
