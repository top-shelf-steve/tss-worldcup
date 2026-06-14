import { api } from "../api.js";
import { esc, flagImg } from "../util.js";

export async function render(root) {
  const { teams, confederations } = await api.teams();

  const pills = [`<button class="pill is-active" data-conf="all">All (${teams.length})</button>`]
    .concat(confederations.map((c) => `<button class="pill" data-conf="${c}">${c}</button>`)).join("");

  root.innerHTML = `
    <div class="section-head"><h1 class="h-section">Teams</h1></div>
    <div class="teams-toolbar">
      <label class="search">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
        <input id="team-search" type="search" placeholder="Search teams" autocomplete="off" />
      </label>
      <div class="pill-row" id="conf-pills">${pills}</div>
    </div>
    <div class="team-grid" id="team-grid"></div>`;

  const grid = root.querySelector("#team-grid");
  let conf = "all", q = "";

  const draw = () => {
    const rows = teams.filter((t) =>
      (conf === "all" || t.confederation === conf) &&
      (!q || t.name.toLowerCase().includes(q))
    );
    grid.innerHTML = rows.length ? rows.map((t) => `
      <a class="team-cell" href="#/team/${esc(t.slug)}">
        ${flagImg(t.flag, t.name)}
        <span class="name">${esc(t.name)}</span>
        <span class="grp">${esc(t.group || "")}</span>
      </a>`).join("") : `<p class="notice" style="grid-column:1/-1">No teams match.</p>`;
  };
  draw();

  root.querySelector("#conf-pills").addEventListener("click", (e) => {
    const btn = e.target.closest(".pill");
    if (!btn) return;
    conf = btn.dataset.conf;
    root.querySelectorAll("#conf-pills .pill").forEach((p) => p.classList.toggle("is-active", p === btn));
    draw();
  });
  root.querySelector("#team-search").addEventListener("input", (e) => {
    q = e.target.value.trim().toLowerCase();
    draw();
  });
}
