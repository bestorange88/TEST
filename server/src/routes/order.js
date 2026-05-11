import { Router } from 'express';
import db from '../models/db.js';
import { authMiddleware } from '../middleware/auth.js';

const router = Router();

router.post('/create', authMiddleware, (req, res) => {
  const { product_id, direction, amount, duration } = req.body;
  if (!product_id || !direction || !amount || !duration) {
    return res.json({ code: 400, msg: '参数不完整' });
  }

  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(product_id);
  if (!product) return res.json({ code: 404, msg: '产品不存在' });

  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.user.id);
  if (user.balance < amount) return res.json({ code: 400, msg: '余额不足' });
  if (!user.verified) return res.json({ code: 400, msg: '请先完成实名认证' });

  const fluctuation = (Math.random() - 0.5) * 0.002;
  const openPrice = product.price * (1 + fluctuation);

  db.prepare('UPDATE users SET balance = balance - ? WHERE id = ?').run(amount, req.user.id);

  const result = db.prepare(`INSERT INTO orders (user_id, product_id, product_name, direction, amount, open_price, duration, profit_rate, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open')`).run(
    req.user.id, product_id, product.name, direction, amount, Number(openPrice.toFixed(5)), duration, product.profit_rate
  );

  // Schedule auto-close
  setTimeout(() => closeOrder(result.lastInsertRowid), duration * 1000);

  res.json({ code: 200, msg: '下单成功', data: { order_id: result.lastInsertRowid } });
});

function closeOrder(orderId) {
  const order = db.prepare('SELECT * FROM orders WHERE id = ? AND status = ?').get(orderId, 'open');
  if (!order) return;

  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(order.product_id);
  const fluctuation = (Math.random() - 0.5) * 0.002;
  const closePrice = product.price * (1 + fluctuation);

  let profit = 0;
  const isWin = Math.random() < 0.45;

  if (order.direction === 'up') {
    profit = isWin ? order.amount * (order.profit_rate / 100) : -order.amount;
  } else if (order.direction === 'down') {
    profit = isWin ? order.amount * (order.profit_rate / 100) : -order.amount;
  } else {
    profit = isWin ? order.amount * (order.profit_rate / 100) * 0.8 : -order.amount;
  }

  const returnAmount = order.amount + profit;

  db.prepare(`UPDATE orders SET close_price = ?, profit = ?, status = 'closed', closed_at = datetime('now') WHERE id = ?`)
    .run(Number(closePrice.toFixed(5)), Number(profit.toFixed(2)), orderId);

  if (returnAmount > 0) {
    db.prepare('UPDATE users SET balance = balance + ?, total_profit = total_profit + ?, today_profit = today_profit + ? WHERE id = ?')
      .run(returnAmount, profit, profit, order.user_id);
  } else {
    db.prepare('UPDATE users SET total_profit = total_profit + ?, today_profit = today_profit + ? WHERE id = ?')
      .run(profit, profit, order.user_id);
  }
}

router.get('/positions', authMiddleware, (req, res) => {
  const orders = db.prepare('SELECT * FROM orders WHERE user_id = ? AND status = ? ORDER BY created_at DESC')
    .all(req.user.id, 'open');
  res.json({ code: 200, data: orders });
});

router.get('/history', authMiddleware, (req, res) => {
  const { page = 1, size = 20 } = req.query;
  const offset = (page - 1) * size;
  const orders = db.prepare('SELECT * FROM orders WHERE user_id = ? AND status = ? ORDER BY closed_at DESC LIMIT ? OFFSET ?')
    .all(req.user.id, 'closed', Number(size), offset);
  const total = db.prepare('SELECT COUNT(*) as count FROM orders WHERE user_id = ? AND status = ?')
    .get(req.user.id, 'closed');
  res.json({ code: 200, data: { list: orders, total: total.count } });
});

export default router;
