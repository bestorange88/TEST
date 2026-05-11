<template>
  <div class="page">
    <div class="nav-bar"><div class="back" @click="router.back()">←</div><div class="title">绑定银行卡</div></div>
    <div v-if="cards.length === 0" class="empty-state">暂无绑定银行卡</div>
    <div v-else class="card-list">
      <div v-for="c in cards" :key="c.id" class="bank-card-item">
        <div class="card-info">
          <div class="card-bank">🏦 {{ c.bank_name }}</div>
          <div class="card-number">**** **** **** {{ c.card_number.slice(-4) }}</div>
          <div class="card-holder">{{ c.holder_name }}</div>
        </div>
        <span class="card-delete" @click="deleteCard(c.id)">删除</span>
      </div>
    </div>
    <div class="add-area">
      <button class="btn" @click="router.push('/bank-card/add')">+ 添加银行卡</button>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api/request.js';
const router = useRouter();
const cards = ref([]);
onMounted(async () => {
  const res = await api.get('/user/bank-cards');
  if (res.code === 200) cards.value = res.data;
});
async function deleteCard(id) {
  if (!confirm('确定删除该银行卡？')) return;
  const res = await api.delete('/user/bank-card/' + id);
  if (res.code === 200) cards.value = cards.value.filter(c => c.id !== id);
}
</script>
<style scoped>
.card-list { padding: 12px; }
.bank-card-item { display: flex; align-items: center; background: linear-gradient(135deg, #4338ca, #6366f1); border-radius: 12px; padding: 16px; margin-bottom: 10px; color: #fff; }
.card-info { flex: 1; }
.card-bank { font-size: 14px; margin-bottom: 8px; }
.card-number { font-size: 18px; letter-spacing: 2px; margin-bottom: 4px; }
.card-holder { font-size: 13px; opacity: 0.8; }
.card-delete { font-size: 13px; opacity: 0.8; cursor: pointer; }
.add-area { padding: 12px 20px; }
</style>
