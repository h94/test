<template>
  <v-text-field
    style="pointer-events: unset;"
    hide-details="auto"
    rounded="lg"
    :variant="props.readonly ? 'plain' : 'outlined'"
    :readonly="props.readonly"
    @update:model-value="_update"
  >
    <template v-slot:loader="{ isActive }">
      <progress-linear v-show="isActive" />
    </template>
    <template v-for="(item, key, index) in $slots" :key="index" v-slot:[key]>
      <slot :name="key"></slot>
    </template>
  </v-text-field>
</template>
<script lang="ts" setup>
interface ITextFieldProps {
  readonly?: boolean;
}
const props = withDefaults(defineProps<ITextFieldProps>(), {});
const emit = defineEmits(["update"]);
const _update = (item: any) => {
  emit("update", item);
};
</script>
