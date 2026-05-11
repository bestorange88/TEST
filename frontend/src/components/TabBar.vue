<template>
  <div class="tabbar">
    <div
      v-for="item in tabs"
      :key="item.path"
      class="tab-item"
      :class="{ active: route.path === item.path }"
      @click="router.push(item.path)"
    >
      <div class="tab-icon">{{ item.icon }}</div>
      <div class="tab-label">{{ item.label }}</div>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const tabs = [
  { path: '/home', label: '首页', icon: '🏠' },
  { path: '/product', label: '产品', icon: '📊' },
  { path: '/personal', label: '个人中心', icon: '👤' },
];
</script>

<style scoped>
.tabbar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 750px;
  height: 56px;
  background: #fff;
  display: flex;
  border-top: 1px solid #eee;
  z-index: 999;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #999;
  transition: color 0.2s;
}

.tab-item.active {
  color: var(--primary);
}

.tab-icon {
  font-size: 20px;
  margin-bottom: 2px;
}

.tab-label {
  font-size: 11px;
}
</style>
