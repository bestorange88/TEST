<template>
  <div class="page">
    <div class="nav-bar"><div class="back" @click="router.back()">←</div><div class="title">资金结算明细</div></div>
    <div v-if="list.length === 0" class="empty-state">暂无结算记录</div>
    <div v-else class="record-list">
      <div v-for="r in list" :key="r.id" class="record-item">
        <div class="record-left">
          <div class="record-amount">-{{ r.amount }} CNY</div>
          <div class="record-time">{{ r.created_at }}</div>
          <div v-if="r.bank_name" class="record-bank">{{ r.bank_name }} **** {{ r.card_number?.slice(-4) }}</div>
        </div>
        <div class="record-status" :class="r.status">
          {{ { pending: '审核中', approved: '已通过', rejected: '已拒绝' }[r.status] }}
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
const list = ref([]);
onMounted(async () => {
  const res = await api.get('/finance/withdraw/list');
  if (res.code === 200) list.value = res.data.list;
});
</script>
<style scoped>
.record-list { padding: 0; }
.record-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; background: #fff; border-bottom: 1px solid #f5f5f5; }
.record-amount { font-size: 15px; font-weight: 600; color: var(--red); }
.record-time { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.record-bank { font-size: 12px; color: var(--text-secondary); }
.record-status { font-size: 13px; }
.record-status.pending { color: var(--warning); }
.record-status.approved { color: var(--green); }
.record-status.rejected { color: var(--red); }
</style>
