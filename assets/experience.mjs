const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
const root = document.documentElement;
const header = document.querySelector(".site-header");
const scene = document.querySelector(".grove-scene");
const hero = document.querySelector(".hero");
const footer = document.querySelector(".footer");
const mobileCta = document.querySelector(".mobile-cta");
const reveals = [...document.querySelectorAll(".reveal")];

root.classList.add("has-js");

function revealEverything() {
  reveals.forEach((element) => element.classList.add("is-visible"));
}

function setupReveals() {
  if (motionPreference.matches || !("IntersectionObserver" in window)) {
    revealEverything();
    return;
  }

  try {
    const observer = new IntersectionObserver(
      (entries, activeObserver) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          activeObserver.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8%", threshold: 0.12 },
    );
    reveals.forEach((element) => observer.observe(element));
  } catch {
    revealEverything();
  }
}

setupReveals();

function updateScrollState() {
  const maximum = document.documentElement.scrollHeight - window.innerHeight;
  const progress = maximum > 0 ? Math.max(0, Math.min((window.scrollY / maximum) * 100, 100)) : 0;
  root.style.setProperty("--scroll-progress", `${progress}%`);
  header?.classList.toggle("is-scrolled", window.scrollY > 18);
  const heroHasPassed = (hero?.getBoundingClientRect().bottom ?? 0) < 80;
  const footerIsVisible = (footer?.getBoundingClientRect().top ?? Infinity) < window.innerHeight;
  const ctaShouldBeActive = heroHasPassed && !footerIsVisible;
  mobileCta?.classList.toggle("is-active", ctaShouldBeActive);
  if (!ctaShouldBeActive && document.activeElement === mobileCta) mobileCta.blur();
}

updateScrollState();
window.addEventListener("scroll", updateScrollState, { passive: true });
window.addEventListener("resize", updateScrollState, { passive: true });

if (scene && !motionPreference.matches) {
  scene.addEventListener("pointermove", (event) => {
    const bounds = scene.getBoundingClientRect();
    const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 2;
    const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * 2;
    root.style.setProperty("--px", x.toFixed(3));
    root.style.setProperty("--py", y.toFixed(3));
  });

  scene.addEventListener("pointerleave", () => {
    root.style.setProperty("--px", "0");
    root.style.setProperty("--py", "0");
  });
}

function handleMotionChange(event) {
  if (event.matches) {
    revealEverything();
    root.style.setProperty("--px", "0");
    root.style.setProperty("--py", "0");
  }
}

if (typeof motionPreference.addEventListener === "function") {
  motionPreference.addEventListener("change", handleMotionChange);
} else {
  motionPreference.addListener?.(handleMotionChange);
}
