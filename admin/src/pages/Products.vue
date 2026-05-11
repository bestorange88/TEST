<template>
  <div>
    <el-card shadow="hover">
      <template #header><div style="display:flex;justify-content:space-between">
        <span>产品管理</span>
        <el-button type="primary" @click="openAdd">添加产品</el-button>
      </div></template>
      <el-table :data="products" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="symbol" label="代码" width="80" />
        <el-table-column prop="price" label="价格" />
        <el-table-column prop="profit_rate" label="收益率(%)" width="90" />
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }"><el-tag :type="row.status ? 'success' : 'danger'" size="small">{{ row.status ? '上架' : '下架' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="editProduct(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProduct(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑产品' : '添加产品'" width="500">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="代码"><el-input v-model="form.symbol" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :precision="5" /></el-form-item>
        <el-form-item label="24H最高"><el-input-number v-model="form.high_24h" :precision="2" /></el-form-item>
        <el-form-item label="24H最低"><el-input-number v-model="form.low_24h" :precision="2" /></el-form-item>
        <el-form-item label="24H量"><el-input v-model="form.volume_24h" /></el-form-item>
        <el-form-item label="24H额"><el-input v-model="form.amount_24h" /></el-form-item>
        <el-form-item label="收益率(%)"><el-input-number v-model="form.profit_rate" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" /></el-form-item>
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

const products = ref([]);
const dialogVisible = ref(false);
const isEdit = ref(false);
const editingId = ref(null);
const form = ref({ name: '', symbol: '', price: 0, high_24h: 0, low_24h: 0, volume_24h: '0', amount_24h: '0', profit_rate: 85, sort_order: 0, status: 1 });

async function loadProducts() {
  const res = await api.get('/admin/products');
  if (res.code === 200) products.value = res.data;
}

function openAdd() {
  isEdit.value = false;
  form.value = { name: '', symbol: '', price: 0, high_24h: 0, low_24h: 0, volume_24h: '0', amount_24h: '0', profit_rate: 85, sort_order: 0, status: 1 };
  dialogVisible.value = true;
}

function editProduct(row) {
  isEdit.value = true;
  editingId.value = row.id;
  form.value = { ...row };
  dialogVisible.value = true;
}

async function save() {
  let res;
  if (isEdit.value) {
    res = await api.put('/admin/product/' + editingId.value, form.value);
  } else {
    res = await api.post('/admin/product', form.value);
  }
  if (res.code === 200) { ElMessage.success(res.msg); dialogVisible.value = false; loadProducts(); }
  else ElMessage.error(res.msg);
}

async function deleteProduct(row) {
  await ElMessageBox.confirm('确定删除该产品？', '提示');
  const res = await api.delete('/admin/product/' + row.id);
  if (res.code === 200) { ElMessage.success('删除成功'); loadProducts(); }
}

onMounted(loadProducts);
</script>
