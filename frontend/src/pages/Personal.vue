<template>
  <div class="page personal-page">
    <div class="user-header" v-if="userStore.isLoggedIn">
      <div class="user-info">
        <div class="username">{{ userStore.user?.username }}</div>
        <div class="user-meta">
          <span class="real-name">{{ userStore.user?.real_name || '未认证' }}</span>
          <span class="credit">信用分:{{ userStore.user?.credit_score || 0 }}</span>
          <span class="verify-badge" :class="userStore.user?.verified ? 'verified' : ''">
            {{ userStore.user?.verified ? '已认证' : '未认证' }}
          </span>
        </div>
      </div>
      <div class="country-badge">CN</div>
    </div>

    <div class="asset-card" v-if="userStore.isLoggedIn">
      <div class="asset-top">
        <div class="asset-main">
          <div class="asset-label">总资产(CNY)</div>
          <div class="asset-value">￥{{ totalAssets.toFixed(2) }}</div>
        </div>
        <div class="asset-pnl">
          <div class="pnl-item">
            <span class="pnl-label">账户盈亏</span>
            <span :class="userStore.user?.total_profit >= 0 ? 'price-up' : 'price-down'">
              {{ userStore.user?.total_profit?.toFixed(2) || '0.00' }}
            </span>
          </div>
          <div class="pnl-item">
            <span class="pnl-label">今日盈亏</span>
            <span :class="userStore.user?.today_profit >= 0 ? 'price-up' : 'price-down'">
              {{ userStore.user?.today_profit?.toFixed(2) || '0.00' }}
            </span>
          </div>
        </div>
      </div>
      <div class="asset-bottom">
        <div class="balance-info">
          <div class="balance-label">可用余额(CNY)</div>
          <div class="balance-value">￥{{ userStore.user?.balance?.toFixed(2) || '0.00' }}</div>
        </div>
        <div class="action-btns">
          <div class="action-btn" @click="router.push('/deposit')">
            <span class="btn-icon">💰</span>
            <span>充值</span>
          </div>
          <div class="action-btn" @click="router.push('/withdraw')">
            <span class="btn-icon">💸</span>
            <span>资金结算</span>
          </div>
        </div>
      </div>
    </div>

    <div class="cell-list">
      <div class="cell-item" @click="goTo('/verify')">
        <div class="cell-icon" style="background:#fde8e8">🪪</div>
        <div class="cell-title">实名认证</div>
        <div class="cell-arrow">›</div>
      </div>
      <div class="cell-item" @click="goTo('/orders')">
        <div class="cell-icon" style="background:#e8f0fd">📋</div>
        <div class="cell-title">订单记录</div>
        <div class="cell-arrow">›</div>
      </div>
      <div class="cell-item" @click="goTo('/deposit-list')">
        <div class="cell-icon" style="background:#e8f4e8">💳</div>
        <div class="cell-title">充值明细</div>
        <div class="cell-arrow">›</div>
      </div>
      <div class="cell-item" @click="goTo('/withdraw-list')">
        <div class="cell-icon" style="background:#e8f4e8">📊</div>
        <div class="cell-title">资金结算明细</div>
        <div class="cell-arrow">›</div>
      </div>
      <div class="cell-item" @click="goTo('/bank-cards')">
        <div class="cell-icon" style="background:#f0e8fd">🏦</div>
        <div class="cell-title">绑定银行卡</div>
        <div class="cell-arrow">›</div>
      </div>
      <div class="cell-item" @click="goTo('/settings')">
        <div class="cell-icon" style="background:#f5f5f5">⚙️</div>
        <div class="cell-title">设置</div>
        <div class="cell-arrow">›</div>
      </div>
      <div class="cell-item" @click="handleLogout">
        <div class="cell-icon" style="background:#fde8e8">🚪</div>
        <div class="cell-title">退出登录</div>
        <div class="cell-arrow">›</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user.js';

const router = useRouter();
const userStore = useUserStore();

const totalAssets = computed(() => {
  const u = userStore.user;
  return (u?.balance || 0) + (u?.frozen_balance || 0);
});

function goTo(path) {
  if (!userStore.isLoggedIn) {
    router.push('/login');
    return;
  }
  router.push(path);
}

function handleLogout() {
  userStore.logout();
  router.push('/login');
}

onMounted(() => {
  if (userStore.isLoggedIn) userStore.fetchUserInfo();
});
</script>

<style scoped>
.user-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px 12px;
  background: #fff;
}

.username { font-size: 18px; font-weight: 700; }

.user-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
}

.real-name { color: var(--text-secondary); }
.credit { color: var(--green); }
.verify-badge {
  padding: 1px 6px;
  border-radius: 4px;
  background: #eee;
  color: #999;
}
.verify-badge.verified { background: #e8f4e8; color: var(--green); }

.country-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--green);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.asset-card {
  margin: 12px;
  background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
  border-radius: 12px;
  padding: 16px;
}

.asset-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.asset-label { font-size: 12px; color: var(--text-secondary); }
.asset-value { font-size: 22px; font-weight: 700; margin-top: 4px; }

.pnl-item { text-align: right; margin-bottom: 4px; }
.pnl-label { font-size: 12px; color: var(--text-secondary); margin-right: 4px; }

.asset-bottom {
  display: flex;
  align-items: center;
  gap: 12px;
}

.balance-info {
  background: #fff;
  border-radius: 8px;
  padding: 8px 12px;
}

.balance-label { font-size: 11px; color: var(--text-secondary); }
.balance-value { font-size: 15px; font-weight: 600; }

.action-btns { display: flex; gap: 8px; }

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  gap: 2px;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(67, 56, 202, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.action-btn span:last-child { font-size: 11px; color: var(--text-secondary); }
</style>
