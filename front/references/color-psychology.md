# Color Psychology Reference

Source: <https://harchaoui.org/warith/colors/>

These palettes are the authoritative color choices for the `front` skill. Map every color decision back to one of these tables. The UI guidelines define *how* color is applied (contrast, dark mode, semantics); this file defines *which* hue is chosen and *why*.

---

## 1. Base palette — hues with light variants

Each base hue ships with a light tint suitable for backgrounds, hover states, and subtle surfaces.

| Name | Hex | RGB | Light variant | Hex | RGB |
|---|---|---|---|---|---|
| Red | `#FF3B30` | 255, 59, 48 | Light Red | `#FFD8D6` | 255, 216, 214 |
| Orange | `#FF9500` | 255, 149, 0 | Light Orange | `#FFEACC` | 255, 234, 204 |
| Yellow | `#FFCC00` | 255, 204, 0 | Light Yellow | `#FFF5CC` | 255, 245, 204 |
| Green | `#28CD41` | 40, 205, 65 | Light Green | `#D4F5D9` | 212, 245, 217 |
| Blue | `#007AFF` | 0, 122, 255 | Light Blue | `#CCE4FF` | 204, 228, 255 |
| Turquoise | `#79DBDC` | 121, 219, 220 | Light Turquoise | `#00FFEF` | 0, 255, 239 |
| Purple | `#AF52DE` | 175, 82, 222 | Light Purple | `#EFDCF8` | 239, 220, 248 |
| Pink | `#FF2D55` | 255, 45, 85 | Light Pink | `#FFD5DD` | 255, 213, 221 |

## 2. Emotion palette — when the design has emotional intent

| Emotion | Hex |
|---|---|
| Silence | `#000000` |
| Neutral | `#808080` |
| Anger | `#FF3B30` |
| Surprise | `#FF9500` |
| Joy | `#FFCC00` |
| Disgust | `#28CD41` |
| Happiness | `#79DBDC` |
| Sadness | `#007AFF` |
| Fear | `#AF52DE` |

## 3. Concept palette — when the design conveys a value

| Concept | Hex |
|---|---|
| Balance, Neutral, Calm | `#808080` |
| Excitement, Youthful, Bold | `#FF3B30` |
| Friendly, Cheerful, Confidence | `#FF9500` |
| Optimism, Clarity, Warmth | `#FFCC00` |
| Peaceful, Growth, Health | `#28CD41` |
| Trust, Dependable, Reliable, Strength | `#007AFF` |
| Creative, Imaginative, Wise | `#AF52DE` |

## 4. Psychology palette — positive vs. negative associations

Always check the negative column before locking a color choice. A color that fits the positive list for one brand can also project a negative trait you didn't intend.

| Color | Hex | Positive | Negative |
|---|---|---|---|
| Red | `#FF3B30` | Power, Passion, Energy, Fearlessness, Strength, Excitement | Anger, Danger, Warning, Defiance, Aggression, Pain |
| Orange | `#FF9500` | Courage, Confidence, Warmth, Innovation, Friendliness, Energy | Deprivation, Frustration, Frivolity, Immaturity, Ignorance, Sluggishness |
| Yellow | `#FFCC00` | Optimism, Warmth, Happiness, Creativity, Intellect, Extraversion | Irrationality, Fear, Caution, Anxiety, Frustration, Cowardice |
| Green | `#28CD41` | Health, Hope, Freshness, Nature, Growth, Prosperity | Boredom, Stagnation, Envy, Blandness, Enervation, Sickness |
| Turquoise | `#79DBDC` | Communication, Clarity, Calmness, Inspiration, Self-expression, Healing | Boastfulness, Secrecy, Unreliability, Reticence, Fence-sitting, Aloofness |
| Blue | `#007AFF` | Trust, Loyalty, Dependability, Logic, Serenity, Security | Coldness, Aloofness, Emotionless, Unfriendliness, Uncaring, Unappetizing |
| Purple | `#AF52DE` | Wisdom, Luxury, Wealth, Spirituality, Imaginative, Sophistication, Introversion | Decadence, Suppression, Inferiority, Extravagance, Moodiness |
| Pink | `#FF2D55` | Imaginative, Passion, Transformation, Creative, Innovation, Balance | Outrageousness, Nonconformity, Flippancy, Impulsiveness, Eccentricity, Ephemerality |
| Brown | `#A52A2A` | Seriousness, Warmth, Earthiness, Reliability, Support, Authenticity | Humorlessness, Heaviness, Unsophisticated, Sadness, Dirtiness, Conservativeness |
| Black | `#000000` | Sophistication, Security, Power, Elegance, Authority, Substance | Oppression, Coldness, Menace, Heaviness, Evil, Mourning |
| Gray | `#808080` | Timelessness, Neutrality, Reliability, Balance, Intelligence, Strength | Unconfident, Dampness, Depression, Hibernation, Lack of energy, Blandness |
| White | `#F8F8F8` | Cleanliness, Clarity, Purity, Simplicity, Sophistication, Freshness | Sterility, Coldness, Unfriendliness, Elitism, Isolation, Emptiness |

---

## How to pick a color

1. **Start from intent**, not from aesthetics. Ask: is the design conveying an *emotion*, a *concept*, or a *system semantic* (success/warning/danger/info)?
2. **Read the negative column** of the Psychology palette. If the negative trait clashes with brand voice, pick a neighbor.
3. **Pair with a light variant** for backgrounds, hover, and selection — never reuse the base hue at low opacity for surfaces, prefer the listed light tint.
4. **Map to Tailwind tokens** — see `stack-tailwind.md`. Every base hue is exported as a Tailwind color so authors write `bg-brand-blue` not `bg-[#007AFF]`.
5. **Reserve red for destructive or critical states**, never for primary CTAs.

## Semantic mapping (defaults)

| Role | Default | Reason |
|---|---|---|
| Primary action / link | Blue `#007AFF` | Trust, dependability |
| Destructive | Red `#FF3B30` | Universally read as danger |
| Success | Green `#28CD41` | Health, growth |
| Warning | Yellow `#FFCC00` | Caution, high attention without alarm |
| Info / neutral notice | Turquoise `#79DBDC` | Calm, communicative |
| Premium / accent | Purple `#AF52DE` | Wisdom, luxury — use sparingly |
| Brand emotion (joyful) | Orange `#FF9500` or Pink `#FF2D55` | Friendly, energetic |
| Neutral surfaces | Gray `#808080`, White `#F8F8F8`, Black `#000000` | Backbone of layout |
