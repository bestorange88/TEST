import { Router } from 'express';
import bcryptjs from 'bcryptjs';
import db from '../models/db.js';
import { authMiddleware, adminMiddleware } from '../middleware/auth.js';

const router = Router();

// Dashboard stats
router.get('/stats', authMiddleware, adminMiddleware, (req, res) => {
  const userCount = db.prepare('SELECT COUNT(*) as count FROM users WHERE role = ?').get('user');
  const orderCount = db.prepare('SELECT COUNT(*) as count FROM orders').get();
  const pendingDeposits = db.prepare('SELECT COUNT(*) as count FROM deposits WHERE status = ?').get('pending');
  const pendingWithdrawals = db.prepare('SELECT COUNT(*) as count FROM withdrawals WHERE status = ?').get('pending');
  const totalDeposits = db.prepare("SELECT COALESCE(SUM(amount), 0) as total FROM deposits WHERE status = 'approved'").get();
  const totalWithdrawals = db.prepare("SELECT COALESCE(SUM(amount), 0) as total FROM withdrawals WHERE status = 'approved'").get();

  res.json({
    code: 200,
    data: {
      user_count: userCount.count,
      order_count: orderCount.count,
      pending_deposits: pendingDeposits.count,
      pending_withdrawals: pendingWithdrawals.count,
      total_deposits: totalDeposits.total,
      total_withdrawals: totalWithdrawals.total,
    }
  });
});

// User management
router.get('/users', authMiddleware, adminMiddleware, (req, res) => {
  const { page = 1, size = 20, keyword } = req.query;
  const offset = (page - 1) * size;
  let users, total;
  if (keyword) {
    users = db.prepare("SELECT id, username, real_name, phone, credit_score, verified, balance, frozen_balance, total_profit, role, created_at FROM users WHERE username LIKE ? OR real_name LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?")
      .all(`%${keyword}%`, `%${keyword}%`, Number(size), offset);
    total = db.prepare("SELECT COUNT(*) as count FROM users WHERE username LIKE ? OR real_name LIKE ?")
      .get(`%${keyword}%`, `%${keyword}%`);
  } else {
    users = db.prepare("SELECT id, username, real_name, phone, credit_score, verified, balance, frozen_balance, total_profit, role, created_at FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?")
      .all(Number(size), offset);
    total = db.prepare("SELECT COUNT(*) as count FROM users").get();
  }
  res.json({ code: 200, data: { list: users, total: total.count } });
});

router.put('/user/:id', authMiddleware, adminMiddleware, (req, res) => {
  const { balance, credit_score, verified, role } = req.body;
  const updates = [];
  const values = [];
  if (balance !== undefined) { updates.push('balance = ?'); values.push(balance); }
  if (credit_score !== undefined) { updates.push('credit_score = ?'); values.push(credit_score); }
  if (verified !== undefined) { updates.push('verified = ?'); values.push(verified); }
  if (role !== undefined) { updates.push('role = ?'); values.push(role); }
  if (updates.length === 0) return res.json({ code: 400, msg: '无更新内容' });

  values.push(req.params.id);
  db.prepare(`UPDATE users SET ${updates.join(', ')} WHERE id = ?`).run(...values);
  res.json({ code: 200, msg: '更新成功' });
});

router.post('/user/:id/reset-password', authMiddleware, adminMiddleware, (req, res) => {
  const newPwd = req.body.password || '123456';
  const hashed = bcryptjs.hashSync(newPwd, 10);
  db.prepare('UPDATE users SET password = ? WHERE id = ?').run(hashed, req.params.id);
  res.json({ code: 200, msg: '密码已重置为: ' + newPwd });
});

// Product management
router.get('/products', authMiddleware, adminMiddleware, (req, res) => {
  const products = db.prepare('SELECT * FROM products ORDER BY sort_order ASC, id ASC').all();
  res.json({ code: 200, data: products });
});

