<template>
  <div class="h-100 d-flex flex-column align-center justify-center overflow-y-auto">
    <div class="text-h5 font-weight-bold mb-6">
      Review Tools
    </div>
    <p class="text-body-2 text-medium-emphasis text-center mb-6 px-4" style="max-width: 32rem;">
      目前僅保留版面範例頁供新頁面參考。請由下方連結或由左側選單進入。
    </p>
    <div class="d-flex ga-4">
      <v-btn
        color="primary"
        :to="{ path: '/example/default-layout' }"
      >
        default layout 範例
      </v-btn>
      <v-btn
        variant="tonal"
        :to="{ path: '/example/search-option' }"
      >
        search-option layout 範例
      </v-btn>
    </div>
  </div>
</template>

<script lang="ts" setup></script>

<style lang="scss" scoped></style>
