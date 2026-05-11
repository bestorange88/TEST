<template>
  <div class="page">
    <div class="nav-bar"><div class="back" @click="router.back()">←</div><div class="title">设置</div></div>
    <div class="cell-list">
      <div class="cell-item" @click="router.push('/change-password')">
        <div class="cell-icon" style="background:#fde8e8">🔒</div>
        <div class="cell-title">修改密码</div>
        <div class="cell-arrow">›</div>
      </div>
      <div class="cell-item">
        <div class="cell-icon" style="background:#e8f0fd">🌐</div>
        <div class="cell-title">语言设置</div>
        <div class="cell-arrow">简体中文 ›</div>
      </div>
      <div class="cell-item" @click="router.push('/about')">
        <div class="cell-icon" style="background:#e8f4e8">ℹ️</div>
        <div class="cell-title">关于我们</div>
        <div class="cell-arrow">›</div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
</script>
