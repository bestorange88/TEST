<template>
  <div class="page">
    <div class="nav-bar"><div class="back" @click="router.back()">←</div><div class="title">添加银行卡</div></div>
    <div style="padding:20px">
      <div class="form-item"><label>银行名称</label><input v-model="form.bank_name" placeholder="如：中国银行" /></div>
      <div class="form-item"><label>卡号</label><input v-model="form.card_number" placeholder="请输入银行卡号" /></div>
      <div class="form-item"><label>持卡人姓名</label><input v-model="form.holder_name" placeholder="请输入持卡人姓名" /></div>
      <div class="form-item"><label>开户行(选填)</label><input v-model="form.branch" placeholder="请输入开户支行" /></div>
      <button class="btn" @click="submit">确认添加</button>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api/request.js';
const router = useRouter();
const form = ref({ bank_name: '', card_number: '', holder_name: '', branch: '' });
async function submit() {
  const res = await api.post('/user/bank-card', form.value);
  if (res.code === 200) { alert('添加成功'); router.back(); }
  else alert(res.msg);
}
</script>
