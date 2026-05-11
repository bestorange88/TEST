import { createRouter, createWebHashHistory } from 'vue-router';

const routes = [
  { path: '/login', component: () => import('../pages/Login.vue') },
  {
    path: '/',
    component: () => import('../pages/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('../pages/Dashboard.vue') },
      { path: 'users', component: () => import('../pages/Users.vue') },
      { path: 'products', component: () => import('../pages/Products.vue') },
      { path: 'orders', component: () => import('../pages/Orders.vue') },
      { path: 'deposits', component: () => import('../pages/Deposits.vue') },
      { path: 'withdrawals', component: () => import('../pages/Withdrawals.vue') },
      { path: 'notices', component: () => import('../pages/Notices.vue') },
    ],
  },
];

const router = createRouter({ history: createWebHashHistory(), routes });

router.beforeEach((to, from, next) => {
  if (to.path !== '/login' && !localStorage.getItem('admin_token')) {
    next('/login');
  } else {
    next();
  }
});

export default router;
