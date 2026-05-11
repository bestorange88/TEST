<template>
  <div>
    <h3 style="margin-bottom:20px">数据概览</h3>
    <el-row :gutter="20">
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="用户数" :value="stats.user_count" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="总订单" :value="stats.order_count" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="待审充值" :value="stats.pending_deposits" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="待审提现" :value="stats.pending_withdrawals" /></el-card></el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12"><el-card shadow="hover"><el-statistic title="总充值金额" :value="stats.total_deposits" prefix="¥" /></el-card></el-col>
      <el-col :span="12"><el-card shadow="hover"><el-statistic title="总提现金额" :value="stats.total_withdrawals" prefix="¥" /></el-card></el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/request.js';

const stats = ref({});
onMounted(async () => {
  const res = await api.get('/admin/stats');
  if (res.code === 200) stats.value = res.data;
});
</script>
