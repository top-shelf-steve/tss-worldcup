import { api } from "../api.js";
import { esc } from "../util.js";
import { standingsTable, matchLine } from "../components.js";

export async function render(root) {
  const { groups } = await api.groups();

  const blocks = groups.map((g) => `
    <div class="group-block">
      <h3>${esc(g.group)}</h3>
      ${standingsTable(g.table, { link: true })}
      <div style="margin-top:14px">${g.fixtures.map(matchLine).join("")}</div>
    </div>`).join("");

  root.innerHTML = `
    <div class="section-head"><h1 class="h-section">Groups</h1>
      <span class="more">Top 2 of each group advance, plus 8 best third-placed</span></div>
    <div class="groups-grid">${blocks}</div>`;
}
