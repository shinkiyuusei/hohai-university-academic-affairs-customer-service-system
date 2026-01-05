<script setup lang="ts">
// 空的 setup 块
</script>

<template>
  <router-view v-slot="{ Component, route }">
    <transition name="page" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>
</template>

<style>
#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* 全局页面切换动画 */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 为登录注册页面特别的动画 */
.page-enter-active {
  transition-delay: 0.05s;
}
</style>
