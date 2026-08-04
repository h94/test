<template>
  <v-app>
    <VLoading />
    <Sidebar />
    <v-main class="" style="height: 100vh; overflow: hidden;">
      <div class="pa-5 h-100">
        <NuxtPage />
      </div>
      1122
    </v-main>
  </v-app>
</template>
<script setup lang="ts">
import { VLoading } from '@/components/loading'
</script>
<script lang="ts" setup>
</script>
<style lang="scss" scoped></style>
<style>
html,
body {
  overflow: hidden !important;
  height: 100vh;
  width: 100vw;
}
main {
  height: 100vh;
  overflow: hidden;
  color: #000;
}
</style>

