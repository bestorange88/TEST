<template>
  <div class="page">
    <div class="nav-bar"><div class="back" @click="router.back()">←</div><div class="title">通知详情</div></div>
    <div v-if="notice" class="notice-content">
      <h3>{{ notice.title }}</h3>
      <p class="notice-time">{{ notice.created_at }}</p>
      <div class="notice-body">{{ notice.content }}</div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api/request.js';
const route = useRoute();
const router = useRouter();
const notice = ref(null);
onMounted(async () => {
  const res = await api.get('/notice/' + route.params.id);
  if (res.code === 200) notice.value = res.data;
});
</script>
<style scoped>
.notice-content { padding: 20px; }
.notice-content h3 { font-size: 18px; margin-bottom: 8px; }
.notice-time { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
.notice-body { font-size: 15px; line-height: 1.8; }
</style>
