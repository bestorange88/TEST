<template>
  <div class="page product-detail" v-if="product">
    <div class="nav-bar">
      <div class="back" @click="router.back()">←</div>
      <div class="title">{{ product.name }}</div>
      <div class="nav-right" @click="router.push('/orders')">📋</div>
    </div>

    <div class="price-section">
      <div class="current-price" :class="product.change_percent >= 0 ? 'price-up' : 'price-down'">
        {{ product.current_price }}
      </div>
      <div class="price-change" :class="product.change_percent >= 0 ? 'price-up' : 'price-down'">
        {{ product.change_amount >= 0 ? '+' : '' }}{{ product.change_amount }}
        <span>{{ product.change_percent >= 0 ? '+' : '' }}{{ product.change_percent }}%</span>
      </div>
    </div>

    <div class="price-stats">
      <div class="stat-row">
        <div class="stat-item"><span class="stat-label">24H最高</span><span>{{ product.high_24h }}</span></div>
        <div class="stat-item"><span class="stat-label">24H量(MX)</span><span>{{ product.volume_24h }}</span></div>
      </div>
      <div class="stat-row">
        <div class="stat-item"><span class="stat-label">24H最低</span><span>{{ product.low_24h }}</span></div>
        <div class="stat-item"><span class="stat-label">24H额</span><span>{{ product.amount_24h }}</span></div>
      </div>
    </div>

    <div class="chart-tabs">
      <span
        v-for="p in periods"
        :key="p"
        :class="{ active: activePeriod === p }"
        @click="activePeriod = p; loadKline()"
      >{{ p }}</span>
    </div>

    <div class="chart-area">
      <canvas ref="chartCanvas" width="720" height="300"></canvas>
    </div>

    <div class="trade-buttons">
      <button class="trade-btn btn-buy" @click="openTrade('up')">买涨</button>
      <button class="trade-btn btn-sell" @click="openTrade('down')">买跌</button>
      <button class="trade-btn btn-both" @click="openTrade('both')">双向</button>
    </div>

    <!-- Trade Dialog -->
    <div v-if="showTradeDialog" class="modal-mask">
      <div class="modal-content">
        <div class="trade-header">
          <span class="trade-product">{{ product.name }}</span>
          <span class="trade-direction" :class="'dir-' + tradeForm.direction">
            {{ { up: '买涨', down: '买跌', both: '双向' }[tradeForm.direction] }}
          </span>
          <span class="trade-cancel" @click="showTradeDialog = false">取消</span>
        </div>
        <div class="trade-field">
          <label>金额</label>
          <div class="amount-input">
            <input v-model.number="tradeForm.amount" type="number" placeholder="请输入其他金额" />
            <span class="amount-unit">CNY</span>
          </div>
          <div class="balance-row">
            <span>余额：{{ userStore.user?.balance?.toFixed(2) || '0.00' }} CNY</span>
            <span class="all-in" @click="tradeForm.amount = userStore.user?.balance || 0">全部下单</span>
          </div>
        </div>
        <div class="trade-field">
          <label>时间</label>
          <div class="duration-options">
            <span
              v-for="d in [300, 600, 900]"
              :key="d"
              :class="{ active: tradeForm.duration === d }"
              @click="tradeForm.duration = d"
            >{{ d }}S</span>
          </div>
        </div>
        <div class="trade-summary">
          <div><span>当前价</span><span>{{ product.current_price }}</span></div>
          <div><span>金额</span><span>{{ tradeForm.amount || 0 }}</span></div>
          <div><span>收益率</span><span>{{ product.profit_rate || 85 }}%</span></div>
          <div><span>预估</span><span>{{ ((tradeForm.amount || 0) * (product.profit_rate || 85) / 100).toFixed(2) }}</span></div>
        </div>
        <button class="btn" @click="submitTrade" :disabled="!tradeForm.amount">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../store/user.js';
import api from '../api/request.js';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const product = ref(null);
const periods = ['Time', '1m', '5m', '30m', '1h', '4h', '1d', '1w'];
const activePeriod = ref('5m');
const chartCanvas = ref(null);
const showTradeDialog = ref(false);
const tradeForm = ref({ direction: 'up', amount: null, duration: 300 });

async function loadProduct() {
  const res = await api.get('/product/detail/' + route.params.id);
  if (res.code === 200) product.value = res.data;
}

async function loadKline() {
  const res = await api.get('/product/kline/' + route.params.id, { params: { period: activePeriod.value } });
  if (res.code === 200) drawChart(res.data);
}

