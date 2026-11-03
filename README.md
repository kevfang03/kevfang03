<p align="center">
  <img src="https://raw.githubusercontent.com/kevfang03/kevfang03/output/sky-islands.svg" width="100%"
       alt="Sky islands: an animated archipelago of floating islands, with a train looping past a town where each of my repositories is a building">
</p>

## Sky islands

An animated banner that grows with my GitHub activity, redrawn every hour from my public stats
and the time of day in Philadelphia. Hand-built SVG from Python, no images.

- Each public repo is a building that upgrades with its commits; the newest one is under
  construction.
- Islands unlock as I level up: the city, the stadium, then Starport and Sky Shrine at
  levels 6 and 8.
- The sky train gains coaches, cargo and an observation dome as I level up, and
  carries wheat, wood, stone and crystals earned from my stats.
- A companion that evolves at levels 5 and 10, a dragon flyover on a 7-day streak,
  and a starfighter squadron for merged pull requests.

<sub>Draw it yourself: <code>uv run python -m sky_islands demo --phase dusk</code>, or
<code>live --login &lt;you&gt;</code> with a <code>GITHUB_TOKEN</code> set.
The rules are in <a href="docs/DESIGN.md">docs/DESIGN.md</a>.</sub>
