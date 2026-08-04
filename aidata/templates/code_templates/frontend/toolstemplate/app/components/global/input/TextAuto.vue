<template>
  <v-autocomplete
    hide-details="auto"
    rounded="lg"
    :variant="props.readonly ? 'plain' : 'outlined'"
  >
    <template v-slot:loader="{ isActive }">
      <progress-linear v-show="isActive" />
    </template>
    <template v-for="(item, key, index) in $slots" :key="index" v-slot:[key]>
      <slot :name="key"></slot> </template
  ></v-autocomplete>
</template>
<script lang="ts" setup>
interface ITextAutoProps {
  readonly?: boolean;
}
const props = withDefaults(defineProps<ITextAutoProps>(), {});
</script>
