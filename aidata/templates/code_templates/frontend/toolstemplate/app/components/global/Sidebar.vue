<template>
  <v-app-bar elevation="1" density="compact" color="primary">
    <v-toolbar-title class="font-weight-bold">
      Review Tools
    </v-toolbar-title>
    <v-spacer />
    <template v-slot:append>
      <v-tooltip text="切換UI主題">
        <template v-slot:activator="{ props }">
          <v-btn
            variant="text"
            :icon="`mdi-${theme.global.name.value === 'dark' ? 'moon-waning-crescent' : 'white-balance-sunny'}`"
            @click="toggleTheme"
            v-bind="props"
          />
        </template>
      </v-tooltip>
    </template>
  </v-app-bar>
  <v-navigation-drawer permanent>
    <v-list color="primary" v-model:opened="openList">
      <template v-for="item in SidebarList">
        <v-list-group :value="item.name">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" :prepend-icon="'mdi-' + item.icon">
              <v-list-item-title class="text-subtitle-1">
                {{ item.name }}
              </v-list-item-title>
            </v-list-item>
          </template>
          <v-list-item
            v-for="subItem in item.subList"
            :key="subItem.name"
            :to="subItem.path"
            :active="$route.path === subItem.path"
          >
            <v-list-item-title class="text-subtitle-1">
              {{ subItem.name }}
            </v-list-item-title>
          </v-list-item>
        </v-list-group>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>
<style lang="scss" scoped></style>
<script lang="ts" setup>
import { useTheme } from "vuetify";

const SidebarList = [
  {
    name: "版面範例",
    key: "/example",
    col: "",
    icon: "view-dashboard-outline",
    subList: [
      {
        name: "default",
        key: "/example/default-layout",
        path: "/example/default-layout",
        col: "",
      },
      {
        name: "search-option",
        key: "/example/search-option",
        path: "/example/search-option",
        col: "",
      },
    ],
  },
];

const getUserPrefs = () => {
  try {
    const prefs = localStorage.getItem("user-preferences");
    return prefs ? JSON.parse(prefs) : {};
  } catch {
    return {};
  }
};

const theme = useTheme();
const openList = ref<string[]>([]);

const toggleTheme = async () => {
  try {
    theme.global.name.value = theme.global.current.value.dark ? "light" : "dark";
    await nextTick();
    const prefs = getUserPrefs();
    localStorage.setItem(
      "user-preferences",
      JSON.stringify({
        ...prefs,
        theme: theme.global.name.value,
      })
    );
  } catch (error) {
    console.error("切換主題失敗:", error);
    theme.global.name.value = theme.global.current.value.dark ? "light" : "dark";
  }
};
</script>
