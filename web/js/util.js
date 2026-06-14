// Small rendering helpers shared by every view.

export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

// flag-icons SVGs are vendored under assets/flags/<code>.svg.
export function flagImg(code, name, cls = "") {
  if (!code) return `<span class="flag--ph ${cls}" aria-hidden="true"></span>`;
  return `<img class="flag ${cls}" src="assets/flags/${code}.svg" alt="${esc(name || code)}" loading="lazy" width="20" height="15" />`;
}

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// kickoff_utc is ISO-8601 (Z); render in the viewer's own timezone.
function local(iso) { return iso ? new Date(iso) : null; }

export function fmtDate(iso) {
  const d = local(iso);
  if (!d) return "";
  return `${DOW[d.getDay()]} ${d.getDate()} ${MON[d.getMonth()]}`;
}
export function fmtDateLong(iso) {
  const d = local(iso);
  if (!d) return "";
  return `${DOW[d.getDay()]} ${d.getDate()} ${MON[d.getMonth()]} ${d.getFullYear()}`;
}
export function fmtTime(iso) {
  const d = local(iso);
  if (!d) return "";
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
// Stable YYYY-MM-DD key in local time, for grouping a schedule by day.
export function dayKey(iso, fallback) {
  const d = local(iso);
  if (!d) return fallback || "";
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function ballIcon(cls = "") {
  return `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="12" cy="12" r="9"/><path d="M12 7.5l3 2.2-1.1 3.5h-3.8L9 9.7 12 7.5z" fill="currentColor" stroke="none"/></svg>`;
}

// outcome letter for a team in a finished match: "W" | "L" | "D"
export function outcome(match, teamName) {
  if (!match.score) return "";
  const isHome = match.team1 === teamName;
  const [a, b] = match.score.ft;
  const me = isHome ? a : b, them = isHome ? b : a;
  return me > them ? "W" : me < them ? "L" : "D";
}

export function scrollTop() { window.scrollTo(0, 0); }
