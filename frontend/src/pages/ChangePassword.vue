<template>
  <div class="page">
    <div class="nav-bar"><div class="back" @click="router.back()">←</div><div class="title">修改密码</div></div>
    <div style="padding:20px">
      <div class="form-item"><label>原密码</label><input v-model="form.old_password" type="password" placeholder="请输入原密码" /></div>
      <div class="form-item"><label>新密码</label><input v-model="form.new_password" type="password" placeholder="请输入新密码" /></div>
      <div class="form-item"><label>确认新密码</label><input v-model="form.confirm" type="password" placeholder="请再次输入新密码" /></div>
      <button class="btn" @click="submit">确认修改</button>
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
const form = ref({ old_password: '', new_password: '', confirm: '' });
async function submit() {
  if (form.value.new_password !== form.value.confirm) { alert('两次密码不一致'); return; }
  const res = await api.post('/auth/change-password', {
    username: userStore.user?.username,
    old_password: form.value.old_password,
    new_password: form.value.new_password,
  });
  if (res.code === 200) { alert('密码修改成功'); router.back(); }
  else alert(res.msg);
}
</script>