function drawChart(data) {
  const canvas = chartCanvas.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  if (!data.length) return;

  const prices = data.map(d => [d.open, d.high, d.low, d.close]).flat();
  const minP = Math.min(...prices);
  const maxP = Math.max(...prices);
  const range = maxP - minP || 1;
  const barW = Math.max(2, (W - 40) / data.length - 1);

  data.forEach((d, i) => {
    const x = 20 + i * ((W - 40) / data.length);
    const oY = H - 20 - ((d.open - minP) / range) * (H - 40);
    const cY = H - 20 - ((d.close - minP) / range) * (H - 40);
    const hY = H - 20 - ((d.high - minP) / range) * (H - 40);
    const lY = H - 20 - ((d.low - minP) / range) * (H - 40);

    const isUp = d.close >= d.open;
    ctx.strokeStyle = isUp ? '#22c55e' : '#ef4444';
    ctx.fillStyle = isUp ? '#22c55e' : '#ef4444';

    ctx.beginPath();
    ctx.moveTo(x + barW / 2, hY);
    ctx.lineTo(x + barW / 2, lY);
    ctx.stroke();

    const top = Math.min(oY, cY);
    const h = Math.abs(oY - cY) || 1;
    ctx.fillRect(x, top, barW, h);
  });
}

function openTrade(direction) {
  if (!userStore.isLoggedIn) {
    router.push('/login');
    return;
  }
  tradeForm.value = { direction, amount: null, duration: 300 };
  showTradeDialog.value = true;
  userStore.fetchUserInfo();
}

async function submitTrade() {
  if (!tradeForm.value.amount || tradeForm.value.amount <= 0) return;
  const res = await api.post('/order/create', {
    product_id: Number(route.params.id),
    direction: tradeForm.value.direction,
    amount: tradeForm.value.amount,
    duration: tradeForm.value.duration,
  });
  if (res.code === 200) {
    showTradeDialog.value = false;
    alert('下单成功！');
    userStore.fetchUserInfo();
  } else {
    alert(res.msg);
  }
}

onMounted(() => {
  loadProduct();
  loadKline();
});

const timer = setInterval(loadProduct, 5000);
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
.nav-right {
  position: absolute;
  right: 12px;
  font-size: 20px;
  cursor: pointer;
}

.price-section {
  padding: 16px;
  background: #fff;
}

.current-price {
  font-size: 28px;
  font-weight: 700;
}

.price-change {
  font-size: 14px;
  margin-top: 4px;
}

.price-stats {
  padding: 8px 16px 16px;
  background: #fff;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.stat-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.stat-label {
  color: var(--text-secondary);
}

.chart-tabs {
  display: flex;
  padding: 8px 16px;
  background: #fff;
  gap: 12px;
  border-top: 1px solid #f0f0f0;
}

.chart-tabs span {
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 8px;
}

.chart-tabs span.active {
  color: var(--primary);
  border-bottom: 2px solid var(--primary);
}

.chart-area {
  background: #fff;
  padding: 0 8px 8px;
}

.chart-area canvas {
  width: 100%;
  height: 200px;
}

.trade-buttons {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 750px;
  display: flex;
  padding: 8px 12px;
  gap: 8px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  z-index: 100;
}

.trade-btn {
  flex: 1;
  height: 40px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  border: none;
}

.btn-buy { background: var(--green); }
.btn-sell { background: var(--red); }
.btn-both { background: linear-gradient(90deg, var(--green), var(--red)); }

.trade-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.trade-product { font-size: 16px; font-weight: 600; }

.trade-direction {
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
}

.dir-up { background: var(--green); }
.dir-down { background: var(--red); }
.dir-both { background: var(--warning); }

.trade-cancel {
  margin-left: auto;
  color: var(--text-secondary);
  cursor: pointer;
}

.trade-field {
  margin-bottom: 16px;
}

.trade-field label {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  display: block;
}

.amount-input {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 0 12px;
}

.amount-input input {
  flex: 1;
  height: 42px;
  background: transparent;
  font-size: 15px;
}

.amount-unit {
  color: var(--text-secondary);
  font-size: 14px;
}

.balance-row {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.all-in {
  color: var(--danger);
  cursor: pointer;
}

.duration-options {
  display: flex;
  gap: 10px;
}

.duration-options span {
  padding: 8px 20px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.duration-options span.active {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(67, 56, 202, 0.05);
}

.trade-summary {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 13px;
}

.trade-summary div {
  text-align: center;
}

.trade-summary span:first-child {
  display: block;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
</style>
