import { api } from "../api.js";
import { esc, flagImg, fmtDateLong, fmtTime, ballIcon } from "../util.js";
import { standingsTable } from "../components.js";

const minuteNum = (m) => parseInt(String(m).replace("+", ""), 10) || 0;

function timeline(m) {
  if (m.status !== "finished") {
    return emptyTab("Not started", `Kick-off ${fmtDateLong(m.kickoff_utc)} · ${fmtTime(m.kickoff_utc)}. The goal timeline appears once the match is played.`);
  }
  const events = [
    ...m.goals1.map((g) => ({ ...g, side: 1 })),
    ...m.goals2.map((g) => ({ ...g, side: 2 })),
  ].sort((a, b) => minuteNum(a.minute) - minuteNum(b.minute));

  if (!events.length) return `<p class="notice">No goals in this match.</p>`;

  return `<div class="timeline">${events.map((e) => {
    const cell = `<span class="tl-ev ${e.side === 2 ? "right" : ""}">${ballIcon("tl-ball")}<span><span class="kind">Goal</span><br><span class="who">${esc(e.name)}</span></span></span>`;
    const left = e.side === 1 ? cell : "<span></span>";
    const right = e.side === 2 ? cell : "<span></span>";
    return `<div class="tl-row">${left}<span class="tl-min">${esc(e.minute)}'</span>${right}</div>`;
  }).join("")}</div>`;
}

function tableTab(m) {
  if (!m.group || !m.table) {
    return emptyTab("Knockout match", "Group tables apply to the group stage only.");
  }
  const rows = m.table.map((r) => ({ ...r, _hl: r.team === m.team1 || r.team === m.team2 }));
  return `<div class="eyebrow" style="margin-bottom:10px">${esc(m.group)}</div>${standingsTable(rows, { link: true })}`;
}

function emptyTab(title, body) {
  return `<div class="empty"><h3>${esc(title)}</h3><p>${esc(body)}</p></div>`;
}

function lineupsTab() {
  return emptyTab("Lineups not available", "The free data source doesn’t include lineups. Enable a keyed live source (see README) to light this up — no UI changes needed.");
}
function statsTab() {
  return emptyTab("Match stats not available", "Possession, shots and xG come from a keyed live source. The layout is ready for them.");
}

export async function render(root, params) {
  const id = parseInt(params[0], 10);
  const m = await api.match(id);

  const fin = m.status === "finished";
  const score = fin
    ? `<div class="scorebug__score">${m.score.ft[0]} <span style="opacity:.35">–</span> ${m.score.ft[1]}</div>`
    : `<div class="scorebug__score" style="font-size:2rem">vs</div>`;
  const state = fin ? "Full time" : `${fmtTime(m.kickoff_utc)}`;
  const stage = m.group || m.round || "";

  root.innerHTML = `
    <a class="back-link" href="#/matches"><span aria-hidden="true">←</span> All matches</a>
    <div class="eyebrow" style="text-align:center">${esc(stage)}</div>
    <div class="scorebug">
      <div class="scorebug__team">${flagImg(m.flag1, m.team1, "flag--xl")}<span class="name">${esc(m.team1)}</span></div>
      <div class="scorebug__mid">${score}<div class="scorebug__state">${esc(state)}</div></div>
      <div class="scorebug__team">${flagImg(m.flag2, m.team2, "flag--xl")}<span class="name">${esc(m.team2)}</span></div>
    </div>
    <div class="match-meta">${esc(fmtDateLong(m.kickoff_utc))}${m.ground ? " · " + esc(m.ground) : ""}</div>

    <div class="tabs" id="tabs">
      <button data-tab="timeline" class="is-active">Timeline</button>
      <button data-tab="lineups">Lineups</button>
      <button data-tab="stats">Stats</button>
      <button data-tab="table">Table</button>
    </div>
    <div id="tabpanel"></div>`;

  const panel = root.querySelector("#tabpanel");
  const render_tab = (tab) => {
    panel.innerHTML =
      tab === "timeline" ? timeline(m)
      : tab === "lineups" ? lineupsTab()
      : tab === "stats" ? statsTab()
      : tableTab(m);
  };
  render_tab("timeline");

  root.querySelector("#tabs").addEventListener("click", (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;
    root.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("is-active", b === btn));
    render_tab(btn.dataset.tab);
  });
}
