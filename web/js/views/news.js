export async function render(root) {
  root.innerHTML = `
    <div class="section-head"><h1 class="h-section">News</h1></div>
    <div class="empty">
      <h3>No news feed connected</h3>
      <p>News isn’t part of the free results feed. Point this at an RSS source or
      a keyed news API to populate it — kept as a deliberate placeholder so the
      navigation matches the full design.</p>
    </div>`;
}
