<template>
  <router-view></router-view>
</template>

<script setup>
import { onMounted } from 'vue';

// 在组件挂载时测试接口
onMounted(() => {
  fetch('http://localhost:8000/api/data')
    .then(res => res.json())
    .then(data => {
      console.log('后端返回数据:', data);
      alert(data.data); // 弹出提示，证明前后端通了
    })
    .catch(err => {
      console.error('请求失败:', err);
    });
});
</script>


<style scoped>
</style>