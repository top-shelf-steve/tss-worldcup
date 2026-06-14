import { api } from "../api.js";
import { esc, flagImg } from "../util.js";

function totalsStrip(t) {
  const bw = t.biggest_win;
  const bwTeam = bw ? (bw.score[0] >= bw.score[1] ? bw.team1 : bw.team2) : null;
  return `
    <div class="stat-strip">
      <div class="stat"><div class="stat__n">${t.goals}</div><div class="stat__l">Goals</div></div>
      <div class="stat"><div class="stat__n">${t.matches_played}</div><div class="stat__l">Matches played</div></div>
      <div class="stat"><div class="stat__n">${t.avg_goals.toFixed(2)}</div><div class="stat__l">Goals / match</div></div>
      ${bw ? `<div class="stat"><div class="stat__n">${bw.score[0]}–${bw.score[1]}</div><div class="stat__l">Biggest win · ${esc(bwTeam)}</div></div>`
           : `<div class="stat"><div class="stat__n">—</div><div class="stat__l">Biggest win</div></div>`}
    </div>`;
}

function scorerTable(scorers) {
  if (!scorers.length) {
    return `<p class="notice">No goals scored yet — the chart fills in as matches are played.</p>`;
  }
  const rows = scorers.map((s, i) => `
    <tr>
      <td class="t-rank">${i + 1}</td>
      <td class="t-team"><a href="#/team/${slug(s.team)}">${flagImg(s.flag, s.team)}<span>${esc(s.name)}</span></a></td>
      <td class="s-team">${esc(s.team)}</td>
      <td class="t-pts">${s.goals}${s.pens ? `<span class="s-pen"> (${s.pens} pen)</span>` : ""}</td>
    </tr>`).join("");
  return `<table class="standtable scorer-table">
    <thead><tr><th class="t-rank">#</th><th class="t-team">Player</th><th class="s-team">Team</th><th class="t-pts">Goals</th></tr></thead>
    <tbody>${rows}</tbody></table>`;
}

function slug(name) {
  return name.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export async function render(root) {
  const s = await api.stats();
  root.innerHTML = `
    <div class="section-head"><h1 class="h-section">Stats</h1></div>
    ${totalsStrip(s.totals)}
    <div class="section-head"><h2 class="h-section">Top scorers</h2></div>
    ${scorerTable(s.scorers)}
    <p class="notice" style="margin-top:18px">Computed from goal data in the schedule feed. Own goals are excluded; penalties count.</p>`;
}
