"""Render predictions as one self-contained HTML page (no server, no CDN)."""

from __future__ import annotations

import json

import pandas as pd

PLAYER_FIELDS = [
    "name", "web_name", "team", "position", "opponent", "price", "expected_points",
    "model_points", "availability", "status", "chance", "news", "form_5gw",
    "last_gw_points", "fpl_ep_next", "owned_pct", "set_pieces",
]  # fmt: skip


def _records(frame: pd.DataFrame, fields: list[str]) -> list[dict]:
    clean = frame[fields].astype(object).where(frame[fields].notna(), None)
    return clean.to_dict("records")


def render_dashboard(
    predictions: pd.DataFrame, squad: pd.DataFrame, meta: dict, track: dict | None = None
) -> str:
    """Return the dashboard HTML for one Gameweek."""
    xi = squad[squad["in_xi"]]
    bench = squad[~squad["in_xi"]].sort_values("bench_order")
    fields = ["web_name", "team", "position", "opponent", "expected_points"]
    xi_rows = _records(xi, fields)
    payload = {
        "meta": meta,
        "track": track,
        "players": _records(predictions, PLAYER_FIELDS),
        "xi": [
            {**row, "captain": bool(c), "vice": bool(v)}
            for row, c, v in zip(xi_rows, xi["captain"], xi["vice_captain"], strict=True)
        ],
        "bench": _records(bench, fields),
    }
    data = json.dumps(payload, allow_nan=False, default=float).replace("</", "<\\/")
    return TEMPLATE.replace("__DATA__", data).replace("__TITLE__", f"GW{meta['gameweek']}")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>FPL AI — __TITLE__ predictions</title>
<style>
:root {
  --bg:#f6f7f9; --card:#fff; --text:#16181d; --muted:#667085; --line:#e4e7ec;
  --accent:#5b3df5; --accent-soft:#ece9fe; --good:#12805c; --warn:#b54708; --bad:#b42318;
  box-sizing:border-box;
  padding-top:env(safe-area-inset-top,0px); padding-bottom:env(safe-area-inset-bottom,0px);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg:#101218; --card:#181b23; --text:#eceef3; --muted:#9aa3b2; --line:#2a2f3a;
    --accent:#9b8cff; --accent-soft:#25223f; --good:#4cd6a0; --warn:#f5b45f; --bad:#ff8a80;
  }
}
:root[data-theme="dark"] {
  --bg:#101218; --card:#181b23; --text:#eceef3; --muted:#9aa3b2; --line:#2a2f3a;
  --accent:#9b8cff; --accent-soft:#25223f; --good:#4cd6a0; --warn:#f5b45f; --bad:#ff8a80;
}
* { box-sizing:border-box; }
html { scroll-padding-top:env(safe-area-inset-top,0px); }
body { margin:0; background:var(--bg); color:var(--text);
  font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
main { max-width:1100px; margin:0 auto; padding:20px 16px 48px; }
h1 { font-size:24px; margin:0 0 4px; }
h2 { font-size:17px; margin:28px 0 10px; }
.sub { color:var(--muted); font-size:13px; }
.banner { margin:14px 0 0; padding:10px 14px; border-radius:10px; font-size:14px;
  background:var(--accent-soft); border:1px solid var(--line); }
.banner.warn { color:var(--warn); }
.cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px; }
.card .rank { color:var(--muted); font-size:12px; }
.card .nm { font-weight:650; font-size:17px; }
.card .pts { font-size:26px; font-weight:700; color:var(--accent); }
.pitch { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px; }
.line { display:flex; justify-content:center; flex-wrap:wrap; gap:10px; margin:8px 0; }
.chip { min-width:104px; text-align:center; padding:8px 10px; border-radius:10px;
  border:1px solid var(--line); background:var(--bg); }
