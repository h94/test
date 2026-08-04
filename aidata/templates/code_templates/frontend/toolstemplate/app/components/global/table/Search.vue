<template>
  <v-combobox v-if="props.combobox" v-bind="defaultProps" :menu-props="{ transition: 'slide-y-transition' }">
    <template v-slot:loader="{ isActive }">
      <progress-linear v-show="isActive" />
    </template>
  </v-combobox>
  <InputTextField v-else v-bind="defaultProps" />
</template>

<script lang="ts" setup>
const props = defineProps({
  combobox: Boolean,
});
const defaultProps = <any>{
  density: "compact",
  variant: "solo",
  prependInnerIcon: "mdi-magnify",
  plac: true,
  singleLine: true,
  hideDetails: true,
  clearable: true,
  rounded: "lg",
  flat: true,
};
</script>

<style lang="scss" scoped></style>
