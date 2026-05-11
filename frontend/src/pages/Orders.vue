<template>
  <div class="page">
    <div class="nav-bar">
      <div class="back" @click="router.back()">←</div>
      <div class="title">订单记录</div>
    </div>
    <div class="tabs">
      <span :class="{ active: tab === 'open' }" @click="tab = 'open'; load()">持仓列表</span>
      <span :class="{ active: tab === 'closed' }" @click="tab = 'closed'; load()">平仓记录</span>
    </div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="orders.length === 0" class="empty-state">暂无订单</div>
    <div v-else class="order-list">
      <div v-for="o in orders" :key="o.id" class="order-card">
        <div class="order-header">
          <span class="order-name">{{ o.product_name }}</span>
          <span class="order-dir" :class="'dir-' + o.direction">
            {{ { up: '买涨', down: '买跌', both: '双向' }[o.direction] }}
          </span>
          <span class="order-status" :class="o.status">{{ o.status === 'open' ? '持仓中' : '已平仓' }}</span>
        </div>
        <div class="order-body">
          <div><span>金额</span><span>{{ o.amount }} CNY</span></div>
          <div><span>开仓价</span><span>{{ o.open_price }}</span></div>
          <div v-if="o.status === 'closed'"><span>平仓价</span><span>{{ o.close_price }}</span></div>
          <div v-if="o.status === 'closed'">
            <span>盈亏</span>
            <span :class="o.profit >= 0 ? 'price-up' : 'price-down'">{{ o.profit >= 0 ? '+' : '' }}{{ o.profit }}</span>
          </div>
          <div><span>时间</span><span>{{ o.created_at }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api/request.js';

const router = useRouter();
const tab = ref('open');
const orders = ref([]);
const loading = ref(false);

async function load() {
  loading.value = true;
  const endpoint = tab.value === 'open' ? '/order/positions' : '/order/history';
  const res = await api.get(endpoint);
  if (res.code === 200) {
    orders.value = tab.value === 'open' ? res.data : res.data.list;
  }
  loading.value = false;
}

onMounted(load);
</script>

<style scoped>
.tabs { display: flex; background: #fff; border-bottom: 1px solid #f0f0f0; }
.tabs span {
  flex: 1; text-align: center; padding: 12px; font-size: 14px;
  color: var(--text-secondary); cursor: pointer; position: relative;
}
.tabs span.active { color: var(--primary); font-weight: 600; }
.tabs span.active::after {
  content: ''; position: absolute; bottom: 0; left: 50%;
  transform: translateX(-50%); width: 24px; height: 3px;
  background: var(--primary); border-radius: 2px;
}

.order-list { padding: 12px; }
.order-card { background: #fff; border-radius: 10px; margin-bottom: 10px; padding: 14px; }
.order-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.order-name { font-size: 15px; font-weight: 600; }
.order-dir { font-size: 12px; padding: 2px 6px; border-radius: 4px; color: #fff; }
.dir-up { background: var(--green); }
.dir-down { background: var(--red); }
.dir-both { background: var(--warning); }
.order-status { margin-left: auto; font-size: 12px; }
.order-status.open { color: var(--warning); }
.order-status.closed { color: var(--text-secondary); }

.order-body div { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
.order-body div span:first-child { color: var(--text-secondary); }
</style>
