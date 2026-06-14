// Router + shared chrome (nav, dark mode, mobile menu).
import { api } from "./api.js";
import { scrollTop } from "./util.js";
import * as overview from "./views/overview.js";
import * as matches from "./views/matches.js";
import * as match from "./views/match.js";
import * as groups from "./views/groups.js";
import * as teams from "./views/teams.js";
import * as team from "./views/team.js";
import * as bracket from "./views/bracket.js";
import * as stats from "./views/stats.js";
import * as news from "./views/news.js";

const root = document.getElementById("app");

// route name -> { view, nav } where nav is the top-level tab to highlight
const ROUTES = {
  "": { view: overview, nav: "overview" },
  overview: { view: overview, nav: "overview" },
  matches: { view: matches, nav: "matches" },
  match: { view: match, nav: "matches" },
  bracket: { view: bracket, nav: "matches" },
  groups: { view: groups, nav: "groups" },
  teams: { view: teams, nav: "teams" },
  team: { view: team, nav: "teams" },
  stats: { view: stats, nav: "stats" },
  news: { view: news, nav: "news" },
};

function parseHash() {
  const raw = (location.hash || "#/").replace(/^#\/?/, "");
  const [name, ...rest] = raw.split("/");
  return { name, params: rest };
}

async function render() {
  const { name, params } = parseHash();
  const route = ROUTES[name] || ROUTES[""];
  setActiveNav(route.nav);
  closeMenu();
  root.innerHTML = `<div class="loading">Loading…</div>`;
  try {
    await route.view.render(root, params);
  } catch (err) {
    root.innerHTML = `<p class="notice">Couldn’t load this view — ${err.message}. The data may still be refreshing; try again in a moment.</p>`;
    console.error(err);
  }
  scrollTop();
}

function setActiveNav(nav) {
  document.querySelectorAll("#nav a").forEach((a) => {
    a.classList.toggle("is-active", a.dataset.route === nav);
  });
}

// --- dark mode -------------------------------------------------------------
const THEME_KEY = "wc-theme";
function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  document.getElementById("theme-toggle").innerHTML =
    t === "dark"
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M19 5l-1.5 1.5M6.5 17.5 5 19"/></svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.6 6.6 0 0 0 9.8 9.8z"/></svg>`;
}
function initTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  const t = saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  applyTheme(t);
  document.getElementById("theme-toggle").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  });
}

// --- mobile menu -----------------------------------------------------------
function closeMenu() {
  document.getElementById("nav").classList.remove("open");
  document.getElementById("menu-toggle").setAttribute("aria-expanded", "false");
}
function initMenu() {
  const btn = document.getElementById("menu-toggle");
  btn.addEventListener("click", () => {
    const nav = document.getElementById("nav");
    const open = nav.classList.toggle("open");
    btn.setAttribute("aria-expanded", String(open));
  });
}

// --- data freshness footer -------------------------------------------------
async function initStatus() {
  try {
    const s = await api.status();
    const el = document.getElementById("data-status");
    if (s.updated_at) {
      const when = new Date(s.updated_at).toLocaleString();
      el.textContent = `Data via ${s.source} · updated ${when}`;
    }
  } catch { /* offline / static: leave default text */ }
}

initTheme();
initMenu();
initStatus();
window.addEventListener("hashchange", render);
render();
