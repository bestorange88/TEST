import { createRouter, createWebHashHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', component: () => import('../pages/Home.vue') },
  { path: '/product', component: () => import('../pages/ProductList.vue') },
  { path: '/product/:id', component: () => import('../pages/ProductDetail.vue') },
  { path: '/personal', component: () => import('../pages/Personal.vue') },
  { path: '/login', component: () => import('../pages/Login.vue') },
  { path: '/register', component: () => import('../pages/Register.vue') },
  { path: '/verify', component: () => import('../pages/Verify.vue') },
  { path: '/orders', component: () => import('../pages/Orders.vue') },
  { path: '/deposit', component: () => import('../pages/Deposit.vue') },
  { path: '/withdraw', component: () => import('../pages/Withdraw.vue') },
  { path: '/deposit-list', component: () => import('../pages/DepositList.vue') },
  { path: '/withdraw-list', component: () => import('../pages/WithdrawList.vue') },
  { path: '/bank-cards', component: () => import('../pages/BankCards.vue') },
  { path: '/bank-card/add', component: () => import('../pages/BankCardAdd.vue') },
  { path: '/settings', component: () => import('../pages/Settings.vue') },
  { path: '/change-password', component: () => import('../pages/ChangePassword.vue') },
  { path: '/about', component: () => import('../pages/About.vue') },
  { path: '/notice/:id', component: () => import('../pages/Notice.vue') },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
