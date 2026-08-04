<template>
  <NuxtLayout name="search-option">
    <template #content>
      <v-data-table :="tableProps" class="data-table">
        <template v-slot:top>
          <v-toolbar class="px-5">
            <TableRefreshBtn class="mr-3" :loading="loading" @click="" />
            <v-col cols="3" class="d-flex align-center">
              <TableSearch
                v-model="search"
                :loading="loading"
                combobox
                :items="tableComboItems"
              />
            </v-col>
          </v-toolbar>
        </template>
        <template v-slot:item.key1="{ item }">
          {{ item.key1 }}
        </template>
        <template v-slot:item.key2="{ item }">
          {{ item.key2 }}
        </template>
        <template v-slot:item.key3="{ item }">
          {{ item.key3 }}
        </template>
        <template v-slot:item.toast>
          <v-btn color="primary" @click="SetToast('標題', '內容', 'info')">
            範例Toast
          </v-btn>
        </template>
        <template v-slot:item.modal>
          <ExampleModal />
        </template>
      </v-data-table>
    </template>
  </NuxtLayout>
</template>

<script lang="ts" setup>
const { SetToast } = useGlobal();

/** 表格欄 align 須為字面類型，否則 v-data-table 型別會報錯 */
const headers = [
  { title: "Key 1", key: "key1", sortable: false, align: "center" as const },
  { title: "Key2", key: "key2", sortable: false, align: "center" as const },
  { title: "Key3", key: "key3", sortable: false, align: "center" as const },
  { title: "範例Toast", key: "toast", sortable: false, align: "center" as const, width: 120 },
  { title: "範例彈窗", key: "modal", sortable: false, align: "center" as const, width: 120 },
];

const templateData = ref<{ key1: string; key2: string; key3: string }[]>([]);

const search = ref<string>("");

const filteredRows = computed(() => {
  const rows = templateData.value;
  const s = search.value.toLowerCase();
  if (!s) return rows;
  return rows.filter((row) =>
    [row.key1, row.key2, row.key3].some((cell) =>
      String(cell).toLowerCase().includes(s),
    ),
  );
});

const loading = ref(false);

/** 原寫 Object.values(templateData) 會拿到 ref 結構而非列資料 */
const tableComboItems = computed(() => templateData.value.map((row) => row.key1));

const DEFAULT_TABLE_PROPS = {
  hover: true,
  fixedFooter: true,
  fixedHeader: true,
  class: {
    "h-100": true,
    "d-flex": true,
    "flex-column": true,
    "flex-grow-1": true,
    "min-h-0": true,
  },
};

const tableProps = computed(() => ({
  ...DEFAULT_TABLE_PROPS,
  headers,
  items: filteredRows.value,
  loading: loading.value,
}));

onMounted(() => {
  templateData.value = [
    { key1: "第一筆資料", key2: "key2", key3: "key3" },
    { key1: "第二筆資料", key2: "key2", key3: "key3" },
  ];
});

</script>

<style lang="scss" scoped>
.data-table {
  :deep(.v-table) {
    height: 100%;
    min-height: 0;
  }
  :deep(.v-table__wrapper) {
    flex: 1 1 0%;
    min-height: 0;
  }
}
</style>
