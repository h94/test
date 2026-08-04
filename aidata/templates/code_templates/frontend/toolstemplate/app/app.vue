<template>
  <v-app>
    <VLoading />
    <Sidebar />
    <v-main class="" style="height: 100vh; overflow: hidden;">
      <div class="pa-5 h-100">
        <NuxtPage />
      </div>
    </v-main>
  </v-app>
</template>

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
</style>

