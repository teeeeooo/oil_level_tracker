// The user manual: clips play while on screen, a screenshot opens larger, and the table of
// contents marks the section on screen. A classic script: the page opens from a file.
(() => {
  const clips = [...document.querySelectorAll("main video")];
  const onScreen = new IntersectionObserver((entries) => {
    for (const { target, isIntersecting } of entries) {
      if (isIntersecting && !target.dataset.stopped) target.play().catch(() => {});
      else target.pause();
    }
  }, { threshold: 0.4 });
  for (const clip of clips) {
    clip.muted = true;
    onScreen.observe(clip);
    clip.addEventListener("click", () => {
      if (clip.paused) {
        delete clip.dataset.stopped;
        clip.play().catch(() => {});
      } else {
        clip.dataset.stopped = "1";
        clip.pause();
      }
    });
  }

  const zoom = document.getElementById("zoom");
  const big = zoom.querySelector("img");
  for (const image of document.querySelectorAll("main img")) {
    image.addEventListener("click", () => {
      big.src = image.src;
      big.alt = image.alt;
      zoom.showModal();
    });
  }
  zoom.addEventListener("click", () => zoom.close());

  const links = [...document.querySelectorAll(".toc a")];
  const headings = links.map((link) => document.getElementById(link.hash.slice(1))).filter(Boolean);
  let pending = false;
  function mark() {
    pending = false;
    let current = headings[0];
    for (const heading of headings) if (heading.getBoundingClientRect().top < 96) current = heading;
    for (const link of links) link.classList.toggle("on", link.hash === `#${current.id}`);
  }
  addEventListener("scroll", () => {
    if (!pending) {
      pending = true;
      requestAnimationFrame(mark);
    }
  }, { passive: true });
  mark();
})();
