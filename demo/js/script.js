const filterInstance = new Filter()
const tabInstance = new Tabs()
//close filter when clicking mask
;(() => {
  const mask = document.querySelector(".filter .mask")
  if (!mask) return
  mask.addEventListener("click", e => {
    filterInstance.closeFilter()
  })
})()
// open popup
;(() => {
  const popups = document.querySelectorAll("[data-popup]")
  if (popups.length == 0) return
  popups.forEach(popup => {
    popup.addEventListener("click", e => {
      e.preventDefault()
      let targetPopup = document.querySelector(
        `.filter .popup.${e.currentTarget.dataset.popup}`
      )
      if (targetPopup) {
        filterInstance.openFilter(targetPopup)
      } else {
        console.warn(`未找到目標`)
      }
    })
  })
})()
// close popup
;(() => {
  const closes = document.querySelectorAll(".filter .close")
  if (closes.length == 0) return
  closes.forEach(close => {
    close.addEventListener("click", () => {
      filterInstance.closeFilter()
    })
  })
})()
// 下拉選單
;(() => {
  const selects = document.querySelectorAll("label.select")
  if (selects.length === 0) return
  selects.forEach(select => {
    select.addEventListener("click", e => {
      selects.forEach(s => {
        if (s !== select) s.classList.remove("active")
      })
      e.currentTarget.classList.toggle("active")
    })
  })
  document.addEventListener("click", e => {
    if (![...selects].some(s => s.contains(e.target))) {
      selects.forEach(s => s.classList.remove("active"))
    }
  })
})()
// 側欄-開關
;(() => {
  const sideBars = document.querySelectorAll("header .menu-navbar.sideBar")
  if (sideBars.length === 0) return
  sideBars.forEach(s => {
    s.addEventListener("click", e => {
      e.target.closest("button.navber") &&
        e.currentTarget.classList.add("active")
      if (e.target.closest(".close_ic") || e.target.closest(".mask")) {
        e.currentTarget.classList.remove("active")
      }
    })
  })
})()
// 待結投注-側欄釘選
;(() => {
  const settlement = document.querySelector("header aside button.settlement")
  if (!settlement) return
  settlement.addEventListener("click", e => {
    if (e.target.closest(".pin_ic")) {
      e.currentTarget.classList.toggle("show")
    }
  })
})()
// 球類頁tab切換
;(() => {
  const tabs = document.querySelectorAll(
    "main.balls section.tabBlock [data-tab]"
  )
  const balls = document.querySelector("main.balls section.ballsBlock")
  if (tabs.length === 0 && !balls) return
  tabs.forEach(tab => {
    tab.addEventListener("click", e => {
      tabs.forEach(t => t.classList.remove("active"))
      e.currentTarget.classList.add("active")
      const target = e.target.dataset.tab
      tabInstance.change(target, balls)
    })
  })
})()
// 管理頁tab切換
;(() => {
  const tabs = document.querySelectorAll(
    "main.account section.tabBlock [data-tab]"
  )
  const account = document.querySelector("main.account section.accountBlock")
  if (tabs.length === 0 && !account) return
  tabInstance.urlChange("tab", account)
  const url = tabInstance.getParams("tab")
  tabs.forEach(t => {
    t.classList.remove("active")
    if (url) {
      t.dataset.tab == url && t.classList.add("active")
    } else {
      tabs[0].classList.add("active")
    }
  })
})()
// 新增帳號頁tab切換
;(() => {
  const tabs = document.querySelectorAll(
    "main.addAccount section.tabBlock [data-tab]"
  )
  const addAccountBlock = document.querySelector(
    "main.addAccount section.addAccountBlock"
  )
  if (tabs.length === 0 && !addAccountBlock) return
  tabInstance.urlChange("tab", addAccountBlock)
  const url = tabInstance.getParams("tab")
  tabs.forEach(t => {
    t.classList.remove("active")
    if (url) {
      t.dataset.tab == url && t.classList.add("active")
    } else {
      window.location.replace(`../index.html`)
    }
  })
})()
// 新增球類表單收合
;(() => {
  const ballLists = document.querySelectorAll(
    "section.ballsBlock .data ul li[data-index]"
  )
  if (ballLists.length === 0) return
  ballLists.forEach(ballList => {
    ballList.addEventListener("click", e => {
      if (e.target.closest(".thead")) {
        const target = e.currentTarget.dataset.index
        ballLists.forEach(b => {
          if (b.dataset.index === target) {
            b.classList.toggle("close")
          }
        })
      }
    })
  })
})()
// 即時注單tab切換
;(() => {
  const betting = document.querySelector("main.betting section.dataBlock")
  if (!betting) return
  tabInstance.urlChange("tab", betting)
})()
// 待結投注tab切換
;(() => {
  const tabs = document.querySelectorAll(
    "header aside button.settlement [data-tab]"
  )
  const settlement = document.querySelector(
    "main.settlement section.settlementBlock"
  )
  if (tabs.length !== 0 && settlement) {
    tabInstance.urlChange("tab", settlement)
    const url = tabInstance.getParams("tab")
    tabs.forEach(t => {
      t.classList.remove("active")
      if (url) {
        t.dataset.tab == url && t.classList.add("active")
      } else {
        tabs[0].classList.add("active")
      }
    })
  }
})()
// 待結投注-詳細列表
;(() => {
  const tbody = document.querySelectorAll(
    "main.settlement section.settlementBlock article.data > ul > li.tbody"
  )
  if (tbody.length === 0) return
  tbody.forEach(t => {
    t.addEventListener("click", e => {
      if (e.target.closest(".plus_ic")) {
        e.currentTarget.classList.toggle("active")
      }
    })
  })
})()
// 待結投注-總得分收合
;(() => {
  const ballNames = document.querySelectorAll(
    "main.settlement section.settlementBlock article.data > ul"
  )
  if (ballNames.length === 0) return
  ballNames.forEach(b => {
    b.addEventListener("click", e => {
      if (e.target.closest(".ballName")) {
        e.currentTarget.classList.toggle("active")
      }
    })
  })
})()
// 返回
;(() => {
  const backs = document.querySelectorAll(".back")
  if (backs.length === 0) return
  backs.forEach(back => {
    back.addEventListener("click", () => {
      window.history.back()
    })
  })
})()
