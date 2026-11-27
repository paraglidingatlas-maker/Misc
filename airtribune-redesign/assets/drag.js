/* Drag to scroll: mouse users can grab any sideways-scrolling row and throw it.
   Touch and trackpads keep their native scrolling. Opt in with data-drag on the scroller.
   A drag of more than 5 px swallows the click that follows, so links and buttons in the row
   still work on a plain click. Scroll snap is paused while dragging and comes back on release. */
(function(){
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const css = document.createElement("style");
  css.textContent = "[data-drag].can-drag{cursor:grab}[data-drag].dragging{cursor:grabbing;scroll-snap-type:none!important;scroll-behavior:auto!important;user-select:none;-webkit-user-select:none}[data-drag].dragging *{cursor:grabbing!important}[data-drag] img{-webkit-user-drag:none}";
  document.head.appendChild(css);

  function bind(el){
    if (el.__drag) return; el.__drag = true;
    let down = false, moved = false, sx = 0, sl = 0, lx = 0, lt = 0, vx = 0, raf = 0;
    const fits = () => el.scrollWidth <= el.clientWidth + 1;
    const mark = () => el.classList.toggle("can-drag", !fits());
    mark(); addEventListener("resize", mark); new ResizeObserver(mark).observe(el);
    el.addEventListener("pointerdown", e => {
      if (e.pointerType !== "mouse" || e.button !== 0 || fits()) return;
      if (e.target.closest("input,select,textarea,[contenteditable]")) return;
      cancelAnimationFrame(raf);
      down = true; moved = false; sx = lx = e.clientX; sl = el.scrollLeft; lt = performance.now(); vx = 0;
    });
    addEventListener("pointermove", e => {
      if (!down) return;
      const dx = e.clientX - sx;
      if (!moved && Math.abs(dx) > 5){ moved = true; el.classList.add("dragging"); }
      if (!moved) return;
      e.preventDefault();
      el.scrollLeft = sl - dx;
      const t = performance.now(), dt = Math.max(1, t - lt);
      vx = .8 * ((e.clientX - lx) / dt) + .2 * vx; lx = e.clientX; lt = t;
    });
    const end = () => {
      if (!down) return; down = false;
      if (!moved){ return; }
      const release = () => el.classList.remove("dragging");
      if (reduce || Math.abs(vx) < .05 || performance.now() - lt > 80){ release(); return; }
      let v = vx * 16;  /* px per frame */
      const step = () => { el.scrollLeft -= v; v *= .93;
        if (Math.abs(v) > .5) raf = requestAnimationFrame(step); else release(); };
      raf = requestAnimationFrame(step);
    };
    addEventListener("pointerup", end); addEventListener("pointercancel", end); addEventListener("blur", end);
    el.addEventListener("click", e => { if (moved){ e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    el.addEventListener("dragstart", e => e.preventDefault());
    el.addEventListener("wheel", () => cancelAnimationFrame(raf), {passive:true});
  }
  const scan = () => document.querySelectorAll("[data-drag]").forEach(bind);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scan); else scan();
  window.dragScroll = bind;
})();
