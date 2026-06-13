# UX Psychology — Cognitive principles applied

A short, working list of cognitive biases and perceptual principles that affect every interface. Use this when the user asks for an "ergonomic review", a "conversion audit", or "why isn't this flow working?".

Organized along the four cognitive steps every user goes through: **filtering information**, **seeking meaning**, **acting under time pressure**, and **storing memories**.

---

## 1. Information — what the user lets in

Users filter ruthlessly. A page that respects this gets used; a page that ignores it gets abandoned.

### Hick's Law
The more options you show, the longer the decision takes. Reduce visible choices; reveal advanced options progressively.

### Cognitive Load
Total mental effort. Cut anything that doesn't carry meaning: decorative chrome, redundant icons, parallel navigation patterns.

### Anchoring
The first number / option / claim sets the comparison frame. If you show three plans, the user evaluates relative to the middle one. Put the option you want chosen in the centre.

### Fitts's Law
Target time depends on size and distance. Make the primary action large and close to the current cursor / thumb position. On mobile, bottom-anchor it.

### Progressive Disclosure
Show the next step only when the current one is done. Settings collapsed by default; advanced filters behind a "More" toggle.

### Visual Hierarchy
The eye reads contrast and size before color. Set hierarchy with weight and size; use color as a secondary cue.

### Von Restorff Effect
One thing that breaks the pattern gets remembered. Use sparingly — one highlighted CTA, one promoted card.

### Aesthetic-Usability Effect
Users perceive attractive interfaces as easier to use. Polish matters, but never at the cost of clarity.

### Banner Blindness
Anything that looks like an ad — coloured strip, dense corner box — gets tuned out, even when it isn't an ad. Don't disguise content as marketing.

### Fitts's Law corollary — edges and corners
Screen edges and corners have effectively infinite size on desktop (you can't overshoot). Reserve them for high-frequency actions on desktop apps.

---

## 2. Meaning — what the user fills in

When there's a gap, users invent a story. Make sure the story is the one you want.

### Mental Model
Users come with a model from prior products. Match it where you can; warn when you diverge. "Save" should mean save; "delete" should mean delete.

### Familiarity Bias
Users prefer what looks familiar. Native-feeling controls beat clever new ones for adoption.

### Social Proof
"Used by N teams" / "X just signed up" works when it's specific and verifiable. Generic logos are noise; logos of real customers earn trust.

### Scarcity
"Only 2 left" and "Sale ends Friday" raise perceived value when true. Faked scarcity destroys trust the moment it's caught.

### Reciprocity
Give something — a useful free tier, a thoughtful empty state, a generous error message — and users feel they should return value. Don't ask for an email before showing the product.

### Goal Gradient Effect
Motivation rises as the goal nears. Onboarding bars showing 75 % complete pull users through faster than ones showing 30 %.

### Authority & Halo
A single trust signal (security badge, expert quote, well-known logo) colors perception of the whole product. Place it early.

### Curse of Knowledge
Designers know the product; users don't. Test copy with someone who doesn't work on it.

### Aha! Moment
The instant the user understands the product's value. Cut every step between landing and that moment.

### Occam's Razor
The simplest explanation tends to be right. If a flow is confusing, the issue is usually obvious.

### Curiosity Gap
"Here's what you don't know" pulls. Use for content discovery; never to manipulate into clicks.

---

## 3. Time — the user is in a hurry

Users skim, satisfice, and bail. Design assumes ~5 seconds of attention per screen.

### Loss Aversion
Losing hurts about twice as much as gaining feels good. "Don't miss out" outperforms "Gain N". But repeated negative framing erodes trust — use sparingly.

### Default Bias
Users keep defaults. Default to the safest, kindest behavior. Pre-tick the consent-to-required box; never pre-tick the marketing one.

### Sunk Cost
The user who's invested time in a wizard wants to finish it. Don't make them restart.

### Reactance
Forced behavior generates resistance. Tell users why, not just what. "We need your email to send the receipt" beats "Email required".

### Decision Fatigue
Each decision costs energy. Reduce trivial decisions; preserve user energy for the meaningful ones.

### Hyperbolic Discounting
A reward now beats a bigger reward later. Show immediate value before asking for future commitment.

### Labor Illusion
Visible work increases perceived quality. A two-second progress bar that names what's happening ("Checking your email…", "Setting up your workspace…") feels better than instant completion. Use sparingly — fake progress bars are bad-faith.

### Tesler's Law
Some complexity is irreducible. Decide who handles it. If you simplify the UI, you push complexity to the user. Find the place where complexity is least painful.

### Discoverability
A feature that exists but isn't findable might as well not exist. Audit: can a new user find each top-level feature without reading docs?

### Investment Loops
The more a user customizes, configures, or invites, the harder it is to leave. Earn investment; never lock it in artificially.

---

## 4. Memory — what the user takes away

Memory is selective. The peak and the end count; the middle barely registers.

### Peak-End Rule
Experiences are judged by their best (or worst) moment and their ending. Invest in the high points and the final screen of a flow.

### Zeigarnik Effect
Incomplete tasks itch. Use this for productive nudges (a saved-but-not-submitted draft); don't use it to nag.

### Endowment Effect
Things the user has touched feel theirs. Editing a profile, configuring a workspace, completing a draft all create ownership.

### Chunking
Working memory holds ~7 items. Group, label, summarize. Phone numbers and credit cards already do this; everything else should too.

### Recognition over Recall
It's easier to recognize than to remember. Show options; don't ask the user to type from memory. Autocomplete > free text.

### Picture Superiority
Images are remembered better than words. A diagram next to a paragraph is read; the paragraph alone is skimmed.

### Storytelling
Facts wrapped in a story are remembered better. The release-note "Why we built this" line beats "What changed".

### Serial Position Effect
The first and last items in a list stick. Place the most important options at the top and bottom; the routine ones in the middle.

### Delighters
A small unexpected pleasure (a thoughtful error illustration, a kind copy line, a smooth confetti on success) sets a positive peak. Save them for moments that deserve it.

### Exit Points
Pages should have a clean way to leave at the right moment. A pushy retention prompt at the door undoes the goodwill the rest of the product earned.

---

## How to apply

1. Pick **one** principle that fits the current task and apply it concretely. Don't sprinkle dozens of biases across a single screen.
2. Match the principle to the user's cognitive step:
   - Landing / first impression → Hierarchy, Anchoring, Aesthetic-Usability, Banner Blindness.
   - Decision moment → Hick's Law, Default Bias, Loss Aversion, Social Proof.
   - During a long flow → Goal Gradient, Sunk Cost, Labor Illusion, Progressive Disclosure.
   - End of flow → Peak-End, Endowment, Delighters, Exit Points.
3. **Stay ethical.** Most of these principles can be weaponized into dark patterns. The skill refuses dark patterns — see `anti-patterns.md` for the list.

## Checklist before a flow ships

- [ ] One clear next action per screen (Hick / Fitts).
- [ ] Hierarchy works in grayscale.
- [ ] Defaults are the safe, kind choice.
- [ ] First and last steps polished (Peak-End).
- [ ] Progress shown for any multi-step flow (Goal Gradient).
- [ ] Recognition beats recall in choosers.
- [ ] No invented social proof or scarcity.
- [ ] Clean exit at every reasonable point.
