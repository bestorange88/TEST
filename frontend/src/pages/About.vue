<template>
  <div class="page">
    <div class="nav-bar"><div class="back" @click="router.back()">←</div><div class="title">关于我们</div></div>
    <div class="about-content">
      <div class="about-logo">
        <span class="logo-icon">🏛</span>
        <h2>中央结算公司</h2>
        <p>Central Settlement Corporation</p>
      </div>
      <div class="about-section">
        <h3>公司简介</h3>
        <p>中央结算公司是一家专业从事金融结算服务的公司，致力于为客户提供安全、便捷、高效的金融交易结算服务。</p>
      </div>
      <div class="about-section">
        <h3>服务范围</h3>
        <p>国债交易、资金结算、账户管理、实名认证等全方位金融服务。</p>
      </div>
      <div class="about-section">
        <h3>联系我们</h3>
        <p>如有任何问题，请联系在线客服。</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
</script>
<style scoped>
.about-content { padding: 20px; }
.about-logo { text-align: center; padding: 30px 0; }
.logo-icon { font-size: 48px; }
.about-logo h2 { margin-top: 8px; color: #8b0000; }
.about-logo p { color: var(--text-secondary); font-size: 14px; }
.about-section { margin-top: 20px; }
.about-section h3 { font-size: 16px; margin-bottom: 8px; }
.about-section p { font-size: 14px; color: var(--text-secondary); line-height: 1.6; }
</style>
