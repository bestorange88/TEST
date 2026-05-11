<template>
  <div class="page login-page">
    <div class="login-header">
      <div class="logo">
        <span class="logo-icon">🏛</span>
        <span class="logo-text">中央结算公司</span>
      </div>
      <div class="lang-toggle">🌐 简体中文</div>
    </div>
    <div class="login-form">
      <h2>账号登录</h2>
      <div class="form-item">
        <label>账号</label>
        <input v-model="form.username" placeholder="请输入账户" />
      </div>
      <div class="form-item">
        <label>密码</label>
        <div class="password-wrap">
          <input
            v-model="form.password"
            :type="showPwd ? 'text' : 'password'"
            placeholder="请输入密码"
          />
          <span class="pwd-toggle" @click="showPwd = !showPwd">{{ showPwd ? '👁' : '👁‍🗨' }}</span>
        </div>
      </div>
      <div v-if="errMsg" class="err-msg">{{ errMsg }}</div>
      <button class="btn" :disabled="!canSubmit" @click="handleLogin">登录</button>
    </div>
    <div class="login-footer">
      <div class="footer-links">
        <span @click="router.push('/register')">立即注册</span>
        <span class="divider">|</span>
        <span>在线客服</span>
      </div>
      <div class="agreement">登录即表示同意APP <a href="#">隐私政策</a></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user.js';
import api from '../api/request.js';

const router = useRouter();
const userStore = useUserStore();

const form = ref({ username: '', password: '' });
const showPwd = ref(false);
const errMsg = ref('');

const canSubmit = computed(() => form.value.username && form.value.password);

async function handleLogin() {
  errMsg.value = '';
  const res = await api.post('/auth/login', form.value);
  if (res.code === 200) {
    userStore.setUser(res.data);
    router.push('/home');
  } else {
    errMsg.value = res.msg;
  }
}
</script>

<style scoped>
.login-page {
  background: var(--bg);
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.login-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 6px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #8b0000;
}

.lang-toggle {
  font-size: 13px;
  color: var(--text-secondary);
}

.login-form {
  flex: 1;
  padding-top: 20px;
}

.login-form h2 {
  font-size: 22px;
  margin-bottom: 24px;
}

.password-wrap {
  position: relative;
}

.password-wrap input {
  width: 100%;
  height: 44px;
  padding: 0 40px 0 12px;
  background: #f9fafb;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 15px;
}

.pwd-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 16px;
}

.err-msg {
  color: var(--danger);
  font-size: 13px;
  margin-bottom: 12px;
}

.login-footer {
  padding: 20px 0 40px;
  text-align: center;
}

.footer-links {
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--primary);
}

.footer-links span {
  cursor: pointer;
}

.footer-links .divider {
  margin: 0 8px;
  color: #ccc;
}

.agreement {
  font-size: 12px;
  color: var(--text-secondary);
}

.agreement a {
  color: var(--primary);
}
</style>
