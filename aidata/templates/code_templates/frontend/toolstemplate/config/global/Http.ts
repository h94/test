export const allowedMethods = ['HEAD', 'GET', 'POST', 'DELETE', 'PUT', 'PATCH', 'OPTIONS'];

export const headers = {
  'Content-Type': 'application/json',
  'X-Requested-With': 'XMLHttpRequest',
  'charset': 'utf-8',
};

export const timeoutSec = 120000;

export const apiUrl = import.meta.env.VITE_API_URL;

export const apiPredictUrl = import.meta.env.VITE_API_PREDICT;

export const apiPriceCenterUrl = import.meta.env.VITE_API_PRICECENTER;

export const apiPriceCenterSiteUrl = import.meta.env.VITE_API_INPLAYZ

export const formDataHeaders = {
  'Accept': '*/*',
  'Content-Type': 'multipart/form-data',
  'charset': 'utf-8',
};

export type Method = 'HEAD' | 'GET' | 'POST' | 'DELETE' | 'PUT' | 'PATCH' | 'OPTIONS'