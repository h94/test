<template>
  <v-select
    hide-details="auto"
    variant="outlined"
    rounded="lg"
    @update:model-value="_itemCallback"
  >
    <template v-for="(item, key, index) in $slots" :key="index" v-slot:[key]>
      <slot :name="key"></slot>
    </template>
  </v-select>
</template>
<script setup lang="ts">
const emit = defineEmits(["itemCallback"]);
const _itemCallback = (item: any) => {
  emit("itemCallback", item);
};
</script>
