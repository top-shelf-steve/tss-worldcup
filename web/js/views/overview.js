import { api } from "../api.js";
import { esc, flagImg, fmtDate, fmtTime, outcome } from "../util.js";

function nextCard(m) {
  const label = m.group || m.round || "";
  return `
    <a class="mcard" href="#/match/${m.id}">
      <div class="mcard__top">
        <div class="grp">${esc(label)}</div>
        <div class="when">${esc(fmtDate(m.kickoff_utc))} · ${esc(fmtTime(m.kickoff_utc))}</div>
      </div>
      <div class="mcard__teams">
        <div class="mteam"><span class="name" style="display:flex;align-items:center;gap:11px">${flagImg(m.flag1, m.team1, "flag--lg")}${esc(m.team1)}</span></div>
        <div class="mcard__vs">vs</div>
        <div class="mteam"><span class="name" style="display:flex;align-items:center;gap:11px">${flagImg(m.flag2, m.team2, "flag--lg")}${esc(m.team2)}</span></div>
      </div>
      <div class="mcard__ground">${esc(m.ground || "")}</div>
    </a>`;
}

function spotlightResult(f, name) {
  const isHome = f.team1 === name;
  const opp = isHome ? f.team2 : f.team1;
  const oppFlag = isHome ? f.flag2 : f.flag1;
  const [a, b] = f.score.ft;
  const me = isHome ? a : b, them = isHome ? b : a;
  const o = outcome(f, name);
  return `
    <a class="mini" href="#/match/${f.id}">
      <span class="badge-wl ${o}">${o}</span>
      <span class="opp">${flagImg(oppFlag, opp)}${esc(opp)}</span>
      <span class="res">${me}<span style="opacity:.4">–</span>${them}</span>
    </a>`;
}

function spotlightFixture(f, name) {
  const isHome = f.team1 === name;
  const opp = isHome ? f.team2 : f.team1;
  const oppFlag = isHome ? f.flag2 : f.flag1;
  return `
    <a class="mini" href="#/match/${f.id}">
      <span class="opp">${flagImg(oppFlag, opp)}${esc(opp)}</span>
      <span class="res"><small>${esc(fmtDate(f.kickoff_utc))}</small>${esc(fmtTime(f.kickoff_utc))}</span>
    </a>`;
}

function spotlight(t) {
  if (!t) return "";
  const stand = t.standing
    ? `${ordinal(t.standing.rank)} · ${esc(t.standing.group)} · ${t.standing.pts} pts`
    : "Group stage";
  const results = (t.results || []).slice(-3).reverse();
  const fixtures = (t.fixtures || []).slice(0, 3);
  return `
    <div class="section-head"><h2 class="h-section">Team USA</h2>
      <a class="more" href="#/team/${esc(t.slug)}">Full schedule →</a></div>
    <div class="spotlight">
      <div class="spotlight__lede">
        <div class="eyebrow">${t.is_host ? "Co-host nation" : "Spotlight"}</div>
        <div class="who">${flagImg(t.flag, t.name, "flag--xl")}<span class="name">${esc(t.name)}</span></div>
        <div class="standing">${stand}</div>
      </div>
      <div>
        <div class="eyebrow">Recent results</div>
        <div class="mini-list">${results.length ? results.map((f) => spotlightResult(f, t.name)).join("") : '<span class="notice">No matches played yet.</span>'}</div>
      </div>
      <div>
        <div class="eyebrow">Upcoming</div>
        <div class="mini-list">${fixtures.length ? fixtures.map((f) => spotlightFixture(f, t.name)).join("") : '<span class="notice">Schedule complete.</span>'}</div>
      </div>
    </div>`;
}

function ordinal(n) {
  const s = ["th", "st", "nd", "rd"], v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

export async function render(root) {
  const d = await api.overview();
  const pins = d.host_pins.map((p) =>
    `<span class="pin" style="left:${p.x}%;top:${p.y}%;background:${p.color};color:${p.color}" title="${esc(p.country)}"></span>`
  ).join("");
  const cards = d.next_matches.slice(0, 4).map(nextCard).join("");

  root.innerHTML = `
    <section class="hero">
      <div>
        <div class="eyebrow">FIFA World Cup · ${esc(d.tournament.dates)}</div>
        <h1 class="display">World Cup<br>2026</h1>
        <div class="hero__meta">
          <div class="dates">${esc(d.tournament.dates)}</div>
          <div>${esc(d.tournament.hosts)}</div>
        </div>
        <a class="hero__cta" href="#/matches">Explore tournament <span aria-hidden="true">→</span></a>
      </div>
      <div class="worldmap">
        <img class="worldmap__dots" src="assets/world-dots.svg" alt="" aria-hidden="true" />
        ${pins}
      </div>
    </section>

    <div class="section-head"><h2 class="h-section">Next matches</h2>
      <a class="more" href="#/matches">All matches →</a></div>
    <div class="card-row">${cards || '<p class="notice">No upcoming matches.</p>'}</div>

    ${spotlight(d.featured)}`;
}
