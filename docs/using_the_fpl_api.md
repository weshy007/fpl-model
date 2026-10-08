# Using the official FPL API

`https://fantasy.premierleague.com/api/bootstrap-static/` is the hub: one request returns
every player, team and Gameweek. Checked against the live payload on 8 Oct 2026
(GW5 finished, GW6 next, deadline 10 Oct 10:00 UTC, 20 teams, 616 players).

| Part of the payload | What it gives | How the project uses it |
|---|---|---|
| `events` | Every Gameweek with `deadline_time`, `is_next`, `is_current`, `finished` | **Done.** `is_next` picks the Gameweek to predict (more reliable than fixtures while a round is in progress); `finished` keeps half-played rounds out of the form features; the deadline is shown on the dashboard |
| `elements[].status`, `chance_of_playing_next_round`, `news` | Injury / suspension flags and news text | **Done.** Expected points are multiplied by the chance of playing (out = 0); news is shown in the table |
| `elements[].ep_next` | FPL's own expected points for the next Gameweek | **Done.** Shown as "FPL xP" and scored against the model in the track record: the honest test of whether the model adds anything |
| `elements[].penalties_order`, `corners_and_indirect_freekicks_order`, `direct_freekicks_order` | Designated set-piece takers | **Done (display only).** Not a model feature yet: there is no history to train on, see snapshots below |
| `elements[].now_cost`, `selected_by_percent` | Price and ownership | **Done.** Price feeds the squad optimiser; ownership is a sortable column (differentials = high expected points, low ownership) |
| `elements[]` season totals (`minutes`, `xG`, `bps`, ...) | Season-to-date stats | Not used: the model builds rolling form from per-Gameweek history instead |
| `element-summary/{id}/` | One player's Gameweek-by-Gameweek history | **Done.** `fetch_live.py` pulls it for every player to rebuild `merged_gw.csv` |
| `fixtures/` | All fixtures with kick-offs and results | **Done.** Opponent, home/away, double and blank Gameweeks |
| `teams` | Names, short names, strength ratings | Names and short names used; `strength_*` fields were still empty/default early in the season |
| `chips` | Which Gameweeks each chip can be played in | **Idea.** Pair with double-Gameweek detection to suggest Bench Boost / Triple Captain weeks |
| `scoring` | Current points rules | Informative: defensive-contribution points (new in 2025-26) change defender and midfielder scoring |
| `price_change_*`, `transfers_in_event` | Price-rise/fall projections and transfer momentum | **Idea.** Price-change alerts for the manager |

## Ideas not built yet

1. **Your own team.** `entry/{team_id}/event/{gw}/picks/` is public for finished Gameweeks; with your team id the dashboard could
   rank *your* transfers and captain instead of an anonymous best XI.
2. **Set-piece and availability features.** `fetch_live.py` now archives a timestamped copy of the player table on every run
   (`data/raw/<season>/snapshots/`). After a few Gameweeks that is the point-in-time history needed to train on injury flags,
   set-piece roles and ownership, which does not exist retroactively.
3. **Automation.** A scheduled GitHub Action that runs `fetch_live.py`, `predict_upcoming.py` and `score_gameweek.py` and publishes
   the dashboard to GitHub Pages (needs the track record persisted between runs).
4. **Multi-Gameweek planning.** Sum expected points over the next 3-5 Gameweeks for transfers and chip timing.
5. **Recency weighting.** Defensive-contribution points arrived in 2025-26. Extra form features for them did *not* help in a test
   (MAE 0.997 vs 0.985), but defenders were under-predicted by 0.135 points in 2025-26; weighting recent seasons more heavily is
   the next thing to try as 2026-27 data accumulates.

## Weekly routine

```bash
python scripts/fetch_live.py            # after the previous Gameweek is finished and checked
python scripts/score_gameweek.py        # grade last week's saved predictions (adds to the track record)
python scripts/predict_upcoming.py      # predict the next Gameweek; re-run just before the deadline for fresh news
```
