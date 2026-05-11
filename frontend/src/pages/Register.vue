<template>
  <div class="page">
    <div class="nav-bar">
      <div class="back" @click="router.back()">←</div>
      <div class="title">注册账号</div>
    </div>
    <div class="register-form">
      <div class="form-item">
        <label>账号</label>
        <input v-model="form.username" placeholder="请输入账号" />
      </div>
      <div class="form-item">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="请输入密码(至少6位)" />
      </div>
      <div class="form-item">
        <label>确认密码</label>
        <input v-model="form.confirmPwd" type="password" placeholder="请再次输入密码" />
      </div>
      <div class="form-item">
        <label>邀请码(选填)</label>
        <input v-model="form.invite_code" placeholder="请输入邀请码" />
      </div>
      <div v-if="errMsg" class="err-msg">{{ errMsg }}</div>
      <button class="btn" @click="handleRegister">立即注册</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user.js';
import api from '../api/request.js';

const router = useRouter();
const userStore = useUserStore();
const form = ref({ username: '', password: '', confirmPwd: '', invite_code: '' });
const errMsg = ref('');

async function handleRegister() {
  errMsg.value = '';
  if (!form.value.username || !form.value.password) {
    errMsg.value = '请填写完整信息';
    return;
  }
  if (form.value.password !== form.value.confirmPwd) {
    errMsg.value = '两次密码不一致';
    return;
  }
  const res = await api.post('/auth/register', form.value);
  if (res.code === 200) {
    userStore.setUser(res.data);
    router.push('/home');
  } else {
    errMsg.value = res.msg;
  }
}
</script>

<style scoped>
.register-form {
  padding: 20px;
}

.err-msg {
  color: var(--danger);
  font-size: 13px;
  margin-bottom: 12px;
}
</style>
