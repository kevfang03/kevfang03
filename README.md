<p align="center"><a href="https://github.com/kevfang03/kevfang03"><img src="https://raw.githubusercontent.com/kevfang03/kevfang03/output/sky-islands.svg" width="100%" alt="Sky islands: an animated archipelago of floating islands, with a train looping past a town where each of my repositories is a building"></a></p>

<p align="center">The sky follows the time in Philadelphia. Pick a time of day, or peek at level 10.</p>

<p align="center">
<a href="https://github.com/kevfang03/kevfang03/blob/main/views/dawn.md"><img src="assets/buttons/dawn.svg" alt="Dawn"></a>
<a href="https://github.com/kevfang03/kevfang03/blob/main/views/day.md"><img src="assets/buttons/day.svg" alt="Day"></a>
<a href="https://github.com/kevfang03/kevfang03/blob/main/views/dusk.md"><img src="assets/buttons/dusk.svg" alt="Dusk"></a>
<a href="https://github.com/kevfang03/kevfang03/blob/main/views/night.md"><img src="assets/buttons/night.svg" alt="Night"></a>
</p>
<p align="center">
<a href="https://github.com/kevfang03/kevfang03/blob/main/views/level-10.md"><img src="assets/buttons/level-10.svg" alt="Lv 10 preview"></a>
</p>

<details>
<summary>How the sky islands work</summary>

An animated banner that grows with my GitHub activity, redrawn every hour from my public stats
and the time of day in Philadelphia. Hand-built SVG from Python, no images.

- Each public repo is a building that upgrades with its commits; the newest one is under
  construction.
- Contributions are XP. Islands unlock as I level up: the city, the stadium, then Starport and
  Sky Shrine at levels 6 and 8.
- The sky train gains coaches, cargo and an observation dome as I level up, and carries wheat,
  wood, stone and crystals earned from my stats.
- A companion evolves at levels 5 and 10, a dragon flies over on a 7-day streak, and a
  starfighter squadron grows with merged pull requests.

A GitHub Action redraws everything every hour, so there is no server. The rules are in
<a href="docs/DESIGN.md">docs/DESIGN.md</a>.

</details>
