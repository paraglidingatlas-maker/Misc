/* Airtribune concept: shared logo.
   Two logos the owner can switch between with one click:
     thermal  – chosen mark: the four legacy triangles as a pinwheel (Thermal / Pinwheel),
                white centre square = the pilot; heavy italic uppercase wordmark.
     heritage – direction No. 1: one red triangle + blue square, lowercase wordmark with triangle tittles.
   The choice is remembered per browser (localStorage) and can be forced with ?logo=thermal or ?logo=1.
   Renders into: every a.logo, every [data-brand] ("" lockup, "mark", "tile"), the favicon,
   and a switch placed in [data-brand-switch], else the page's .concept bar, else a floating chip. */
(function () {
  "use strict";
  var KEY = "at-logo";
  var ORANGE = "#FF5F00", RED = "#ED1C24", BLUE = "#00AEEF", DEEP = "#051416";

  var MARK = {
    thermal: function (blade, pilot) {
      return '<svg class="atb-m" viewBox="0 0 40 40" aria-hidden="true" focusable="false"><g fill="' + blade + '">' +
        '<path d="M0 0H17.5V17.5Z"/><path d="M40 0V17.5H22.5Z"/><path d="M40 40H22.5V22.5Z"/><path d="M0 40V22.5H17.5Z"/></g>' +
        '<rect x="17.5" y="17.5" width="5" height="5" fill="' + pilot + '"/></svg>';
    },
    heritage: function (tri, sq) {
      return '<svg class="atb-m" viewBox="0 0 40 40" aria-hidden="true" focusable="false">' +
        '<path d="M2 2h36v36z" fill="' + tri + '"/><rect x="2" y="20" width="16" height="16" fill="' + sq + '"/></svg>';
    }
  };
  var LABEL = { thermal: "Thermal", heritage: "No. 1" };

  function word(k) {
    if (k === "thermal") return '<b class="atb-w atb-w-t">Airtribune</b>';
    var w = "airtribune".replace(/i/g, '<span class="atb-tit">ı</span>');
    return '<b class="atb-w atb-w-h">' + w + "</b>";
  }
  function mark(k) { return k === "thermal" ? MARK.thermal(ORANGE, "currentColor") : MARK.heritage(RED, BLUE); }
  function tile(k) {
    return k === "thermal"
      ? '<span class="atb-tile" style="background:' + ORANGE + '">' + MARK.thermal("#FFFFFF", DEEP) + "</span>"
      : '<span class="atb-tile" style="background:#0B2630">' + MARK.heritage(RED, BLUE) + "</span>";
  }
  function favicon(k) {
    var svg = k === "thermal"
      ? '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="' + ORANGE + '"/><g transform="translate(6 6) scale(.7)">' +
        MARK.thermal("#FFFFFF", DEEP).replace(/^<svg[^>]*>|<\/svg>$/g, "") + "</g></svg>"
      : '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">' + MARK.heritage(RED, BLUE).replace(/^<svg[^>]*>|<\/svg>$/g, "") + "</svg>";
    return "data:image/svg+xml," + encodeURIComponent(svg);
  }

  var CSS =
    ".atb-lock{display:inline-flex;align-items:center;gap:.45em;line-height:1;white-space:nowrap;color:inherit}" +
    ".atb-m{display:block;flex:none;width:1.2em;height:1.2em}" +
    "a.logo .atb-m{width:26px;height:26px}" +
    ".atb-w{font-family:Archivo,var(--f-display,system-ui),sans-serif;line-height:1;color:inherit}" +
    "a.logo .atb-w.atb-w-t,.atb-w.atb-w-t{font-weight:900;font-style:italic;text-transform:uppercase;letter-spacing:-.015em}" +
    "a.logo .atb-w.atb-w-h,.atb-w.atb-w-h{font-weight:700;font-style:normal;text-transform:none;letter-spacing:-.01em}" +
    ".atb-tit{position:relative;display:inline-block}" +
    ".atb-tit::before{content:'';position:absolute;left:50%;top:-.02em;width:.3em;height:.3em;transform:translateX(-30%);background:" + RED + ";clip-path:polygon(0 0,100% 0,100% 100%)}" +
    ".atb-tile{display:grid;place-items:center;width:34px;height:34px;border-radius:8px;flex:none}" +
    ".atb-tile .atb-m{width:62%;height:62%}" +
    ".atb-sw{display:inline-flex;align-items:center;gap:2px;margin-left:auto;padding:2px;border-radius:7px;background:rgba(127,127,127,.16);font:700 10px/1 Archivo,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap}" +
    ".atb-sw>span{padding:0 6px 0 7px;opacity:.7}" +
    ".atb-sw button{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:5px;color:inherit;opacity:.75}" +
    ".atb-sw button .atb-m{width:12px;height:12px}" +
    ".atb-sw button[aria-pressed=true]{background:#fff;color:#051416;opacity:1;box-shadow:0 1px 3px rgba(0,0,0,.25)}" +
    ".atb-sw button:focus-visible{outline:2px solid " + ORANGE + ";outline-offset:2px}" +
    ".atb-sw.float{position:fixed;left:12px;bottom:12px;z-index:200;background:rgba(5,20,22,.9);color:#fff;box-shadow:0 4px 18px rgba(0,0,0,.35)}";

  function current() {
    var q = new URLSearchParams(location.search).get("logo");
    if (q) { q = (q === "1" || q === "heritage") ? "heritage" : "thermal"; try { localStorage.setItem(KEY, q); } catch (e) {} return q; }
    try { var s = localStorage.getItem(KEY); if (s === "heritage" || s === "thermal") return s; } catch (e) {}
    return "thermal";
  }

  function render(k) {
    document.documentElement.setAttribute("data-logo", k);
    var logos = document.querySelectorAll("a.logo");
    for (var i = 0; i < logos.length; i++) logos[i].innerHTML = mark(k) + word(k);
    var els = document.querySelectorAll("[data-brand]");
    for (var j = 0; j < els.length; j++) {
      var t = els[j].getAttribute("data-brand");
      els[j].innerHTML = t === "mark" ? mark(k) : t === "tile" ? tile(k) : '<span class="atb-lock">' + mark(k) + word(k) + "</span>";
    }
    var link = document.querySelector('link[rel="icon"]');
    if (!link) { link = document.createElement("link"); link.rel = "icon"; document.head.appendChild(link); }
    link.type = "image/svg+xml"; link.href = favicon(k);
    var btns = document.querySelectorAll(".atb-sw button");
    for (var b = 0; b < btns.length; b++) btns[b].setAttribute("aria-pressed", String(btns[b].getAttribute("data-k") === k));
    document.dispatchEvent(new CustomEvent("brandchange", { detail: k }));
  }

  function set(k) { try { localStorage.setItem(KEY, k); } catch (e) {} render(k); }

  function addSwitch() {
    var sw = document.createElement("span");
    sw.className = "atb-sw"; sw.setAttribute("role", "group"); sw.setAttribute("aria-label", "Logo option");
    sw.innerHTML = "<span>Logo</span>" + ["thermal", "heritage"].map(function (k) {
      var m = k === "thermal" ? MARK.thermal(ORANGE, "currentColor") : MARK.heritage(RED, BLUE);
      return '<button type="button" data-k="' + k + '" aria-pressed="false">' + m + LABEL[k] + "</button>";
    }).join("");
    sw.addEventListener("click", function (e) { var b = e.target.closest("button[data-k]"); if (b) set(b.getAttribute("data-k")); });
    var host = document.querySelector("[data-brand-switch]") || document.querySelector(".concept .wrap") || document.querySelector(".concept");
    if (host) host.appendChild(sw); else { sw.classList.add("float"); document.body.appendChild(sw); }
  }

  function init() {
    var st = document.createElement("style"); st.textContent = CSS; document.head.appendChild(st);
    if (!document.querySelector('link[href*="family=Archivo"]')) {
      var f = document.createElement("link"); f.rel = "stylesheet";
      f.href = "https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,700;1,900&display=swap";
      document.head.appendChild(f);
    }
    addSwitch();
    render(current());
  }
  window.AirtribuneBrand = { set: set, get: current };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
