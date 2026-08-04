---
name: nuxt4-patterns
description: Nuxt 4 效能與懶載入模式（已為本專案 CSR-only 環境裁剪，移除 SSR/水合/路由規則章節）。
origin: ECC (trimmed)
---

# Nuxt 4 效能與懶載入模式

在處理 Nuxt 4 應用的效能優化、元件懶載入、延遲水合或有效負載大小時使用。

> **注意**：本副本已為專案環境裁剪。SSR 資料獲取、水合安全性、路由規則章節已移除，因為本專案預設關閉 SSR。

## 何時啟用

* 圍繞懶載入、延遲水合或有效負載大小的效能工作
* 與 Nuxt 路由、中間件相關的路由問題

## 懶載入與效能

* Nuxt 已經按路由進行程式碼分割。在微優化元件分割之前，保持路由邊界的意義。
* 使用 `Lazy` 前綴來動態匯入非關鍵元件。
* 使用 `v-if` 有條件地渲染懶載入元件，以便在 UI 實際需要時才載入該程式碼塊。
* 對首屏下方或非關鍵的互動式 UI 使用延遲水合。

```vue
<template>
  <LazyRecommendations v-if="showRecommendations" />
  <LazyProductGallery hydrate-on-visible />
</template>
```

* 對於自訂策略，使用 `defineLazyHydrationComponent()` 配合可見性或閒置策略。
* Nuxt 延遲水合適用於單檔案元件。向延遲水合的元件傳遞新 props 將立即觸發水合。
* 在內部導航中使用 `NuxtLink`，以便 Nuxt 可以預取路由元件和生成的有效負載。

## 檢查清單（僅適用部分）

* 重量級互動式元件是懶載入或延遲水合的
* 內部導航使用 `NuxtLink` 以利用預取