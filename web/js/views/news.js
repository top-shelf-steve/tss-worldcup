import { api } from "../api.js";
import { esc } from "../util.js";

// "3h ago" / "2d ago" from an RFC-822 pubDate string.
function relative(pub) {
  const d = pub ? new Date(pub) : null;
  if (!d || isNaN(d)) return "";
  const mins = Math.round((Date.now() - d.getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
}

export async function render(root) {
  const { items } = await api.news();

  if (!items || !items.length) {
    root.innerHTML = `
      <div class="section-head"><h1 class="h-section">News</h1></div>
      <div class="empty">
        <h3>No headlines right now</h3>
        <p>The news feed didn’t return anything this build. It refreshes
        automatically on the next rebuild.</p>
      </div>`;
    return;
  }

  const list = items.map((it) => {
    const meta = [it.source, relative(it.published)].filter(Boolean).join(" · ");
    return `
      <a class="news-item" href="${esc(it.link)}" target="_blank" rel="noopener noreferrer">
        <span class="news-item__title">${esc(it.title)}</span>
        ${meta ? `<span class="news-item__meta">${esc(meta)}</span>` : ""}
      </a>`;
  }).join("");

  root.innerHTML = `
    <div class="section-head"><h1 class="h-section">News</h1>
      <span class="more">Latest headlines</span></div>
    <div class="news-list">${list}</div>
    <p class="notice" style="margin-top:18px">Headlines from an external news feed — links open on the publisher’s site.</p>`;
}
