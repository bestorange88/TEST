<template>
  <div>
    <el-card shadow="hover">
      <template #header><div style="display:flex;justify-content:space-between">
        <span>通知管理</span>
        <el-button type="primary" @click="openAdd">添加通知</el-button>
      </div></template>
      <el-table :data="notices" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="content" label="内容" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }"><el-tag :type="row.status ? 'success' : 'info'" size="small">{{ row.status ? '启用' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="editNotice(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteNotice(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑通知' : '添加通知'" width="500">
      <el-form :model="form" label-width="60px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" rows="4" /></el-form-item>
        <el-form-item v-if="isEdit" label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '../api/request.js';
const notices = ref([]); const dialogVisible = ref(false); const isEdit = ref(false); const editingId = ref(null);
const form = ref({ title: '', content: '', status: 1 });
async function load() { const res = await api.get('/admin/notices'); if (res.code === 200) notices.value = res.data; }
function openAdd() { isEdit.value = false; form.value = { title: '', content: '', status: 1 }; dialogVisible.value = true; }
function editNotice(row) { isEdit.value = true; editingId.value = row.id; form.value = { ...row }; dialogVisible.value = true; }
async function save() {
  let res;
  if (isEdit.value) res = await api.put('/admin/notice/' + editingId.value, form.value);
  else res = await api.post('/admin/notice', form.value);
  if (res.code === 200) { ElMessage.success(res.msg); dialogVisible.value = false; load(); } else ElMessage.error(res.msg);
}
async function deleteNotice(row) {
  await ElMessageBox.confirm('确定删除？', '提示');
  const res = await api.delete('/admin/notice/' + row.id);
  if (res.code === 200) { ElMessage.success('删除成功'); load(); }
}
onMounted(load);
</script>
