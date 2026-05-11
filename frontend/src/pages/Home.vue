<template>
  <div class="page home-page">
    <div class="home-header">
      <div class="header-left">
        <span class="logo-icon">🏛</span>
        <span class="logo-text">中央结算公司</span>
      </div>
      <div class="lang-toggle">🌐 简体中文</div>
    </div>

    <div class="banner-area">
      <div class="mascot">
        <span class="mascot-char">🧝</span>
        <span class="mascot-bubble">点击我~</span>
      </div>
    </div>

    <div class="quick-actions">
      <div class="action-item" @click="goTo('/product')">
        <div class="action-icon" style="background:#e8f4e8">📊</div>
        <span>产品交易</span>
      </div>
      <div class="action-item" @click="goTo('/orders')">
        <div class="action-icon" style="background:#fde8e8">📋</div>
        <span>持仓</span>
      </div>
      <div class="action-item" @click="goTo('/about')">
        <div class="action-icon" style="background:#e8f0fd">🏢</div>
        <span>关于我们</span>
      </div>
      <div class="action-item" @click="goTo('/about')">
        <div class="action-icon" style="background:#fdf0e8">❓</div>
        <span>帮助中心</span>
      </div>
      <div class="action-item service-item">
        <div class="service-info">
          <span class="service-title">在线客服</span>
          <span class="service-desc">优质竭诚为您服务</span>
        </div>
        <div class="service-icon">💬</div>
      </div>
    </div>

    <div v-if="notices.length" class="notice-bar" @click="goTo('/notice/' + notices[0].id)">
      <div class="notice-icon">🔔</div>
      <div class="notice-content">
        <span class="notice-title">{{ notices[0].title }}</span>
        <span class="notice-time">{{ notices[0].created_at }}</span>
      </div>
    </div>

    <div class="section-title">产品推荐</div>
    <div class="product-scroll">
      <div
        v-for="p in products"
        :key="p.id"
        class="product-card"
        @click="goTo('/product/' + p.id)"
      >
        <div class="p-name">{{ p.name }}</div>
        <div class="p-price">{{ p.current_price }}</div>
        <div class="p-change" :class="p.change_percent >= 0 ? 'price-up' : 'price-down'">
          <span>{{ p.change_amount >= 0 ? '+' : '' }}{{ p.change_amount }}</span>
          <span class="p-pct">{{ p.change_percent >= 0 ? '+' : '' }}{{ p.change_percent }}%</span>
        </div>
      </div>
    </div>

    <div class="section-title" style="margin-top:16px">产品列表</div>
    <div class="product-list">
      <div
        v-for="p in products"
        :key="'list-' + p.id"
        class="product-row"
        @click="goTo('/product/' + p.id)"
      >
        <div class="row-left">
          <div class="row-name">{{ p.name }}</div>
          <div class="row-vol">24H量 {{ p.volume_24h }}</div>
        </div>
        <div class="row-price">{{ p.current_price }}</div>
        <div class="row-pct" :class="p.change_percent >= 0 ? 'pct-up' : 'pct-down'">
          {{ p.change_percent >= 0 ? '+' : '' }}{{ p.change_percent }}%
        </div>
      </div>
    </div>

    <!-- Login dialog -->
    <div v-if="showLoginDialog" class="dialog-mask" @click="showLoginDialog = false">
      <div class="dialog-box" @click.stop>
        <div class="dialog-msg">请先登录</div>
        <div class="dialog-btn" @click="router.push('/login')">好的</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user.js';
import api from '../api/request.js';

const router = useRouter();
const userStore = useUserStore();
const products = ref([]);
const notices = ref([]);
const showLoginDialog = ref(false);

function goTo(path) {
  if (!userStore.isLoggedIn && path !== '/about') {
    showLoginDialog.value = true;
    return;
  }
  router.push(path);
}

async function loadData() {
  const [prodRes, noticeRes] = await Promise.all([
    api.get('/product/list'),
    api.get('/notice/list'),
  ]);
  if (prodRes.code === 200) products.value = prodRes.data;
  if (noticeRes.code === 200) notices.value = noticeRes.data;
}

onMounted(loadData);

// Auto refresh prices
let timer;
onMounted(() => {
  timer = setInterval(async () => {
    const res = await api.get('/product/list');
    if (res.code === 200) products.value = res.data;
  }, 5000);
});

import { onUnmounted } from 'vue';
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.logo-icon { font-size: 22px; }
.logo-text { font-size: 15px; font-weight: 700; color: #8b0000; }
.lang-toggle { font-size: 13px; color: var(--text-secondary); }

.banner-area {
  background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
  padding: 30px 0;
  text-align: center;
  border-radius: 0 0 16px 16px;
}

.mascot { position: relative; display: inline-block; }
.mascot-char { font-size: 60px; }
.mascot-bubble {
  position: absolute;
  top: -10px;
  right: -60px;
  background: #fff;
  border: 1px solid #e74c3c;
  border-radius: 12px;
  padding: 4px 10px;
  font-size: 12px;
  color: #e74c3c;
  white-space: nowrap;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  padding: 12px;
  gap: 8px;
  background: #fff;
  margin: 12px;
  border-radius: 12px;
}

.action-item {
  width: calc(25% - 6px);
  text-align: center;
  cursor: pointer;
  padding: 8px 0;
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 4px;
  font-size: 18px;
}

.action-item span {
  font-size: 12px;
  color: var(--text);
}

.service-item {
  width: calc(50% - 6px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 10px;
}

.service-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.service-title { font-size: 13px; font-weight: 600; }
.service-desc { font-size: 11px; color: var(--text-secondary); }
.service-icon { font-size: 28px; }

.notice-bar {
  display: flex;
  align-items: center;
  margin: 0 12px;
  padding: 12px;
  background: #fff;
  border-radius: 12px;
  cursor: pointer;
}

.notice-icon { font-size: 18px; margin-right: 10px; }
.notice-content { flex: 1; }
.notice-title { font-size: 14px; font-weight: 500; margin-right: 8px; }
.notice-time { font-size: 11px; color: var(--text-secondary); }

.section-title {
  padding: 12px 16px 8px;
  font-size: 15px;
  font-weight: 600;
}

.product-scroll {
  display: flex;
  overflow-x: auto;
  padding: 0 12px;
  gap: 10px;
  -webkit-overflow-scrolling: touch;
}

.product-scroll::-webkit-scrollbar { display: none; }

.product-card {
  min-width: 120px;
  background: #fff;
  border-radius: 10px;
  padding: 12px;
  cursor: pointer;
}

.p-name { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.p-price { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.p-change { font-size: 12px; }
.p-pct { margin-left: 4px; }

.product-list {
  margin: 0 12px 20px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.product-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.row-left { flex: 1; }
.row-name { font-size: 14px; font-weight: 600; }
.row-vol { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
.row-price { font-size: 15px; font-weight: 600; margin-right: 12px; }

.row-pct {
  min-width: 60px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  text-align: center;
  color: #fff;
}

.pct-up { background: var(--green); }
.pct-down { background: var(--red); }
</style>
