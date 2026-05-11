<template>
  <div class="app-container">
    <router-view />
    <TabBar v-if="showTabBar" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import TabBar from './components/TabBar.vue';

const route = useRoute();
const tabPages = ['/home', '/product', '/personal'];
const showTabBar = computed(() => tabPages.includes(route.path));
</script>
