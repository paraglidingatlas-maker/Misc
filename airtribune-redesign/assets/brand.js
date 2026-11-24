/* Airtribune concept: shared logo.
   FINAL: Heritage (logo study, direction No. 1), chosen by the owner on 24 Nov 2026.
   One red triangle + blue square from today's grid; lowercase wordmark with triangle tittles on the i's.
   Renders into: every a.logo, every [data-brand] ("" = lockup, "mark", "tile") and the favicon. */
(function () {
  "use strict";
  var RED = "#ED1C24", BLUE = "#00AEEF";

  function mark() {
    return '<svg class="atb-m" viewBox="0 0 40 40" aria-hidden="true" focusable="false">' +
      '<path d="M2 2h36v36z" fill="' + RED + '"/><rect x="2" y="20" width="16" height="16" fill="' + BLUE + '"/></svg>';
  }
  function word() {
    return '<b class="atb-w">' + "airtribune".replace(/i/g, '<span class="atb-tit">ı</span>') + "</b>";
  }
  function tile() { return '<span class="atb-tile">' + mark() + "</span>"; }
  function favicon() {
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">' + mark().replace(/^<svg[^>]*>|<\/svg>$/g, "") + "</svg>";
    return "data:image/svg+xml," + encodeURIComponent(svg);
  }

  var CSS =
    ".atb-lock{display:inline-flex;align-items:center;gap:.45em;line-height:1;white-space:nowrap;color:inherit}" +
    ".atb-m{display:block;flex:none;width:1.2em;height:1.2em}" +
    "a.logo .atb-m{width:26px;height:26px}" +
    "a.logo .atb-w,.atb-w{font-family:Archivo,var(--f-display,system-ui),sans-serif;font-weight:700;font-style:normal;text-transform:none;letter-spacing:-.01em;line-height:1;color:inherit}" +
    ".atb-tit{position:relative;display:inline-block}" +
    ".atb-tit::before{content:'';position:absolute;left:50%;top:-.02em;width:.3em;height:.3em;transform:translateX(-30%);background:" + RED + ";clip-path:polygon(0 0,100% 0,100% 100%)}" +
    ".atb-tile{display:grid;place-items:center;width:34px;height:34px;border-radius:8px;flex:none;background:#0B2630}" +
    ".atb-tile .atb-m{width:62%;height:62%}";

  function render() {
    var logos = document.querySelectorAll("a.logo");
    for (var i = 0; i < logos.length; i++) logos[i].innerHTML = mark() + word();
    var els = document.querySelectorAll("[data-brand]");
    for (var j = 0; j < els.length; j++) {
      var t = els[j].getAttribute("data-brand");
      els[j].innerHTML = t === "mark" ? mark() : t === "tile" ? tile() : '<span class="atb-lock">' + mark() + word() + "</span>";
    }
    var link = document.querySelector('link[rel="icon"]');
    if (!link) { link = document.createElement("link"); link.rel = "icon"; document.head.appendChild(link); }
    link.type = "image/svg+xml"; link.href = favicon();
  }

  function init() {
    var st = document.createElement("style"); st.textContent = CSS; document.head.appendChild(st);
    if (!document.querySelector('link[href*="family=Archivo"]')) {
      var f = document.createElement("link"); f.rel = "stylesheet";
      f.href = "https://fonts.googleapis.com/css2?family=Archivo:wght@700&display=swap";
      document.head.appendChild(f);
    }
    render();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
