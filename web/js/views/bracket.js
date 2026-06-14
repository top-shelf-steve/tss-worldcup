import { api } from "../api.js";
import { esc, flagImg } from "../util.js";

function slotRow(slot, score, isWinner, isLoser) {
  const name = slot.resolved ? slot.name : slot.label;
  const flag = slot.resolved ? flagImg(slot.flag, slot.name) : `<span class="flag--ph"></span>`;
  const cls = isWinner ? "win" : isLoser ? "lose" : "";
  return `<div class="brow ${cls}">${flag}<span class="name ${slot.resolved ? "" : "ph"}">${esc(name)}</span>${score !== null ? `<span class="sc">${score}</span>` : ""}</div>`;
}

function node(m) {
  const fin = m.score && m.winner;
  const s1 = m.score ? m.score.ft[0] : null;
  const s2 = m.score ? m.score.ft[1] : null;
  return `
    <a class="bnode" href="#/match/${m.id}" style="text-decoration:none">
      <div class="bnode__num">M${m.id}</div>
      ${slotRow(m.team1, s1, fin && m.winner === 1, fin && m.winner === 2)}
      ${slotRow(m.team2, s2, fin && m.winner === 2, fin && m.winner === 1)}
    </a>`;
}

export async function render(root) {
  const b = await api.bracket();
  const columns = b.columns.map((col) => `
    <div class="bcol">
      <div class="bcol__title">${esc(col.title)}</div>
      ${col.matches.map(node).join("")}
    </div>`).join("");

  const third = b.third_place ? `
    <div class="section-head" style="margin-top:48px"><h2 class="h-section">Third-place play-off</h2></div>
    <div style="max-width:240px">${node(b.third_place)}</div>` : "";

  root.innerHTML = `
    <div class="section-head"><h1 class="h-section">Knockout bracket</h1>
      <a class="more" href="#/matches">← Back to matches</a></div>
    <div class="bracket-scroll"><div class="bracket">${columns}</div></div>
    ${third}`;
}
