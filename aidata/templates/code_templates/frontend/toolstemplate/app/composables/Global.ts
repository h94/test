import { toast, type ToastOptions, type ToastType } from "vue3-toastify";
import { GlobalStore } from "~~/store/global";

export const useGlobal = () => {
  const globalStore = GlobalStore();
  const Router = useRouter();
  const Route = useRoute();
  const Params = computed(() => Route.params);
  const Query = computed(() => Route.query);
  const Loading = computed(() => globalStore.GetLoading());
  const SetLoading = (val: boolean) => globalStore.SetLoading(val);
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

  return {
    Router,
    Route,
    Params,
    Query,
    Loading,
    SetLoading,
    SetToast,
  };
};
