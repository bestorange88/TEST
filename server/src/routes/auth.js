import { Router } from 'express';
import bcryptjs from 'bcryptjs';
import jwt from 'jsonwebtoken';
import db from '../models/db.js';
import { JWT_SECRET } from '../middleware/auth.js';

const router = Router();

router.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.json({ code: 400, msg: '请输入账号和密码' });

  const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
  if (!user) return res.json({ code: 400, msg: '账号不存在' });

  if (!bcryptjs.compareSync(password, user.password)) {
    return res.json({ code: 400, msg: '密码错误' });
  }

  const token = jwt.sign(
    { id: user.id, username: user.username, role: user.role },
    JWT_SECRET,
    { expiresIn: '7d' }
  );

  res.json({
    code: 200,
    msg: '登录成功',
    data: {
      token,
      user: {
        id: user.id,
        username: user.username,
        real_name: user.real_name,
        credit_score: user.credit_score,
        verified: user.verified,
        balance: user.balance,
        total_profit: user.total_profit,
        today_profit: user.today_profit,
        role: user.role,
      }
    }
  });
});

router.post('/register', (req, res) => {
  const { username, password, invite_code } = req.body;
  if (!username || !password) return res.json({ code: 400, msg: '请输入账号和密码' });
  if (password.length < 6) return res.json({ code: 400, msg: '密码至少6位' });

  const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
  if (existing) return res.json({ code: 400, msg: '账号已存在' });

  const hashed = bcryptjs.hashSync(password, 10);
  const result = db.prepare('INSERT INTO users (username, password) VALUES (?, ?)').run(username, hashed);

  const token = jwt.sign(
    { id: result.lastInsertRowid, username, role: 'user' },
    JWT_SECRET,
    { expiresIn: '7d' }
  );

  res.json({
    code: 200,
    msg: '注册成功',
    data: { token, user: { id: result.lastInsertRowid, username, balance: 0 } }
  });
});

router.post('/change-password', (req, res) => {
  const { username, old_password, new_password } = req.body;
  if (!username || !old_password || !new_password) {
    return res.json({ code: 400, msg: '请填写完整信息' });
  }

  const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
  if (!user) return res.json({ code: 400, msg: '用户不存在' });
  if (!bcryptjs.compareSync(old_password, user.password)) {
    return res.json({ code: 400, msg: '原密码错误' });
  }

  const hashed = bcryptjs.hashSync(new_password, 10);
  db.prepare('UPDATE users SET password = ? WHERE id = ?').run(hashed, user.id);
  res.json({ code: 200, msg: '密码修改成功' });
});

export default router;
