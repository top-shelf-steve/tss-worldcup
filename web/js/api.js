// Fetch layer. Defaults to the Flask API; the static build injects
// window.__WC_API__ = { base: "data", ext: ".json" } to read flat files instead.
const CFG = window.__WC_API__ || { base: "/api", ext: "" };

const cache = new Map();

async function get(path) {
  const url = `${CFG.base}/${path}${CFG.ext}`;
  if (cache.has(url)) return cache.get(url);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  const data = await res.json();
  cache.set(url, data);
  return data;
}

export const api = {
  overview: () => get("overview"),
  matches: () => get("matches"),
  match: (id) => get(`match/${id}`),
  groups: () => get("groups"),
  teams: () => get("teams"),
  team: (slug) => get(`team/${slug}`),
  bracket: () => get("bracket"),
  stats: () => get("stats"),
  news: () => get("news"),
  status: () => get("status"),
};
