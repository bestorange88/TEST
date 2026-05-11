<template>
  <div>
    <el-card shadow="hover">
      <template #header><div style="display:flex;justify-content:space-between;align-items:center">
        <span>订单管理</span>
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadOrders" style="width:120px">
          <el-option label="全部" value="" />
          <el-option label="持仓中" value="open" />
          <el-option label="已平仓" value="closed" />
        </el-select>
      </div></template>
      <el-table :data="orders" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户" />
        <el-table-column prop="product_name" label="产品" />
        <el-table-column prop="direction" label="方向" width="70">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'up' ? 'success' : row.direction === 'down' ? 'danger' : 'warning'" size="small">
              {{ { up: '买涨', down: '买跌', both: '双向' }[row.direction] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="open_price" label="开仓价" />
        <el-table-column prop="profit" label="盈亏">
          <template #default="{ row }"><span :style="{ color: row.profit >= 0 ? '#67c23a' : '#f56c6c' }">{{ row.profit }}</span></template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 'open' ? 'warning' : 'info'" size="small">{{ row.status === 'open' ? '持仓中' : '已平仓' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="row.status === 'open'" size="small" type="warning" @click="closeOrder(row)">强制平仓</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination :current-page="page" :page-size="20" :total="total" @current-change="p => { page = p; loadOrders(); }" style="margin-top:16px" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '../api/request.js';

const orders = ref([]);
const page = ref(1);
const total = ref(0);
const statusFilter = ref('');

async function loadOrders() {
  const res = await api.get('/admin/orders', { params: { page: page.value, status: statusFilter.value } });
  if (res.code === 200) { orders.value = res.data.list; total.value = res.data.total; }
}

async function closeOrder(row) {
  const { value } = await ElMessageBox.prompt('请输入盈亏金额(正数盈利，负数亏损)', '强制平仓', { inputValue: '0' });
  const res = await api.put('/admin/order/' + row.id, { status: 'closed', profit: Number(value) });
  if (res.code === 200) { ElMessage.success('平仓成功'); loadOrders(); }
}

onMounted(loadOrders);
</script>
