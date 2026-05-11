<template>
  <div class="page">
    <div class="nav-bar">
      <div class="back" @click="router.back()">←</div>
      <div class="title">充值</div>
    </div>
    <div class="deposit-form">
      <div class="form-item">
        <label>充值金额(CNY)</label>
        <input v-model.number="amount" type="number" placeholder="请输入充值金额" />
      </div>
      <div class="quick-amounts">
        <span v-for="a in [100, 500, 1000, 5000, 10000, 50000]" :key="a" @click="amount = a" :class="{ active: amount === a }">
          {{ a }}
        </span>
      </div>
      <div class="form-item">
        <label>充值方式</label>
        <div class="method-options">
          <div class="method" :class="{ active: method === 'bank' }" @click="method = 'bank'">🏦 银行转账</div>
          <div class="method" :class="{ active: method === 'usdt' }" @click="method = 'usdt'">💎 USDT</div>
        </div>
      </div>
      <button class="btn" @click="submit" :disabled="!amount">提交充值</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api/request.js';

const router = useRouter();
const amount = ref(null);
const method = ref('bank');

async function submit() {
  if (!amount.value) return;
  const res = await api.post('/finance/deposit', { amount: amount.value, method: method.value });
  if (res.code === 200) {
    alert('充值申请已提交，等待审核');
    router.back();
  } else {
    alert(res.msg);
  }
}
</script>

<style scoped>
.deposit-form { padding: 20px; }
.quick-amounts { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.quick-amounts span {
  padding: 8px 16px; border: 1px solid var(--border); border-radius: 6px;
  font-size: 14px; cursor: pointer;
}
.quick-amounts span.active { border-color: var(--primary); color: var(--primary); background: rgba(67,56,202,0.05); }
.method-options { display: flex; gap: 10px; }
.method {
  flex: 1; padding: 12px; text-align: center; border: 1px solid var(--border);
  border-radius: 8px; cursor: pointer; font-size: 14px;
}
.method.active { border-color: var(--primary); color: var(--primary); background: rgba(67,56,202,0.05); }
</style>
