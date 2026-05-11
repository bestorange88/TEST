<template>
  <el-container style="min-height:100vh">
    <el-aside width="220px" style="background:#304156">
      <div class="logo">🏛 管理后台</div>
      <el-menu :default-active="route.path" background-color="#304156" text-color="#bfcbd9" active-text-color="#409eff" router>
        <el-menu-item index="/dashboard"><span>📊 数据概览</span></el-menu-item>
        <el-menu-item index="/users"><span>👥 用户管理</span></el-menu-item>
        <el-menu-item index="/products"><span>📦 产品管理</span></el-menu-item>
        <el-menu-item index="/orders"><span>📋 订单管理</span></el-menu-item>
        <el-menu-item index="/deposits"><span>💰 充值审核</span></el-menu-item>
        <el-menu-item index="/withdrawals"><span>💸 提现审核</span></el-menu-item>
        <el-menu-item index="/notices"><span>📢 通知管理</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;align-items:center;justify-content:flex-end;background:#fff;border-bottom:1px solid #eee">
        <span style="margin-right:16px">{{ adminUser?.username }}</span>
        <el-button type="text" @click="logout">退出</el-button>
      </el-header>
      <el-main style="background:#f0f2f5"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const adminUser = computed(() => JSON.parse(localStorage.getItem('admin_user') || '{}'));

function logout() {
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin_user');
  router.push('/login');
}
</script>

<style scoped>
.logo { color: #fff; font-size: 16px; font-weight: 700; padding: 20px; text-align: center; }
</style>
