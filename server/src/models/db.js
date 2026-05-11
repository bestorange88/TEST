import Database from 'better-sqlite3';
import bcryptjs from 'bcryptjs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const db = new Database(join(__dirname, '../../data.db'));
db.pragma('journal_mode = WAL');

export function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      real_name TEXT DEFAULT '',
      id_card TEXT DEFAULT '',
      phone TEXT DEFAULT '',
      credit_score INTEGER DEFAULT 100,
      verified INTEGER DEFAULT 0,
      balance REAL DEFAULT 0,
      frozen_balance REAL DEFAULT 0,
      total_profit REAL DEFAULT 0,
      today_profit REAL DEFAULT 0,
      role TEXT DEFAULT 'user',
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      symbol TEXT NOT NULL,
      price REAL DEFAULT 0,
      change_amount REAL DEFAULT 0,
      change_percent REAL DEFAULT 0,
      high_24h REAL DEFAULT 0,
      low_24h REAL DEFAULT 0,
      volume_24h TEXT DEFAULT '0',
      amount_24h TEXT DEFAULT '0',
      profit_rate REAL DEFAULT 85,
      status INTEGER DEFAULT 1,
      sort_order INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      product_name TEXT NOT NULL,
      direction TEXT NOT NULL,
      amount REAL NOT NULL,
      open_price REAL NOT NULL,
      close_price REAL DEFAULT 0,
      profit REAL DEFAULT 0,
      profit_rate REAL DEFAULT 0,
      duration INTEGER NOT NULL,
      status TEXT DEFAULT 'open',
      created_at TEXT DEFAULT (datetime('now')),
      closed_at TEXT DEFAULT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS deposits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      amount REAL NOT NULL,
      method TEXT DEFAULT 'bank',
      status TEXT DEFAULT 'pending',
      remark TEXT DEFAULT '',
      created_at TEXT DEFAULT (datetime('now')),
      reviewed_at TEXT DEFAULT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS withdrawals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      amount REAL NOT NULL,
      bank_card_id INTEGER,
      status TEXT DEFAULT 'pending',
      remark TEXT DEFAULT '',
      created_at TEXT DEFAULT (datetime('now')),
      reviewed_at TEXT DEFAULT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS bank_cards (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      bank_name TEXT NOT NULL,
      card_number TEXT NOT NULL,
      holder_name TEXT NOT NULL,
      branch TEXT DEFAULT '',
      is_default INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS notices (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      type TEXT DEFAULT 'system',
      status INTEGER DEFAULT 1,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
  `);

  const admin = db.prepare('SELECT id FROM users WHERE username = ?').get('admin');
  if (!admin) {
    const hashed = bcryptjs.hashSync('admin123', 10);
    db.prepare(`INSERT INTO users (username, password, real_name, role, balance, verified, credit_score)
      VALUES (?, ?, ?, ?, ?, ?, ?)`).run('admin', hashed, '管理员', 'admin', 0, 1, 100);
  }

  const productCount = db.prepare('SELECT COUNT(*) as count FROM products').get();
  if (productCount.count === 0) {
    const products = [
      { name: '25国债01', symbol: 'GZ01', price: 2337.55, high: 2340, low: 2335 },
      { name: '25国债02', symbol: 'GZ02', price: 450.079, high: 451, low: 449 },
      { name: '25国债03', symbol: 'GZ03', price: 58.52, high: 59, low: 58 },
      { name: '25国债04', symbol: 'GZ04', price: 1.473, high: 1.48, low: 1.46 },
      { name: '25国债05', symbol: 'GZ05', price: 2.042, high: 2.05, low: 2.03 },
      { name: '25国债06', symbol: 'GZ06', price: 1.360, high: 1.37, low: 1.35 },
      { name: '25国债07', symbol: 'GZ07', price: 3.869, high: 3.88, low: 3.86 },
      { name: '25国债08', symbol: 'GZ08', price: 9.777, high: 9.8, low: 9.75 },
      { name: '25国债09', symbol: 'GZ09', price: 0.28, high: 0.29, low: 0.27 },
      { name: '25国债10', symbol: 'GZ10', price: 81669.3, high: 81700, low: 81600 },
      { name: '25国债11', symbol: 'GZ11', price: 0.111, high: 0.115, low: 0.108 },
      { name: '25国债12', symbol: 'GZ12', price: 0.077, high: 0.08, low: 0.075 },
    ];
    const stmt = db.prepare(`INSERT INTO products (name, symbol, price, high_24h, low_24h, volume_24h, amount_24h, profit_rate)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
    for (const p of products) {
      stmt.run(p.name, p.symbol, p.price, p.high, p.low, '11M', '4K', 85);
    }
  }

  const noticeCount = db.prepare('SELECT COUNT(*) as count FROM notices').get();
  if (noticeCount.count === 0) {
    db.prepare(`INSERT INTO notices (title, content) VALUES (?, ?)`)
      .run('通知', '欢迎使用中央结算公司交易平台，请遵守相关规定进行交易。');
  }
}

export default db;
