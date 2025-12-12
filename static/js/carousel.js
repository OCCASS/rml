document.addEventListener("DOMContentLoaded", () => {
  const carousel = document.querySelector(".carousel");
  if (!carousel) return;

  const track = carousel.querySelector(".carousel__track");
  const slides = Array.from(carousel.querySelectorAll(".carousel__slide"));
  const dots = Array.from(carousel.querySelectorAll(".carousel__dot"));
  const prevButton = carousel.querySelector(".carousel__control--prev");
  const nextButton = carousel.querySelector(".carousel__control--next");
  const transitionValue = track.style.transition || "transform 0.4s ease";
  let activeIndex = 0;
  let startX = 0;
  let deltaX = 0;
  let isTouching = false;

  const setActiveState = (index) => {
    slides.forEach((slide, idx) => {
      slide.classList.toggle("is-active", idx === index);
    });
    dots.forEach((dot, idx) => {
      dot.classList.toggle("is-active", idx === index);
      dot.setAttribute("aria-current", idx === index ? "true" : "false");
    });
  };

  const moveTo = (index) => {
    activeIndex = (index + slides.length) % slides.length;
    track.style.transition = transitionValue;
    track.style.transform = `translateX(-${activeIndex * 100}%)`;
    setActiveState(activeIndex);
  };

  const handlePrev = () => moveTo(activeIndex - 1);
  const handleNext = () => moveTo(activeIndex + 1);

  prevButton.addEventListener("click", handlePrev);
  nextButton.addEventListener("click", handleNext);
  dots.forEach((dot, idx) => dot.addEventListener("click", () => moveTo(idx)));

  const handleTouchStart = (event) => {
    startX = event.touches[0].clientX;
    deltaX = 0;
    isTouching = true;
    track.style.transition = "none";
  };

  const handleTouchMove = (event) => {
    if (!isTouching) return;
    deltaX = event.touches[0].clientX - startX;
    track.style.transform = `translateX(calc(${-activeIndex * 100}% + ${deltaX}px))`;
  };

  const handleTouchEnd = () => {
    if (!isTouching) return;
    track.style.transition = transitionValue;

    if (Math.abs(deltaX) > 50) {
      if (deltaX < 0) {
        handleNext();
      } else {
        handlePrev();
      }
    } else {
      moveTo(activeIndex);
    }

    deltaX = 0;
    isTouching = false;
  };

  track.addEventListener("touchstart", handleTouchStart, { passive: true });
  track.addEventListener("touchmove", handleTouchMove, { passive: true });
  track.addEventListener("touchend", handleTouchEnd, { passive: true });
  window.addEventListener("resize", () => moveTo(activeIndex));

  moveTo(activeIndex);
});