.chip b { display:block; font-size:14px; }
.chip span { font-size:12px; color:var(--muted); }
.chip em { font-style:normal; font-weight:700; color:var(--accent); font-size:13px; }
.chip .badge, .badge { display:inline-block; font-size:11px; font-weight:700; padding:1px 6px; border-radius:99px;
  background:var(--accent); color:#fff; margin-left:4px; }
.chip .badge { color:#fff; font-size:11px; }
.bench { margin-top:10px; padding-top:10px; border-top:1px dashed var(--line); }
.controls { display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 12px; align-items:center; }
input,select { padding:8px 10px; border-radius:8px; border:1px solid var(--line);
  background:var(--card); color:var(--text); font:inherit; }
label.chk { font-size:14px; color:var(--muted); display:flex; gap:6px; align-items:center; }
.tablewrap { overflow-x:auto; background:var(--card); border:1px solid var(--line);
  border-radius:12px; }
table { border-collapse:collapse; width:100%; min-width:900px; }
th,td { padding:8px 10px; text-align:left; border-bottom:1px solid var(--line); white-space:nowrap; }
th { font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted);
  cursor:pointer; user-select:none; position:sticky; top:0; background:var(--card); }
th.sorted::after { content:" ▼"; } th.sorted.asc::after { content:" ▲"; }
td.num,th.num { text-align:right; }
td.sp { color:var(--muted); font-size:13px; }
td.st { max-width:260px; overflow:hidden; text-overflow:ellipsis; }
.bar { display:inline-block; height:6px; border-radius:3px; background:var(--accent);
  margin-right:8px; vertical-align:middle; }
.pos { font-size:11px; font-weight:700; padding:2px 6px; border-radius:6px; background:var(--accent-soft); }
.st-ok { color:var(--good); } .st-doubt { color:var(--warn); } .st-out { color:var(--bad); }
.foot { margin-top:26px; font-size:12.5px; color:var(--muted); }
.more { margin:12px auto 0; display:block; padding:8px 16px; border-radius:8px; cursor:pointer;
  border:1px solid var(--line); background:var(--card); color:var(--text); font:inherit; }
</style>
</head>
<body>
<main>
  <h1 id="title"></h1>
  <div class="sub" id="subtitle"></div>
  <div id="banners"></div>

  <h2>Top captain picks</h2>
  <div class="cards" id="top"></div>

  <h2>Best XI under FPL rules</h2>
  <div class="pitch" id="xi"></div>
  <div class="sub" style="margin-top:6px">Ignores your current squad: it is the best 15 / XI
    from scratch within £100.0m, 3 players per club and the formation limits.</div>

  <div id="trackwrap" hidden>
    <h2>Track record <span class="sub" id="trackgws"></span></h2>
    <div class="tablewrap"><table style="min-width:520px"><thead><tr>
      <th>Predictor</th><th class="num">MAE</th><th class="num">Rank corr.</th>
      <th class="num">Top-10 pts</th><th class="num">Captain pts</th><th class="num">XI pts</th>
    </tr></thead><tbody id="track"></tbody></table></div>
    <div class="sub" style="margin-top:6px">Average over gameweeks already played, scored from the
      predictions saved before each deadline. "fpl_ep_next" is FPL's own expected-points figure.</div>
  </div>

  <h2>All players</h2>
  <div class="controls">
    <input id="q" type="search" placeholder="Search player or team">
    <select id="pos"><option value="">All positions</option><option>GK</option><option>DEF</option>
      <option>MID</option><option>FWD</option></select>
    <select id="team"><option value="">All teams</option></select>
    <label class="chk">Max price <input id="price" type="number" step="0.5" min="3.5" max="16"
      placeholder="any" style="width:80px"></label>
    <label class="chk"><input id="avail" type="checkbox"> Hide doubtful / out</label>
  </div>
  <div class="tablewrap"><table>
    <thead><tr id="head"></tr></thead><tbody id="rows"></tbody>
  </table></div>
  <button class="more" id="more" hidden>Show all players</button>

  <div class="foot">
    <b>Exp. pts</b> is the model's estimate of this Gameweek's points, multiplied by FPL's own
    chance-of-playing flag. <b>Model</b> is the estimate before that adjustment. The model is a
    gradient-boosted regressor on rolling form, minutes, fixture and team features; it beats
    simple form averages in backtests but football is noisy and predictions are not guarantees.
    Not affiliated with the Premier League or Fantasy Premier League.
  </div>
</main>
<script id="data" type="application/json">__DATA__</script>
<script>
(function () {
  var D = JSON.parse(document.getElementById("data").textContent);
  var meta = D.meta, P = D.players;
  var $ = function (id) { return document.getElementById(id); };
  var fmt = function (x, d) { return x == null ? "–" : Number(x).toFixed(d == null ? 1 : d); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g,
    function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); };

  $("title").textContent = "Gameweek " + meta.gameweek + " predictions";
  $("subtitle").textContent = meta.season + (meta.deadline ? " · deadline " + meta.deadline.replace("T", " ").replace("Z", " UTC") : "") +
    " · generated " + meta.generated_at +
    " · trained on " + meta.train_rows.toLocaleString() + " player-gameweeks";

  var banners = [];
  if (meta.note) banners.push(["warn", meta.note]);
  if (meta.history_through_gw == null) {
    banners.push(["warn", "No results from this season were available, so form uses previous seasons only."]);
  } else if (meta.gameweek - meta.history_through_gw > 1) {
    banners.push(["warn", "Form data stops at GW" + meta.history_through_gw + ", but these are predictions for GW" +
      meta.gameweek + ". Refresh the data (scripts/fetch_live.py) for up-to-date form."]);
  } else {
    banners.push(["", "Form data is up to date through GW" + meta.history_through_gw + "."]);
  }
  var flagged = P.filter(function (p) { return p.availability < 1 && p.model_points >= 3; })
    .slice(0, 6).map(function (p) {
      return p.web_name + " (" + (p.availability <= 0 ? "out" : Math.round(p.availability * 100) + "%") + ")"; });
  if (flagged.length) banners.push(["warn", "Strong picks with an availability flag, already discounted: " + flagged.join(", ") + "."]);
  $("banners").innerHTML = banners.map(function (b) {
    return '<div class="banner ' + b[0] + '">' + esc(b[1]) + "</div>"; }).join("");

  $("top").innerHTML = P.slice(0, 4).map(function (p, i) {
    return '<div class="card"><div class="rank">#' + (i + 1) + " · " + esc(p.position) + " · " + esc(p.team) +
      '</div><div class="nm">' + esc(p.web_name) + '</div><div class="pts">' + fmt(p.expected_points) +
      ' <span class="sub">pts</span></div><div class="sub">vs ' + esc(p.opponent) + " · £" + fmt(p.price) + "m</div></div>";
  }).join("");

  function chip(p) {
    return '<div class="chip"><b>' + esc(p.web_name) + (p.captain ? '<span class="badge">C</span>' : "") +
      (p.vice ? '<span class="badge" style="background:var(--muted)">V</span>' : "") + "</b><span>" +
      esc(p.team) + " · " + esc(p.opponent) + "</span><br><em>" + fmt(p.expected_points) + "</em></div>";
  }
  var html = ["GK", "DEF", "MID", "FWD"].map(function (pos) {
    return '<div class="line">' + D.xi.filter(function (p) { return p.position === pos; }).map(chip).join("") + "</div>";
  }).join("");
  html += '<div class="bench sub">Bench</div><div class="line">' + D.bench.map(chip).join("") + "</div>";
  $("xi").innerHTML = html;

  if (D.track && D.track.rows.length) {
    $("trackwrap").hidden = false;
    var gws = D.track.gameweeks;
    $("trackgws").textContent = "· GW" + gws[0] + (gws.length > 1 ? "–GW" + gws[gws.length - 1] : "") +
      " (" + gws.length + " scored)";
    $("track").innerHTML = D.track.rows.map(function (r) {
      return "<tr><td><b>" + esc(r.predictor) + '</b></td><td class="num">' + fmt(r.mae, 2) + '</td><td class="num">' +
        fmt(r.spearman, 2) + '</td><td class="num">' + fmt(r.top10_points) + '</td><td class="num">' +
        fmt(r.captain_points) + '</td><td class="num">' + fmt(r.xi_points) + "</td></tr>"; }).join("");
  }

  var teams = Array.from(new Set(P.map(function (p) { return p.team; }))).sort();
  $("team").innerHTML += teams.map(function (t) { return "<option>" + esc(t) + "</option>"; }).join("");

  var cols = [
    ["Player", "web_name", false], ["Pos", "position", false], ["Team", "team", false],
    ["Opp", "opponent", false], ["Price", "price", true], ["Own %", "owned_pct", true],
    ["Form (5 GW)", "form_5gw", true], ["FPL xP", "fpl_ep_next", true],
    ["Model", "model_points", true], ["Exp. pts", "expected_points", true],
    ["Set pieces", "set_pieces", false], ["Availability", "availability", false]
  ];
  var sortKey = "expected_points", asc = false, showAll = false, LIMIT = 100;
  $("head").innerHTML = cols.map(function (c) {
    return '<th data-k="' + c[1] + '" class="' + (c[2] ? "num" : "") + '">' + c[0] + "</th>"; }).join("");
  $("head").addEventListener("click", function (e) {
    var k = e.target.getAttribute("data-k"); if (!k) return;
    if (k === sortKey) asc = !asc; else { sortKey = k; asc = false; }
    draw();
  });

  function status(p) {
    if (p.availability >= 1) return '<span class="st-ok">Available</span>';
    var pct = p.availability <= 0 ? "Out" : Math.round(p.availability * 100) + "%";
    return '<span title="' + esc(p.news) + '" class="' + (p.availability <= 0 ? "st-out" : "st-doubt") + '">' +
      pct + (p.news ? " · " + esc(p.news) : "") + "</span>";
  }

  function draw() {
    var q = $("q").value.trim().toLowerCase(), pos = $("pos").value, team = $("team").value;
    var maxp = parseFloat($("price").value), hide = $("avail").checked;
    var rows = P.filter(function (p) {
      return (!q || (p.name + " " + p.web_name + " " + p.team).toLowerCase().indexOf(q) >= 0) &&
        (!pos || p.position === pos) && (!team || p.team === team) &&
        (isNaN(maxp) || p.price <= maxp) && (!hide || p.availability >= 1);
    });
    rows.sort(function (a, b) {
      var x = a[sortKey], y = b[sortKey];
      if (x == null) return 1; if (y == null) return -1;
      var r = typeof x === "string" ? x.localeCompare(y) : x - y;
      return asc ? r : -r;
    });
    var total = rows.length;
    if (!showAll) rows = rows.slice(0, LIMIT);
    var max = Math.max.apply(null, P.map(function (p) { return p.expected_points; })) || 1;
    $("rows").innerHTML = rows.map(function (p) {
      return "<tr><td><b>" + esc(p.web_name) + '</b></td><td><span class="pos">' + esc(p.position) + "</span></td><td>" +
        esc(p.team) + "</td><td>" + esc(p.opponent) + '</td><td class="num">£' + fmt(p.price) + "m</td>" +
        '<td class="num">' + fmt(p.owned_pct) + '%</td><td class="num">' + fmt(p.form_5gw) + '</td><td class="num">' +
        fmt(p.fpl_ep_next) + '</td><td class="num">' + fmt(p.model_points) + "</td>" +
        '<td class="num"><span class="bar" style="width:' + Math.round(p.expected_points / max * 60) + 'px"></span><b>' +
        fmt(p.expected_points) + '</b></td><td class="sp">' + esc(p.set_pieces) + '</td><td class="st">' + status(p) + "</td></tr>";
    }).join("") || '<tr><td colspan="12" class="sub">No players match.</td></tr>';
    Array.prototype.forEach.call($("head").children, function (th) {
      th.className = (th.className.replace(/ ?(sorted|asc)/g, "")) +
        (th.getAttribute("data-k") === sortKey ? " sorted" + (asc ? " asc" : "") : "");
    });
    $("more").hidden = showAll || total <= LIMIT;
    $("more").textContent = "Show all " + total + " players";
  }
  ["q", "pos", "team", "price", "avail"].forEach(function (id) {
    $(id).addEventListener("input", draw); });
  $("more").addEventListener("click", function () { showAll = true; draw(); });
  draw();
})();
</script>
</body>
</html>
"""
