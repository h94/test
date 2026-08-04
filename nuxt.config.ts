import vuetify from "vite-plugin-vuetify";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  compatibilityDate: "2026-07-10",
  app: {
    head: {
      title: "Frontend Tools Template",
    },
  },
  pinia: {
    storesDirs: ["./store/**"],
  },
  css: [
    "vuetify/styles",
    "@vuepic/vue-datepicker/dist/main.css",
    "@mdi/font/css/materialdesignicons.min.css",
  ],
  vite: {
    plugins: [vuetify({ autoImport: true })],
    optimizeDeps: {
      include: [
        "@vue/devtools-core",
        "@vue/devtools-kit",
        "dayjs",
        "dayjs/plugin/relativeTime",
        "dayjs/plugin/updateLocale",
        "dayjs/plugin/utc",
        "vue3-toastify",
      ],
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: "modern-compiler",
          silenceDeprecations: [
            "legacy-js-api",
            "color-functions",
            "global-builtin",
            "import",
            "if-function",
          ],
        } as Record<string, unknown>,
        sass: {
          api: "modern-compiler",
          silenceDeprecations: [
            "legacy-js-api",
            "color-functions",
            "global-builtin",
            "import",
            "if-function",
          ],
        } as Record<string, unknown>,
      },
    },
  },
  modules: ["@pinia/nuxt", "@vueuse/nuxt", "nuxt-lodash", "dayjs-nuxt"],
  build: {
    transpile: ["vuetify", "@vuepic/vue-datepicker"],
  },
  ssr: false,
  routeRules: {},
});
