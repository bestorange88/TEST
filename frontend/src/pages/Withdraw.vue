<template>
  <div class="page">
    <div class="nav-bar">
      <div class="back" @click="router.back()">←</div>
      <div class="title">资金结算</div>
    </div>
    <div class="withdraw-form">
      <div class="balance-info">可用余额：{{ userStore.user?.balance?.toFixed(2) || '0.00' }} CNY</div>
      <div class="form-item">
        <label>结算金额(CNY)</label>
        <input v-model.number="amount" type="number" placeholder="请输入结算金额" />
      </div>
      <div class="form-item">
        <label>提现至银行卡</label>
        <select v-model="bankCardId" class="select-card">
          <option value="">请选择银行卡</option>
          <option v-for="c in cards" :key="c.id" :value="c.id">{{ c.bank_name }} **** {{ c.card_number.slice(-4) }}</option>
        </select>
      </div>
      <div class="add-card" @click="router.push('/bank-card/add')">+ 添加新银行卡</div>
      <button class="btn" @click="submit" :disabled="!amount || !bankCardId">提交结算</button>
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
const amount = ref(null);
const bankCardId = ref('');
const cards = ref([]);

onMounted(async () => {
  const res = await api.get('/user/bank-cards');
  if (res.code === 200) cards.value = res.data;
});

async function submit() {
  if (!amount.value || !bankCardId.value) return;
  const res = await api.post('/finance/withdraw', { amount: amount.value, bank_card_id: bankCardId.value });
  if (res.code === 200) {
    alert('提现申请已提交，等待审核');
    userStore.fetchUserInfo();
    router.back();
  } else {
    alert(res.msg);
  }
}
</script>

<style scoped>
.withdraw-form { padding: 20px; }
.balance-info { font-size: 14px; color: var(--text-secondary); margin-bottom: 16px; padding: 12px; background: #f5f5f5; border-radius: 8px; }
.select-card { width: 100%; height: 44px; padding: 0 12px; background: #f9fafb; border: 1px solid var(--border); border-radius: 8px; font-size: 15px; }
.add-card { text-align: center; color: var(--primary); font-size: 14px; margin: 12px 0 20px; cursor: pointer; }
</style>
