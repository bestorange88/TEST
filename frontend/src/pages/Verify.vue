<template>
  <div class="page">
    <div class="nav-bar">
      <div class="back" @click="router.back()">←</div>
      <div class="title">实名认证</div>
    </div>
    <div v-if="userStore.user?.verified" class="verify-success">
      <div class="success-icon">✅</div>
      <div class="success-text">认证成功</div>
    </div>
    <div v-else class="verify-form">
      <div class="form-item">
        <label>真实姓名</label>
        <input v-model="form.real_name" placeholder="请输入真实姓名" />
      </div>
      <div class="form-item">
        <label>身份证号</label>
        <input v-model="form.id_card" placeholder="请输入身份证号" />
      </div>
      <div class="form-item">
        <label>手机号(选填)</label>
        <input v-model="form.phone" placeholder="请输入手机号" />
      </div>
      <button class="btn" style="margin:20px" @click="submit">提交认证</button>
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
const form = ref({ real_name: '', id_card: '', phone: '' });

async function submit() {
  const res = await api.post('/user/verify', form.value);
  if (res.code === 200) {
    alert('认证成功');
    userStore.fetchUserInfo();
  } else {
    alert(res.msg);
  }
}
</script>

<style scoped>
.verify-form { padding: 20px; }
.verify-success { text-align: center; padding: 80px 20px; }
.success-icon { font-size: 48px; margin-bottom: 12px; }
.success-text { font-size: 18px; font-weight: 600; color: var(--green); }
</style>
