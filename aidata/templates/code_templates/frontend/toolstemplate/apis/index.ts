import {
  allowedMethods,
  headers,
  apiUrl,
  type Method,
} from "@@/config/global/Http";
import { type IPayload } from "@@/types/Http";
export interface ApiResponse<T> {
  data: T | null;
  error: any;
}

export const BackendSite = async <T = any>(
  method: Method,
  url: string,
  payload: IPayload = {},
): Promise<ApiResponse<T>> => {
  if (!allowedMethods.includes(method))
    throw new Error(`Not allowedMethods: ${method}`);
  const isFormData =
    import.meta.client && payload.body instanceof FormData;
  try {
    const data = await $fetch<T>(`${apiUrl}${url}`, {
      headers: isFormData
        ? { "X-Requested-With": "XMLHttpRequest", charset: "utf-8" }
        : headers,
      method: method,
      query: payload.query,
      body: payload.body,
    });
    return {
      data,
      error: null,
    };
  } catch (err) {
    return {
      data: null,
      error: err,
    };
  }
};
