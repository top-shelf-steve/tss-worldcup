export async function render(root) {
  root.innerHTML = `
    <div class="section-head"><h1 class="h-section">Stats</h1></div>
    <div class="empty">
      <h3>Tournament stats coming with live data</h3>
      <p>Top scorers, possession, xG and shot maps come from a keyed live source.
      This tracker ships on the free, no-key feed; wire up a keyed source
      (see the README) and this section fills in automatically — the layout is
      already built for it.</p>
    </div>`;
}
