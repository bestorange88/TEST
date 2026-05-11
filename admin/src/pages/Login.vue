<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <h2>中央结算公司 - 管理后台</h2>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="请输入管理员账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" @click="handleLogin" :loading="loading" style="width:100%">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import api from '../api/request.js';

const router = useRouter();
const form = ref({ username: '', password: '' });
const loading = ref(false);

async function handleLogin() {
  loading.value = true;
  const res = await api.post('/auth/login', form.value);
  loading.value = false;
  if (res.code === 200) {
    if (res.data.user.role !== 'admin') {
      ElMessage.error('无管理员权限');
      return;
    }
    localStorage.setItem('admin_token', res.data.token);
    localStorage.setItem('admin_user', JSON.stringify(res.data.user));
    router.push('/dashboard');
  } else {
    ElMessage.error(res.msg);
  }
}
</script>

<style scoped>
.login-container { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: #f0f2f5; }
.login-card { width: 400px; }
.login-card h2 { text-align: center; margin-bottom: 24px; color: #303133; }
</style>
