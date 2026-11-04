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

### Hi, I'm Kevin

I study computer science and work on a university IT service desk, so I build the tools I
wish the desk had: automation that takes the repetitive work off people and is safe to point
at real student data. Read-only access, plain rules before any AI, and answers that show
their sources.

### Featured projects

<table>
<tr>
<td width="50%" valign="top">
<a href="https://github.com/kevfang03/tdx-queue-auditor"><img src="assets/social/social-tdx-queue-auditor.png" alt="TDX queue auditor: a demo Teams shift summary card listing tickets grouped by what the help desk should do next"></a>
<h4><a href="https://github.com/kevfang03/tdx-queue-auditor">TDX queue auditor</a></h4>
Checks a help desk's ticket queue for stale and stuck tickets with plain, testable rules, then
posts a shift summary card to the desk's Teams chat. Read-only, and no AI unless you turn it on.
<br><sub>Python · Playwright · Teams Workflows · optional Claude API</sub>
</td>
<td width="50%" valign="top">
<a href="https://github.com/kevfang03/scis-help-assistant"><img src="assets/social/social-scis-help-assistant.png" alt="SCIS help assistant: the chat widget answering a VPN question with a numbered source link"></a>
<h4><a href="https://github.com/kevfang03/scis-help-assistant">SCIS help assistant</a></h4>
A chat assistant that answers students' IT questions from public support pages, cites every
page it used, and says so when a question isn't covered instead of guessing.
<br><sub>Python · FastAPI · hybrid search (BM25 + embeddings) · Claude API</sub>
</td>
</tr>
</table>

<p align="center">
<img src="https://img.shields.io/badge/Python-17123a?style=for-the-badge&logo=python&logoColor=ffd27a" alt="Python">
<img src="https://img.shields.io/badge/Claude_API-17123a?style=for-the-badge&logo=claude&logoColor=ffd27a" alt="Claude API">
<img src="https://img.shields.io/badge/Playwright-17123a?style=for-the-badge" alt="Playwright">
<img src="https://img.shields.io/badge/FastAPI-17123a?style=for-the-badge&logo=fastapi&logoColor=ffd27a" alt="FastAPI">
<img src="https://img.shields.io/badge/GitHub_Actions-17123a?style=for-the-badge&logo=githubactions&logoColor=ffd27a" alt="GitHub Actions">
<img src="https://img.shields.io/badge/pytest-17123a?style=for-the-badge&logo=pytest&logoColor=ffd27a" alt="pytest">
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
