import { api } from "../api.js";
import { esc, flagImg } from "../util.js";
import { standingsTable, matchLine } from "../components.js";

export async function render(root, params) {
  const slug = params[0];
  const [t, groupsData] = await Promise.all([api.team(slug), api.groups()]);

  const groupName = t.standing ? t.standing.group : null;
  const groupBlock = groupName
    ? (() => {
        const g = groupsData.groups.find((x) => x.group === groupName);
        const rows = g.table.map((r) => ({ ...r, _hl: r.team === t.name }));
        return `<div class="section-head"><h2 class="h-section">${esc(groupName)}</h2></div>${standingsTable(rows, { link: true })}`;
      })()
    : "";

  const results = (t.results || []).slice().reverse();
  const subhead = [t.confederation, groupName, t.is_host ? "Co-host" : null]
    .filter(Boolean).join(" · ");

  root.innerHTML = `
    <a class="back-link" href="#/teams"><span aria-hidden="true">←</span> All teams</a>
    <div class="scorebug__team" style="flex-direction:row;justify-content:flex-start;gap:18px;align-items:center">
      ${flagImg(t.flag, t.name, "flag--xl")}
      <div>
        <h1 class="display" style="font-size:clamp(2rem,6vw,3.4rem)">${esc(t.name)}</h1>
        <div class="eyebrow" style="margin-top:8px">${esc(subhead)}</div>
      </div>
    </div>

    ${groupBlock}

    <div class="section-head"><h2 class="h-section">Results</h2></div>
    ${results.length ? results.map(matchLine).join("") : '<p class="notice">No matches played yet.</p>'}

    <div class="section-head"><h2 class="h-section">Upcoming</h2></div>
    ${t.fixtures.length ? t.fixtures.map(matchLine).join("") : '<p class="notice">No upcoming fixtures.</p>'}`;
}
