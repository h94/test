const handleClick = (swiper, e) => {
  const clickedSlide = e.target.closest(".swiper-slide")
  if (!clickedSlide) return
  swiper.slides.forEach(slide => {
    slide.classList.remove("active")
  })
  clickedSlide.classList.add("active")
}
// odd swiper
;(() => {
  const oddSwipers = document.querySelectorAll(
    "main.balls section.ballsBlock .swiper",
  )
  if (oddSwipers.length === 0) return
  oddSwipers.forEach(oddSwiper => {
    const swiper = new Swiper(oddSwiper, {
      slidesPerView: 2,
      slidesPerGroup: 2,
      breakpoints: {
        1200: {
          slidesPerGroup: 3,
          slidesPerView: 3,
        },
        1400: {
          slidesPerView: 6,
        },
      },
      pagination: {
        el: ".swiper-pagination",
        clickable: true,
        renderBullet: (i, c) => {
          return `
              <use href="#paginationBullet" class="${c}" aria-label="Go to slide ${i + 1}" x=${0 + i * 15} y="0"/>
          `
        },
      },
    })
  })
})()
// balls swiper
;(() => {
  const ballsSwiper = document.querySelector(
    "main.balls section.sportsBlock .swiper",
  )
  if (!ballsSwiper) return
  const swiper = new Swiper(ballsSwiper, {
    slidesPerView: 8,
    navigation: {
      nextEl: ".next",
      prevEl: ".prev",
    },
    grid: {
      rows: 2,
      fill: "row",
    },
    breakpoints: {
      1400: {
        slidesPerView: "auto",
        grid: {
          rows: 1,
        },
      },
    },
    // active 效果
    on: {
      click: (swiper, e) => {
        handleClick(swiper, e)
      },
    },
  })
})()
// addAccount swiper
;(() => {
  const ballsSwipers = document.querySelectorAll(
    "main.addAccount section.addAccountBlock article.ballTabs .swiper",
  )
  if (ballsSwipers.length === 0) return
  ballsSwipers.forEach(ballsSwiper => {
    const swiper = new Swiper(ballsSwiper, {
      slidesPerView: 8,
      navigation: {
        nextEl: ".next",
        prevEl: ".prev",
      },
      grid: {
        rows: 2,
        fill: "row",
      },
      breakpoints: {
        1400: {
          slidesPerView: "auto",
          grid: {
            rows: 1,
          },
        },
      },
      // active 效果
      on: {
        click: (swiper, e) => {
          handleClick(swiper, e)
        },
      },
    })
  })
})()
