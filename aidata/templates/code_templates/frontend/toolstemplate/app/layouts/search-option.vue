<template>
  <div class="d-flex flex-column h-100">
    <v-card elevation="2" rounded="lg" style="margin-bottom: 10px; flex-shrink: 0;">
      <slot name="search"></slot>
    </v-card>
    <v-card
      elevation="2"
      rounded="lg"
      style="flex-grow: 1;"
    >
      <slot name="content"></slot>
    </v-card>
  </div>
</template>
<style lang="scss" scoped></style>
<script lang="ts" setup>

</script>
