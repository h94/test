import Vue3Toastify, { type ToastContainerOptions } from 'vue3-toastify';
import "../../styles/_toastifyCustom.scss";

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(Vue3Toastify, {
    theme: 'colored',
    autoClose: 5000,
    dangerouslyHTMLString: true,
  }) as ToastContainerOptions;
});