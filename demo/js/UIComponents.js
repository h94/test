// Filter
class Filter {
  constructor() {
    this.filter = document.querySelector(".filter")
  }
  /**
   * @param {string} popup - 目標彈窗
   */
  openFilter(popup) {
    if (!this.filter) return
    this.closeFilter()
    popup.classList.add("display")
  }
  closeFilter() {
    if (!this.filter) return
    const popups = this.filter?.querySelectorAll(".popup.display")
    popups.forEach(popup => {
      popup.classList.remove("display")
    })
  }
}
// Tabs
class Tabs {
  #url
  constructor() {
    this.#url = new URL(window.location)
  }
  /**
   * @param {string} target - 目標選項卡的類名
   * @param {HTMLElement} container - 包含選項卡的容器元素
   */
  change(target, container) {
    if (!container || !target) {
      console.warn("無效參數")
      return
    }
    container
      .querySelectorAll(":scope > .active")
      .forEach(active => active.classList.remove("active"))
    const targetEl = container.querySelector(`.${target}`)
    if (targetEl) {
      targetEl.classList.add("active")
    } else {
      console.warn("未找到目標元素")
    }
    this.#url.search = ""
    window.history.replaceState({}, "", this.#url)
  }
  /**
   * @param {string} paramName - URL 查詢參數名稱
   * @param {HTMLElement} container - 包含選項卡的容器元素
   */
  urlChange(paramName, container) {
    if (!container || !paramName) {
      console.warn("無效參數")
      return
    }
    const target = this.#url.searchParams.get(paramName)
    if (target) {
      container
        .querySelectorAll(":scope > .active")
        .forEach(active => active.classList.remove("active"))
      const targetEl = container.querySelector(`.${target}`)
      if (targetEl) {
        targetEl.classList.add("active")
      } else {
        console.warn("未找到目標元素")
      }
    }
  }
  /**
   * @param {string} param - URL 查詢參數名稱
   */
  getParams(param) {
    return this.#url.searchParams.get(param)
  }
}
