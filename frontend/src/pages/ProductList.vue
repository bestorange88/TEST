<template>
  <div class="page">
    <div class="search-bar">
      <input v-model="keyword" placeholder="请输入产品名称" @input="search" />
      <span class="search-icon">🔍</span>
    </div>
    <div class="tabs">
      <div class="tab active">产品</div>
    </div>
    <div class="product-list">
      <div
        v-for="p in products"
        :key="p.id"
        class="product-row"
        @click="router.push('/product/' + p.id)"
      >
        <div class="row-left">
          <div class="row-name">{{ p.name }}</div>
          <div class="row-vol">24H量 {{ p.volume_24h }}</div>
        </div>
        <div class="row-price">{{ p.current_price }}</div>
        <div class="row-pct" :class="p.change_percent >= 0 ? 'pct-up' : 'pct-down'">
          {{ p.change_percent >= 0 ? '' : '' }}{{ p.change_percent }}%
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api/request.js';

const router = useRouter();
const products = ref([]);
const keyword = ref('');

async function loadProducts() {
  const res = await api.get('/product/list', { params: { keyword: keyword.value } });
  if (res.code === 200) products.value = res.data;
}

function search() {
  loadProducts();
}

onMounted(loadProducts);

const timer = setInterval(loadProducts, 5000);
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.search-bar input {
  flex: 1;
  height: 36px;
  background: #f5f5f5;
  border-radius: 18px;
  padding: 0 12px;
  border: none;
  font-size: 14px;
}

.search-icon {
  margin-left: 8px;
  font-size: 18px;
  cursor: pointer;
}

.tabs {
  display: flex;
  padding: 0 12px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.tab {
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  position: relative;
}

.tab.active {
  color: var(--primary);
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  background: var(--primary);
  border-radius: 2px;
}

.product-list {
  padding: 0;
}

.product-row {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  background: #fff;
  border-bottom: 1px solid #f8f8f8;
  cursor: pointer;
}

.row-left { flex: 1; }
.row-name { font-size: 15px; font-weight: 600; }
.row-vol { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
.row-price { font-size: 16px; font-weight: 600; margin-right: 12px; }

.row-pct {
  min-width: 65px;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 13px;
  text-align: center;
  color: #fff;
}

.pct-up { background: var(--green); }
.pct-down { background: var(--red); }
</style>
