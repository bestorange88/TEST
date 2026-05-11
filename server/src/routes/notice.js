import { Router } from 'express';
import db from '../models/db.js';

const router = Router();

router.get('/list', (req, res) => {
  const notices = db.prepare('SELECT * FROM notices WHERE status = 1 ORDER BY created_at DESC').all();
  res.json({ code: 200, data: notices });
});

router.get('/:id', (req, res) => {
  const notice = db.prepare('SELECT * FROM notices WHERE id = ?').get(req.params.id);
  if (!notice) return res.json({ code: 404, msg: '通知不存在' });
  res.json({ code: 200, data: notice });
});

export default router;
