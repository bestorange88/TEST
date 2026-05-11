import { Router } from 'express';
import db from '../models/db.js';

const router = Router();

router.get('/list', (req, res) => {
  const { keyword } = req.query;
  let products;
  if (keyword) {
    products = db.prepare('SELECT * FROM products WHERE status = 1 AND name LIKE ? ORDER BY sort_order ASC, id ASC')
      .all(`%${keyword}%`);
  } else {
    products = db.prepare('SELECT * FROM products WHERE status = 1 ORDER BY sort_order ASC, id ASC').all();
  }

  // Simulate small price fluctuations
  products = products.map(p => {
    const fluctuation = (Math.random() - 0.5) * 0.002;
    const newPrice = p.price * (1 + fluctuation);
    const change = newPrice - p.price;
    const changePercent = fluctuation * 100;
    return {
      ...p,
      current_price: Number(newPrice.toFixed(5)),
      change_amount: Number(change.toFixed(3)),
      change_percent: Number(changePercent.toFixed(2)),
    };
  });

  res.json({ code: 200, data: products });
});

router.get('/detail/:id', (req, res) => {
  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id);
  if (!product) return res.json({ code: 404, msg: '产品不存在' });

  const fluctuation = (Math.random() - 0.5) * 0.002;
  const currentPrice = product.price * (1 + fluctuation);

  res.json({
    code: 200,
    data: {
      ...product,
      current_price: Number(currentPrice.toFixed(5)),
      change_amount: Number((currentPrice - product.price).toFixed(3)),
      change_percent: Number((fluctuation * 100).toFixed(2)),
    }
  });
});

router.get('/kline/:id', (req, res) => {
  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id);
  if (!product) return res.json({ code: 404, msg: '产品不存在' });

  const { period = '5m' } = req.query;
  const now = Date.now();
  const klineData = [];
  let count = 60;
  let interval = 5 * 60 * 1000;

  const periodMap = { '1m': 60000, '5m': 300000, '30m': 1800000, '1h': 3600000, '4h': 14400000, '1d': 86400000, '1w': 604800000 };
  interval = periodMap[period] || 300000;

  let price = product.price;
  for (let i = count; i >= 0; i--) {
    const time = now - i * interval;
    const open = price;
    const change = (Math.random() - 0.5) * price * 0.005;
    price = price + change;
    const high = Math.max(open, price) + Math.abs(change) * Math.random();
    const low = Math.min(open, price) - Math.abs(change) * Math.random();
    const volume = Math.floor(Math.random() * 1000000);

    klineData.push({
      time: Math.floor(time / 1000),
      open: Number(open.toFixed(5)),
      high: Number(high.toFixed(5)),
      low: Number(low.toFixed(5)),
      close: Number(price.toFixed(5)),
      volume,
    });
  }

  res.json({ code: 200, data: klineData });
});

export default router;
