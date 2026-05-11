import { Router } from 'express';
import db from '../models/db.js';
import { authMiddleware } from '../middleware/auth.js';

const router = Router();

router.post('/deposit', authMiddleware, (req, res) => {
  const { amount, method } = req.body;
  if (!amount || amount <= 0) return res.json({ code: 400, msg: '请输入有效金额' });

  db.prepare('INSERT INTO deposits (user_id, amount, method) VALUES (?, ?, ?)')
    .run(req.user.id, amount, method || 'bank');

  res.json({ code: 200, msg: '充值申请已提交，等待审核' });
});

router.get('/deposit/list', authMiddleware, (req, res) => {
  const { page = 1, size = 20 } = req.query;
  const offset = (page - 1) * size;
  const list = db.prepare('SELECT * FROM deposits WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?')
    .all(req.user.id, Number(size), offset);
  const total = db.prepare('SELECT COUNT(*) as count FROM deposits WHERE user_id = ?').get(req.user.id);
  res.json({ code: 200, data: { list, total: total.count } });
});

router.post('/withdraw', authMiddleware, (req, res) => {
  const { amount, bank_card_id } = req.body;
  if (!amount || amount <= 0) return res.json({ code: 400, msg: '请输入有效金额' });

  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.user.id);
  if (!user.verified) return res.json({ code: 400, msg: '请先完成实名认证' });
  if (user.balance < amount) return res.json({ code: 400, msg: '余额不足' });

  if (bank_card_id) {
    const card = db.prepare('SELECT id FROM bank_cards WHERE id = ? AND user_id = ?').get(bank_card_id, req.user.id);
    if (!card) return res.json({ code: 400, msg: '银行卡不存在' });
  }

  db.prepare('UPDATE users SET balance = balance - ?, frozen_balance = frozen_balance + ? WHERE id = ?')
    .run(amount, amount, req.user.id);

  db.prepare('INSERT INTO withdrawals (user_id, amount, bank_card_id) VALUES (?, ?, ?)')
    .run(req.user.id, amount, bank_card_id || null);

  res.json({ code: 200, msg: '提现申请已提交，等待审核' });
});

router.get('/withdraw/list', authMiddleware, (req, res) => {
  const { page = 1, size = 20 } = req.query;
  const offset = (page - 1) * size;
  const list = db.prepare(`SELECT w.*, b.bank_name, b.card_number FROM withdrawals w
    LEFT JOIN bank_cards b ON w.bank_card_id = b.id
    WHERE w.user_id = ? ORDER BY w.created_at DESC LIMIT ? OFFSET ?`)
    .all(req.user.id, Number(size), offset);
  const total = db.prepare('SELECT COUNT(*) as count FROM withdrawals WHERE user_id = ?').get(req.user.id);
  res.json({ code: 200, data: { list, total: total.count } });
});

export default router;
