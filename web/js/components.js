// Reusable bits shared across views.
import { esc, flagImg, fmtTime, fmtDate, dayKey } from "./util.js";

// A single clickable match row used by Matches, Groups fixtures, Team pages.
export function matchLine(m) {
  const fin = m.status === "finished";
  const a = m.score ? m.score.ft[0] : null;
  const b = m.score ? m.score.ft[1] : null;
  const loseL = fin && m.winner === 2;
  const loseR = fin && m.winner === 1;
  const label = m.group ? m.group.replace("Group ", "Grp ") : (m.round || "");
  const score = fin
    ? `<span class="score">${a}<span style="opacity:.4"> – </span>${b}</span>`
    : `<span class="score vs">vs</span>`;
  return `
    <a class="match-line" href="#/match/${m.id}">
      <span class="when">${esc(fmtTime(m.kickoff_utc) || "")}<span class="grp">${esc(label)}</span></span>
      <span class="side ${loseL ? "lose" : ""}">${flagImg(m.flag1, m.team1)}<span class="name">${esc(m.team1)}</span></span>
      ${score}
      <span class="side right ${loseR ? "lose" : ""}">${flagImg(m.flag2, m.team2)}<span class="name">${esc(m.team2)}</span></span>
      <span class="chev">›</span>
    </a>`;
}

// Group a flat list of matches into dated sections, newest grouping order preserved.
export function matchDayGroups(list) {
  const order = [];
  const byDay = new Map();
  for (const m of list) {
    const key = dayKey(m.kickoff_utc, m.date);
    if (!byDay.has(key)) { byDay.set(key, []); order.push(key); }
    byDay.get(key).push(m);
  }
  return order.map((key) => {
    const rows = byDay.get(key).map(matchLine).join("");
    const heading = fmtDate(byDay.get(key)[0].kickoff_utc) || key;
    return `<div class="daygroup"><div class="daygroup__date">${esc(heading)}</div>${rows}</div>`;
  }).join("");
}

// Standings table. opts: { link } to make team names link to their page.
export function standingsTable(rows, opts = {}) {
  const head = `
    <tr>
      <th class="t-rank">#</th><th class="t-team">Team</th>
      <th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th class="t-pts">Pts</th>
    </tr>`;
  const body = rows.map((r) => {
    const name = opts.link
      ? `<a href="#/team/${slugFor(r.team, opts)}">${flagImg(r.flag, r.team)}<span>${esc(r.team)}</span></a>`
      : `<span style="display:inline-flex;align-items:center;gap:11px;font-weight:600">${flagImg(r.flag, r.team)}<span>${esc(r.team)}</span></span>`;
    const qual = r.rank <= 2 ? "qual" : "";
    const hl = r._hl ? "hl" : "";
    const gd = r.gd > 0 ? `+${r.gd}` : r.gd;
    return `
      <tr class="${qual} ${hl}">
        <td class="t-rank">${r.rank}</td>
        <td class="t-team">${name}</td>
        <td>${r.p}</td><td>${r.w}</td><td>${r.d}</td><td>${r.l}</td>
        <td>${gd}</td><td class="t-pts">${r.pts}</td>
      </tr>`;
  }).join("");
  return `<table class="standtable"><thead>${head}</thead><tbody>${body}</tbody></table>`;
}

// teams payload carries slugs; for standings we may not have them, so derive.
function slugFor(name) {
  return name.toLowerCase()
    .normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}