router.post('/product', authMiddleware, adminMiddleware, (req, res) => {
  const { name, symbol, price, high_24h, low_24h, volume_24h, amount_24h, profit_rate, status, sort_order } = req.body;
  if (!name || !symbol) return res.json({ code: 400, msg: '请填写产品名称和代码' });

  db.prepare(`INSERT INTO products (name, symbol, price, high_24h, low_24h, volume_24h, amount_24h, profit_rate, status, sort_order)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
    .run(name, symbol, price || 0, high_24h || 0, low_24h || 0, volume_24h || '0', amount_24h || '0', profit_rate || 85, status ?? 1, sort_order || 0);
  res.json({ code: 200, msg: '添加成功' });
});

router.put('/product/:id', authMiddleware, adminMiddleware, (req, res) => {
  const { name, symbol, price, high_24h, low_24h, volume_24h, amount_24h, profit_rate, status, sort_order } = req.body;
  db.prepare(`UPDATE products SET name = ?, symbol = ?, price = ?, high_24h = ?, low_24h = ?, volume_24h = ?, amount_24h = ?, profit_rate = ?, status = ?, sort_order = ? WHERE id = ?`)
    .run(name, symbol, price, high_24h, low_24h, volume_24h, amount_24h, profit_rate, status, sort_order, req.params.id);
  res.json({ code: 200, msg: '更新成功' });
});

router.delete('/product/:id', authMiddleware, adminMiddleware, (req, res) => {
  db.prepare('DELETE FROM products WHERE id = ?').run(req.params.id);
  res.json({ code: 200, msg: '删除成功' });
});

// Order management
router.get('/orders', authMiddleware, adminMiddleware, (req, res) => {
  const { page = 1, size = 20, status, user_id } = req.query;
  const offset = (page - 1) * size;
  let where = '1=1';
  const params = [];
  if (status) { where += ' AND o.status = ?'; params.push(status); }
  if (user_id) { where += ' AND o.user_id = ?'; params.push(Number(user_id)); }

  const list = db.prepare(`SELECT o.*, u.username FROM orders o LEFT JOIN users u ON o.user_id = u.id WHERE ${where} ORDER BY o.created_at DESC LIMIT ? OFFSET ?`)
    .all(...params, Number(size), offset);
  const total = db.prepare(`SELECT COUNT(*) as count FROM orders o WHERE ${where}`).get(...params);
  res.json({ code: 200, data: { list, total: total.count } });
});

router.put('/order/:id', authMiddleware, adminMiddleware, (req, res) => {
  const { profit, status } = req.body;
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.json({ code: 404, msg: '订单不存在' });

  if (status === 'closed' && order.status === 'open') {
    const finalProfit = profit !== undefined ? profit : 0;
    const returnAmount = order.amount + finalProfit;

    db.prepare(`UPDATE orders SET profit = ?, status = 'closed', closed_at = datetime('now') WHERE id = ?`)
      .run(finalProfit, order.id);

    if (returnAmount > 0) {
      db.prepare('UPDATE users SET balance = balance + ?, total_profit = total_profit + ? WHERE id = ?')
        .run(returnAmount, finalProfit, order.user_id);
    } else {
      db.prepare('UPDATE users SET total_profit = total_profit + ? WHERE id = ?')
        .run(finalProfit, order.user_id);
    }
  }
  res.json({ code: 200, msg: '更新成功' });
});

// Deposit management
router.get('/deposits', authMiddleware, adminMiddleware, (req, res) => {
  const { page = 1, size = 20, status } = req.query;
  const offset = (page - 1) * size;
  let where = '1=1';
  const params = [];
  if (status) { where += ' AND d.status = ?'; params.push(status); }

  const list = db.prepare(`SELECT d.*, u.username FROM deposits d LEFT JOIN users u ON d.user_id = u.id WHERE ${where} ORDER BY d.created_at DESC LIMIT ? OFFSET ?`)
    .all(...params, Number(size), offset);
  const total = db.prepare(`SELECT COUNT(*) as count FROM deposits d WHERE ${where}`).get(...params);
  res.json({ code: 200, data: { list, total: total.count } });
});

router.put('/deposit/:id', authMiddleware, adminMiddleware, (req, res) => {
  const { status } = req.body;
  const deposit = db.prepare('SELECT * FROM deposits WHERE id = ?').get(req.params.id);
  if (!deposit) return res.json({ code: 404, msg: '记录不存在' });
  if (deposit.status !== 'pending') return res.json({ code: 400, msg: '该记录已处理' });

  db.prepare("UPDATE deposits SET status = ?, reviewed_at = datetime('now') WHERE id = ?")
    .run(status, deposit.id);

  if (status === 'approved') {
    db.prepare('UPDATE users SET balance = balance + ? WHERE id = ?')
      .run(deposit.amount, deposit.user_id);
  }
  res.json({ code: 200, msg: '处理成功' });
});

// Withdrawal management
router.get('/withdrawals', authMiddleware, adminMiddleware, (req, res) => {
  const { page = 1, size = 20, status } = req.query;
  const offset = (page - 1) * size;
  let where = '1=1';
  const params = [];
  if (status) { where += ' AND w.status = ?'; params.push(status); }

  const list = db.prepare(`SELECT w.*, u.username, b.bank_name, b.card_number FROM withdrawals w
    LEFT JOIN users u ON w.user_id = u.id LEFT JOIN bank_cards b ON w.bank_card_id = b.id
    WHERE ${where} ORDER BY w.created_at DESC LIMIT ? OFFSET ?`)
    .all(...params, Number(size), offset);
  const total = db.prepare(`SELECT COUNT(*) as count FROM withdrawals w WHERE ${where}`).get(...params);
  res.json({ code: 200, data: { list, total: total.count } });
});

router.put('/withdrawal/:id', authMiddleware, adminMiddleware, (req, res) => {
  const { status } = req.body;
  const withdrawal = db.prepare('SELECT * FROM withdrawals WHERE id = ?').get(req.params.id);
  if (!withdrawal) return res.json({ code: 404, msg: '记录不存在' });
  if (withdrawal.status !== 'pending') return res.json({ code: 400, msg: '该记录已处理' });

  db.prepare("UPDATE withdrawals SET status = ?, reviewed_at = datetime('now') WHERE id = ?")
    .run(status, withdrawal.id);

  if (status === 'rejected') {
    db.prepare('UPDATE users SET balance = balance + ?, frozen_balance = frozen_balance - ? WHERE id = ?')
      .run(withdrawal.amount, withdrawal.amount, withdrawal.user_id);
  } else if (status === 'approved') {
    db.prepare('UPDATE users SET frozen_balance = frozen_balance - ? WHERE id = ?')
      .run(withdrawal.amount, withdrawal.user_id);
  }
  res.json({ code: 200, msg: '处理成功' });
});

// Notice management
router.get('/notices', authMiddleware, adminMiddleware, (req, res) => {
  const notices = db.prepare('SELECT * FROM notices ORDER BY created_at DESC').all();
  res.json({ code: 200, data: notices });
});

router.post('/notice', authMiddleware, adminMiddleware, (req, res) => {
  const { title, content, type } = req.body;
  if (!title || !content) return res.json({ code: 400, msg: '请填写标题和内容' });
  db.prepare('INSERT INTO notices (title, content, type) VALUES (?, ?, ?)').run(title, content, type || 'system');
  res.json({ code: 200, msg: '添加成功' });
});

router.put('/notice/:id', authMiddleware, adminMiddleware, (req, res) => {
  const { title, content, status } = req.body;
  db.prepare('UPDATE notices SET title = ?, content = ?, status = ? WHERE id = ?')
    .run(title, content, status, req.params.id);
  res.json({ code: 200, msg: '更新成功' });
});

router.delete('/notice/:id', authMiddleware, adminMiddleware, (req, res) => {
  db.prepare('DELETE FROM notices WHERE id = ?').run(req.params.id);
  res.json({ code: 200, msg: '删除成功' });
});

export default router;
