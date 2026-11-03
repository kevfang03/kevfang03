# Sky islands: design

A lo-fi floating world on a GitHub profile. It is redrawn every hour from public GitHub
activity, Philadelphia time and weather, and Philly sports schedules. Coding builds the world
out; time, weather, seasons and random events keep it alive between visits.

## Art direction

- **Lo-fi lighting first.** Each hour has one clear mood: golden hour, dusk, night, rainy
  night or snowy morning. Warm small lights (lanterns, string lights, windows) sit against a
  big sky. The distance fades into the sky colour, and the foreground drops to soft silhouettes.
- **A cozy anchor.** In the foreground, a figure in a hoodie and headphones sits on a balcony
  with a laptop, next to a sleeping cat, watching the islands. They are seen from behind, so it
  is not a portrait.
- **The game UI stays small.** A level badge, a few resource pills and one event or quest line
  are enough. The art leads.
- Vector SVG with CSS animation only; every file under 600 KB; animation is turned off for
  viewers who prefer reduced motion.
- **Phones:** shown at phone width the banner is a third of its size, so a media query inside
  the SVG hides the labels and fine print and enlarges the title and level bar.

## Resources (all public GitHub data)

| Resource | Source | What it builds |
|---|---|---|
| XP | all-time contributions | island level, new islands |
| Wheat | contributions this year | the Server Farm's racks (one per 30) and the old wheat patch |
| Wood | current streak (days) | trees and an orchard; a broken streak stops growth, it never destroys |
| Stone | merged pull requests | roads, bridges, docks |
| Crystals | stars received | glowing crystals under the islands |

## Buildings and upgrades

- **HQ** grows with level: cottage, then hall, then keep.
- **One building per public repo.** The style comes from the main language (Python: library
  or observatory; JavaScript/TypeScript: workshop; docs: bookshop; other: cottage). Its tier
  comes from the commit count: wood, then stone, then glowing.
  - **Recently active repos** have lit windows and chimney smoke.
  - **Repos untouched for 6+ months** grow vines but are never ruined.
- **Current project:** the most recently pushed repo, under scaffolding with a crane, shown as
  the quest ("Finish ops-suite · 56 to go").
- **Badges** (100-day streak, first release, 1,000 contributions) hang as banners on the HQ.

## Islands (unlock by XP, linked by bridges and a sky rail)

1. **Home meadow:** HQ, repo buildings, farm, orchard.
2. **Philly island:** a mini skyline with City Hall and Boathouse Row.
3. **Stadium island:** dark most days; lit up on game days.
4. **Starport** (level 6): a landing pad, a hangar, fuel tanks and a control tower, floating on
   thrusters. One starfighter parks there per 3 merged pull requests (up to three), and one
   lifts off now and then.
5. **Sky Shrine** (level 8): a torii gate, a shrine hall, stone lanterns and cherry trees, with
   paper lanterns strung under its lip. Home of the sky dragon.

Locked islands float nearby, hazy, with a padlock and the level they open at. All creatures
and ships are original designs; no characters or ships from existing franchises.

## Your companion

An original sky sprite on the HQ roof terrace, next to you and the cat, that evolves with your
level: **Puff** (a round cloud sprite with a leaf sprout), then **Drift** at level 5 (a fox-like
sprite with a cloud tail and a brow crystal), then **Nimbus** at level 10 (winged, hovering, its
crystal glowing after dark).

## The sky train

A navy-and-gold liner that runs the loop around the islands. It grows with you: the engine,
one coach per two levels (up to four), a cargo wagon, and from level 4 a glass-domed
observation car. The cargo wagon carries this week's resources: wheat sacks for contributions
this week, logs for streak days, stone blocks for merged pull requests and crystals for stars
(up to three of each).

On the ride it stops at three stations and waits four seconds at each (the loop is 96
seconds). Every moment runs on the loop's clock, so it plays exactly while the train stands
there, and a sign over each platform shows the number that builds that place:

