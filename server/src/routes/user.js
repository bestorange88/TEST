import { Router } from 'express';
import db from '../models/db.js';
import { authMiddleware } from '../middleware/auth.js';

const router = Router();

router.get('/info', authMiddleware, (req, res) => {
  const user = db.prepare('SELECT id, username, real_name, phone, credit_score, verified, balance, frozen_balance, total_profit, today_profit, role, created_at FROM users WHERE id = ?')
    .get(req.user.id);
  if (!user) return res.json({ code: 404, msg: '用户不存在' });
  res.json({ code: 200, data: user });
});

router.post('/verify', authMiddleware, (req, res) => {
  const { real_name, id_card, phone } = req.body;
  if (!real_name || !id_card) return res.json({ code: 400, msg: '请填写完整认证信息' });

  const user = db.prepare('SELECT verified FROM users WHERE id = ?').get(req.user.id);
  if (user.verified) return res.json({ code: 400, msg: '已完成实名认证' });

  db.prepare('UPDATE users SET real_name = ?, id_card = ?, phone = ?, verified = 1 WHERE id = ?')
    .run(real_name, id_card, phone || '', req.user.id);

  res.json({ code: 200, msg: '认证成功' });
});

router.get('/bank-cards', authMiddleware, (req, res) => {
  const cards = db.prepare('SELECT * FROM bank_cards WHERE user_id = ? ORDER BY is_default DESC, created_at DESC')
    .all(req.user.id);
  res.json({ code: 200, data: cards });
});

router.post('/bank-card', authMiddleware, (req, res) => {
  const { bank_name, card_number, holder_name, branch } = req.body;
  if (!bank_name || !card_number || !holder_name) {
    return res.json({ code: 400, msg: '请填写完整银行卡信息' });
  }

  const user = db.prepare('SELECT verified FROM users WHERE id = ?').get(req.user.id);
  if (!user.verified) return res.json({ code: 400, msg: '请先完成实名认证' });

  const existingCount = db.prepare('SELECT COUNT(*) as count FROM bank_cards WHERE user_id = ?').get(req.user.id);
  const isDefault = existingCount.count === 0 ? 1 : 0;

  db.prepare('INSERT INTO bank_cards (user_id, bank_name, card_number, holder_name, branch, is_default) VALUES (?, ?, ?, ?, ?, ?)')
    .run(req.user.id, bank_name, card_number, holder_name, branch || '', isDefault);

  res.json({ code: 200, msg: '添加成功' });
});

router.delete('/bank-card/:id', authMiddleware, (req, res) => {
  db.prepare('DELETE FROM bank_cards WHERE id = ? AND user_id = ?').run(req.params.id, req.user.id);
  res.json({ code: 200, msg: '删除成功' });
});

export default router;
