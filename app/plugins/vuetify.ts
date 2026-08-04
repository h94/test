import { createVuetify } from "vuetify";
import * as VDateInput from "vuetify/labs/VDateInput";
import { zhHant } from "vuetify/locale";
import { aliases, mdi } from "vuetify/iconsets/mdi";

export default defineNuxtPlugin((nuxtApp) => {
  const vuetify = createVuetify({
    components: { ...VDateInput },
    icons: {
      defaultSet: "mdi",
      aliases,
      sets: {
        mdi,
      },
    },
    theme: {
      defaultTheme: (() => {
        try {
          const prefs = localStorage.getItem("user-preferences");
          return prefs ? JSON.parse(prefs)?.theme || "dark" : "dark";
        } catch {
          return "dark";
        }
      })(),
    },
    locale: {
      locale: "zhHant",
      fallback: "sv",
      messages: { zhHant },
    },
  });

  nuxtApp.vueApp.use(vuetify);
});
