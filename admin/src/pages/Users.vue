<template>
  <div>
    <el-card shadow="hover">
      <template #header><div style="display:flex;justify-content:space-between;align-items:center">
        <span>用户管理</span>
        <el-input v-model="keyword" placeholder="搜索用户名/姓名" style="width:200px" @keyup.enter="loadUsers" clearable />
      </div></template>
      <el-table :data="users" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="balance" label="余额" />
        <el-table-column prop="credit_score" label="信用分" />
        <el-table-column prop="verified" label="认证" width="60">
          <template #default="{ row }"><el-tag :type="row.verified ? 'success' : 'info'" size="small">{{ row.verified ? '已认证' : '未认证' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="editUser(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="resetPwd(row)">重置密码</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination :current-page="page" :page-size="20" :total="total" @current-change="p => { page = p; loadUsers(); }" style="margin-top:16px" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="编辑用户" width="400">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="余额"><el-input-number v-model="editForm.balance" :precision="2" /></el-form-item>
        <el-form-item label="信用分"><el-input-number v-model="editForm.credit_score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="认证状态"><el-switch v-model="editForm.verified" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '../api/request.js';

const users = ref([]);
const keyword = ref('');
const page = ref(1);
const total = ref(0);
const dialogVisible = ref(false);
const editForm = ref({});
const editingId = ref(null);

async function loadUsers() {
  const res = await api.get('/admin/users', { params: { page: page.value, keyword: keyword.value } });
  if (res.code === 200) { users.value = res.data.list; total.value = res.data.total; }
}

function editUser(row) {
  editingId.value = row.id;
  editForm.value = { balance: row.balance, credit_score: row.credit_score, verified: row.verified };
  dialogVisible.value = true;
}

async function saveUser() {
  const res = await api.put('/admin/user/' + editingId.value, editForm.value);
  if (res.code === 200) { ElMessage.success('更新成功'); dialogVisible.value = false; loadUsers(); }
  else ElMessage.error(res.msg);
}

async function resetPwd(row) {
  await ElMessageBox.confirm('确定将该用户密码重置为123456？', '提示');
  const res = await api.post('/admin/user/' + row.id + '/reset-password');
  if (res.code === 200) ElMessage.success(res.msg);
}

onMounted(loadUsers);
</script>
