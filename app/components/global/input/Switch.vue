<template>
  <v-switch inset color="primary" hide-details="auto">
    <template v-for="(item, key, index) in $slots" :key="index" v-slot:[key]>
      <slot :name="key"></slot>
    </template>
  </v-switch>
</template>