| Station | While the train waits | Sign |
|---|---|---|
| Stadium | fireworks over the stands; while locked, a glint on the padlock | all-time contributions, or how many to go |
| Wild side | sky jellies rise past the forest, the dragon flies over; once open, a starfighter lifts off the Starport and petals blow off the Shrine | current streak |
| Server Farm | a drone lowers a crate into the cargo wagon | contributions this year |

The town's station master waves the train off and back in.

## Living world

- **Time:** Philly time picks dawn, day, golden hour, dusk or night, from real sunrise and sunset.
- **Weather:** real weather from Open-Meteo, with real sunrise and sunset: an overcast tint,
  rain, storms with lightning, snow and fog. If the feed is down the sky is drawn clear.
- **Seasons:** trees, crops and flowers change colour; spring petals drift across the sky,
  butterflies come out on summer days, autumn leaves tumble down, and in winter every
  island gets a snow cap and icicles and snowmen stand in the town and on the Server Farm.
- **Holidays:** each lasts as long as it is celebrated, from Pi Day's one day to a month
  of December lights, and decorates the whole map: the town street, the ride's station
  platforms, the Server Farm and the sky. Christmas week puts the dragon in a Santa hat
  and swaps the starfighters for a reindeer sleigh; Lunar New Year turns it into a golden
  dragon chasing a flaming pearl, under red lanterns. Halloween, Thanksgiving, Hanukkah,
  Valentine's, St. Patrick's, Easter, July 4 and New Year each have their own; the full
  list is in `sky_islands/holidays.py`.

## Events

Rolled once per hourly redraw with a seed from the date and hour, so each image is repeatable.
The header names whatever rare or dated event is happening, rarest first:

| Event | When |
|---|---|
| Shooting stars | most clear nights |
| Sky train between islands | always, about once a minute |
| Airship arrivals | one per pull request merged this week |
| Dragon flyover | every loop while your streak is 7 days or more, during the wild-side stop |
| Starfighter squadron | every loop, as the overview opens |
| Golden "shiny" dragon | about 1 in 200 redraws; flies even without a streak |
| Sky whale and calf | every overview, gliding far behind the islands; glowing spots at night |
| Sky jellies | always, rising out of the cloud sea between islands; lit up at night |
| Cargo airship | always, drifting over the Server Farm's sunset on the ride |
| Meteor shower | real dates (Perseids around Aug 12, Geminids around Dec 14) |
| Big moon | real full-moon nights |
| Aurora | about 1 in 12 clear winter nights (Dec to Feb) |
| Comet | about 1 in 30 clear evenings |
| Game day | stadium lights, crowd, opponent and start time; the score once it starts |
| Victory fireworks | the day after a Philly win, in the team's colours |
| Holiday fireworks | July 4 and New Year's Eve, after dark |
| Grand opening | the day a new repo appears |
| Lighthouse flash | the day of a release |
| Anniversary | GitHub account anniversary |
| Night owl | a commit after midnight keeps the balcony laptop glowing; no commits yet today and the figure naps |

## Companion

A dragon pet that grows with level: egg, then hatchling, then young dragon, then a full dragon
circling the islands. Navy and gold; an original design, not any school's logo.

## Customization (`island.toml`, non-secret)

Palette, island names, pet, figure colours, the decorations shown, and which teams count for
game days.

## The profile page

The banner sits on top, linked to the repo. Under it, game-style buttons (Dawn, Day, Dusk,
Night and Lv 10 preview) open pages in `views/`, each showing today's world at that time of
day, or the same account fully grown at level 10 with a 7-day streak and three starfighters.
GitHub runs no scripts in a README, so every button is a picture inside a link, and the page
you are on shows its button pressed. How it all works sits in a collapsed section.

The hourly Action draws the banner and all five views and force-pushes them to the `output`
branch. The buttons never change, so they live on main (`python -m sky_islands buttons`).

## Data sources

- **GitHub GraphQL** (Action token): contribution calendar per year, repositories, pull
  requests, stars, releases.
- **Open-Meteo** (no key): weather, sunrise and sunset.
- **ESPN public scoreboard:** schedules and scores. If it fails, game-day features are skipped.

## Open questions

- Whether to show the figure, or the cat alone.
- How many islands to plan before the art gets crowded at README width (~880 px).
