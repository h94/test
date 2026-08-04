<template>
  <v-overlay v-model="loading" class="align-center justify-center">
    <div class="d-flex flex-column align-center">
      <v-progress-circular color="primary" indeterminate size="88"></v-progress-circular>
      <div class="font">Loading</div>
    </div>
  </v-overlay>
</template>
<script lang="ts" setup>
import { useGlobal } from "~/composables/Global";

const { Loading: loading } = useGlobal();

</script>

<style lang="scss" scoped>
.font {
  margin-top: 10px;
  font-size: 2.5rem;
  text-align: center;
  color: transparent;
  font-weight: bold;
  background: linear-gradient(
    45deg,
    rgb(var(--v-theme-primary)),
    rgb(var(--v-theme-secondary)),
    rgb(var(--v-theme-primary))
  );
  -webkit-background-clip: text;
  background-size: 200% 200%;
  background-clip: text;
  animation: loading 1s linear infinite;
}

@keyframes loading {
  0% {
    background-position: 0% 0%;
  }

  100% {
    background-position: 100% 100%;
  }
}
</style>
