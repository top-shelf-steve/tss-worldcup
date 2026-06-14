import { api } from "../api.js";
import { matchDayGroups } from "../components.js";

const FILTERS = [
  { key: "all", label: "All" },
  { key: "group", label: "Groups" },
  { key: "r32", label: "Round of 32" },
  { key: "r16", label: "Round of 16" },
  { key: "qf", label: "Quarter-finals" },
  { key: "sf", label: "Semi-finals" },
  { key: "final", label: "Final" },
];

export async function render(root) {
  const { matches } = await api.matches();

  root.innerHTML = `
    <div class="section-head"><h1 class="h-section">Matches</h1>
      <a class="more" href="#/bracket">Knockout bracket →</a></div>
    <div class="pill-row" id="mfilters" style="margin-bottom:22px">
      ${FILTERS.map((f, i) => `<button class="pill ${i === 0 ? "is-active" : ""}" data-key="${f.key}">${f.label}</button>`).join("")}
    </div>
    <div id="mlist"></div>`;

  const list = root.querySelector("#mlist");
  const draw = (key) => {
    const rows = key === "all" ? matches : matches.filter((m) => m.stage === key || (key === "group" && m.group));
    list.innerHTML = rows.length ? matchDayGroups(rows) : `<p class="notice">No matches in this round yet.</p>`;
  };
  draw("all");

  root.querySelector("#mfilters").addEventListener("click", (e) => {
    const btn = e.target.closest(".pill");
    if (!btn) return;
    root.querySelectorAll("#mfilters .pill").forEach((p) => p.classList.toggle("is-active", p === btn));
    draw(btn.dataset.key);
  });
}
