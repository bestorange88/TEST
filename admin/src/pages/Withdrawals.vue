<template>
  <div>
    <el-card shadow="hover">
      <template #header><div style="display:flex;justify-content:space-between;align-items:center">
        <span>提现审核</span>
        <el-select v-model="statusFilter" clearable placeholder="状态" @change="load" style="width:120px">
          <el-option label="全部" value="" /><el-option label="待审核" value="pending" /><el-option label="已通过" value="approved" /><el-option label="已拒绝" value="rejected" />
        </el-select>
      </div></template>
      <el-table :data="list" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户" />
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="bank_name" label="银行" />
        <el-table-column prop="card_number" label="卡号">
          <template #default="{ row }">{{ row.card_number ? '**** ' + row.card_number.slice(-4) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="{ pending: 'warning', approved: 'success', rejected: 'danger' }[row.status]" size="small">
            {{ { pending: '待审核', approved: '已通过', rejected: '已拒绝' }[row.status] }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="review(row, 'approved')">通过</el-button>
              <el-button size="small" type="danger" @click="review(row, 'rejected')">拒绝</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination :current-page="page" :page-size="20" :total="total" @current-change="p => { page = p; load(); }" style="margin-top:16px" />
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import api from '../api/request.js';
const list = ref([]); const page = ref(1); const total = ref(0); const statusFilter = ref('');
async function load() {
  const res = await api.get('/admin/withdrawals', { params: { page: page.value, status: statusFilter.value } });
  if (res.code === 200) { list.value = res.data.list; total.value = res.data.total; }
}
async function review(row, status) {
  const res = await api.put('/admin/withdrawal/' + row.id, { status });
  if (res.code === 200) { ElMessage.success('处理成功'); load(); } else ElMessage.error(res.msg);
}
onMounted(load);
</script>
