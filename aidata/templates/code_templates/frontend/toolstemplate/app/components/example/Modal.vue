<template>
  <v-dialog width="400" v-model="isModalOpen">
    <template #activator="{ props: activatorProps }">
      <v-btn
        variant="flat"
        color="primary"
        v-bind="activatorProps"
        text="開啟範例 modal"
      />
    </template>
    <template #default="{ isActive }">
      <v-card>
        <v-card-item>
          <v-card-title class="d-flex align-center">
            <span class="text-truncate">範例 modal</span>
            <v-spacer />
            <v-btn icon="mdi-close" variant="text" @click="isActive.value = false" />
          </v-card-title>
        </v-card-item>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <InputTextField
                  v-model="sampleText"
                  label="示意欄位"
                  hide-details="auto"
                  clearable
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="flat" color="error" text="取消" @click="closeModal" />
          <v-btn variant="flat" color="primary" text="確定" @click="confirm" />
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>

<script lang="ts" setup>
import { useGlobal } from "~/composables/Global";

const emit = defineEmits<{ refresh: [] }>();
const { SetToast } = useGlobal();

const isModalOpen = ref(false);
const sampleText = ref("");

const closeModal = () => {
  isModalOpen.value = false;
};

const confirm = () => {
  SetToast(
    "範例 modal",
    sampleText.value ? `輸入：${sampleText.value}` : "已送出（示意）",
    "success",
  );
  emit("refresh");
  closeModal();
};

watch(isModalOpen, (open) => {
  if (open) sampleText.value = "";
});
</script>

<style lang="scss" scoped></style>
