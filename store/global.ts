import { defineStore } from "pinia";
import { toast, type ToastOptions, type ToastType } from "vue3-toastify";

export const GlobalStore = defineStore("global", () => {
  /* state */
  const Loading = ref<boolean>(false);
  /* getter */
  const GetLoading = () => Loading.value;
  /* actions */
  const SetToast = (
    title: string,
    message: string,
    type: ToastType = "error",
    option: ToastOptions = {},
  ) => {
    toast(`<h3>${title}</h3><p>${message}</p>`, {
      type,
      ...option,
    });
  };
  const SetLoading = (val: boolean) => (Loading.value = val);

  return {
    GetLoading,
    SetToast,
    SetLoading,
  };
});
