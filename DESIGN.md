---
name: BloodDrive
description: Upcoming blood drives billed like a festival lineup, soonest first.
colors:
  ultramarine: "#2f3dd9"
  ground: "#f3f4ff"
  ink: "#0d1033"
  ink-soft: "#2b2f57"
  marigold: "#ffb627"
  marigold-hover: "#ffc552"
  white: "#ffffff"
typography:
  display:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "clamp(4rem, 12vw, 6rem)"
    fontWeight: 900
    lineHeight: 0.95
    fontVariation: "'wdth' 62"
  headline-large:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "clamp(2.5rem, 7vw, 3.25rem)"
    fontWeight: 900
    lineHeight: 0.95
    fontVariation: "'wdth' 75"
  headline-medium:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "clamp(2.125rem, 5vw, 2.5rem)"
    fontWeight: 900
    lineHeight: 0.95
    fontVariation: "'wdth' 87"
  title:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 900
    lineHeight: 0.95
    fontVariation: "'wdth' 100"
  band:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "clamp(1.125rem, 3vw, 1.5rem)"
    fontWeight: 900
    letterSpacing: "0.04em"
    fontVariation: "'wdth' 125"
  wordmark:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 900
    letterSpacing: "0.02em"
    fontVariation: "'wdth' 125"
  when:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 800
    lineHeight: 1.4
    fontFeature: "'tnum' 1"
  body:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "'tnum' 1"
  meta:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    letterSpacing: "0.1em"
    fontVariation: "'wdth' 125"
  tag:
    fontFamily: "'Archivo Variable', system-ui, sans-serif"
    fontSize: "0.6875rem"
    fontWeight: 800
    letterSpacing: "0.1em"
    fontVariation: "'wdth' 125"
rounded:
  tag: "3px"
  control: "4px"
spacing:
  xxs: "4px"
  xs: "8px"
  sm: "10px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  column: "48px"
components:
  register:
    backgroundColor: "{colors.marigold}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
  register-hover:
    backgroundColor: "{colors.marigold-hover}"
  register-headline:
    backgroundColor: "{colors.marigold}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "12px 20px"
  button-filter:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
  button-filter-hover:
    backgroundColor: "{colors.ground}"
  button-clear:
    textColor: "{colors.white}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
  input-filter:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "9px 10px"
  tag:
    textColor: "{colors.ink}"
    typography: "{typography.tag}"
    rounded: "{rounded.tag}"
    padding: "2px 6px"
  tag-solid:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
    typography: "{typography.tag}"
    rounded: "{rounded.tag}"
    padding: "2px 6px"
  text-button:
    textColor: "{colors.ultramarine}"
  masthead:
    backgroundColor: "{colors.ultramarine}"
    textColor: "{colors.white}"
---

# Design System: BloodDrive

## Overview

**Creative North Star: "The Lineup Poster"**

BloodDrive bills blood drives the way a festival poster bills acts. The soonest drive headlines at poster scale; everything after it steps down in tiers (This week, Next week, Later), each tier smaller and wider than the one above. One variable family, Archivo, does all of the tiering through its width axis: condensed black caps for the names that matter most, wide caps for bands, labels and tags. The page is a flat printed sheet: an ultramarine masthead field over a periwinkle-white ground, ink type, heavy and hairline rules, and one marigold action.

Density is poster-like rather than app-like. There are no cards, no panels, no shadows; structure comes from type size, rules and two-column billing rows on wide screens. Color stays cool and calm on purpose: the system avoids the clinical hospital look and keeps red out of the palette. Every status is said in words (CANCELLED, DEMO) before it is shown in color.

Motion is absent: state changes are instant.

**Key Characteristics:**
- Venue names in heavy uppercase, condensed at the top and widening tier by tier (62%, 75%, 87%, 100% width).
- Wide-cap bands sit on a 3px ink rule; acts inside a band are split by 1px ink hairlines.
- Ultramarine masthead, periwinkle-white page, ink text, marigold Register.
- Flat surfaces, 4px corners, no elevation.
- Tabular numerals everywhere, so dates and times line up.

## Colors

A cool, high-contrast poster palette: one saturated blue field, near-white ground, deep blue-black ink, and a single warm action color.

### Primary
- **Poster Ultramarine** (`ultramarine`): the masthead field, the browser theme color, the favicon tile, text-link buttons on the ground, the scrollbar and caret, and the cancelled bar through a venue name.

### Secondary
- **Marigold** (`marigold`): fills the Register button and nothing else. Its other uses are functional signals only: the text-selection highlight, the focus ring inside the ultramarine masthead, and the border of an invalid filter input. Register hover lightens to `marigold-hover`.

### Neutral
- **Periwinkle Ground** (`ground`): the page background below the masthead; also the hover fill of the white filter button.
- **Lineup Ink** (`ink`): all primary text, every rule, tag outlines, the solid CANCELLED tag fill, and the default focus ring.
- **Soft Ink** (`ink-soft`): secondary meta lines (address, organizer, capacity) and the footer. It is the lightest text color allowed on the ground.
- **White** (`white`): masthead text, filter inputs and the primary filter button, solid-tag text.

### Named Rules
**The One Action Rule.** Marigold fills exactly one kind of element: the Register link. It never decorates, never becomes a background band, and never marks a second button.

**The Full Contrast Rule.** Text is ink, soft ink, or white on ultramarine. No grey text below WCAG AA anywhere.

## Typography

**Display Font:** Archivo Variable (with system-ui, sans-serif), self-hosted, width axis 62–125%
**Body Font:** Archivo Variable
**Label Font:** Archivo Variable at 125% width

**Character:** One grotesque family stretched across its whole width range. Narrow black caps read as headliners; wide spaced caps read as poster billing and labels. The build sets width with `font-stretch`; the `fontVariation` values in the tokens are the same widths.

### Hierarchy
- **Display** (900, 62% width, uppercase): the headliner venue name only. Balanced wrapping.
- **Headline Large / Medium** (900, 75% / 87% width, uppercase): venue names in This week and Next week.
- **Title** (900, 100% width, uppercase): venue names in Later.
- **Band** (900, 125% width, uppercase): tier names (This week, Next week, Later).
- **Wordmark** (900, 125% width, uppercase; 1.375rem below 720px): BLOODDRIVE in the masthead.
- **When** (800): date and local time line. Scales up to clamp(1.125rem, 2.5vw, 1.5rem) for the headliner and down to 0.9375rem in Later. The headliner's "Next up" / "Happening now" sits inline at the start of this line in 125% uppercase, separated by a middle dot.
- **Body** (400, line-height 1.4): drive descriptions, max 65ch; the welcome line in the masthead, max 60ch.
- **Meta** (400, soft ink): address, title and organizer, capacity.
- **Label** (700, 125% width, uppercase): filter field labels.
- **Tag** (800, 125% width, uppercase): DEMO and CANCELLED.

### Named Rules
**The Lineup Rule.** Importance is width and size, never color. The nearer the drive, the larger and more condensed its venue name; each tier steps one notch wider and smaller.

**The Wide Caps Rule.** Short structural words (wordmark, bands, labels, tags, the headliner lead) are wide 125% caps with positive tracking. Running text is never set in caps.

## Layout

A single centered column, max 1120px, with 16px side padding. The masthead is a full-bleed ultramarine field; the content column sits on the ground below it.

- **Filters:** below 720px a three-column grid (state 5rem, city 1fr, ZIP 6.5rem) with buttons on their own row; from 720px one row (7rem, minmax(12rem, 1fr), 9rem, auto).
- **Tiers:** the headliner section has no band heading; every following tier opens with its band. Entries in a tier are separated by a 24px gap and a hairline, with 24px above each entry.
- **Billing rows:** from 960px every drive is a two-column row, venue in the left 3fr column, when/where/actions in a 2fr column (min 300px), 48px column gap, baseline-aligned; the headliner aligns to the bottom. Below 960px everything stacks.
- **Rhythm:** 4/8/10/16/24/32/48px. Small gaps (4–12px) inside an entry, 24–32px between entries and around status messages.

## Elevation & Depth

Fully flat. There are no shadows, no blur and no layered surfaces. Depth comes from the masthead's solid field against the pale ground and from rule weight: a 3px ink rule opens a tier, a 1px ink hairline splits entries and closes the demo notice.

### Named Rules
**The Printed Sheet Rule.** Nothing floats. Hierarchy is carried by type and rules, never by shadow or card containers.

## Shapes

Square-ish. Controls (inputs, buttons, Register) have 4px corners; tags have 3px corners and a 1.5px ink outline. Rules run the full column width. The favicon repeats the system in miniature: an ultramarine 4px tile with three white-to-marigold bars stepping down in length, like billing lines.

## Components

### Buttons
- **Register (primary action):** marigold fill, ink text, weight 800, 4px corners, 10px 16px padding (12px 20px with 1.0625rem text on the headliner). Carries a 16px inline stroke icon for "external" and screen-reader text saying it opens the organizer's site in a new tab. Hover lightens the fill and underlines the label.
- **Find drives (masthead):** white fill and border, ink text, weight 800, 4px corners; hover fills with ground.
- **Clear (masthead):** transparent with a 2px white border and white text; hover adds a 12% white wash.
- **Text button (on the ground):** ultramarine, weight 800, underlined (offset 3px). Used for "Try again" and "Show all drives".
- **Focus:** 3px solid ink outline, 2px offset; inside the masthead the outline turns marigold.

### Chips
- **Tag:** wide caps on a transparent ground with a 1.5px ink outline, 3px corners, 2px 6px padding. Used for DEMO, next to the listing and in the demo notice.
- **Solid tag:** ink fill, white text. Used only for CANCELLED.

### Inputs / Fields
- **Style:** white field, 2px white border, 4px corners, 9px 10px padding, 1rem ink text at normal width, labels above in wide caps.
- **Focus:** marigold outline (masthead focus rule).
- **Error:** an invalid, non-empty field gets a marigold border; the browser title text explains the format.

### Navigation
- **Masthead:** ultramarine field holding the wordmark, one welcome line and the filter form. No other navigation.

### Drive Entry (signature)
Venue name, then a details block: when line, meta lines, optional description, and an actions row (CANCELLED tag, Register or "No sign-up link yet", DEMO tag). Later-tier entries are compact: city, state and organizer on one meta line, no address or description.

### Cancelled Drive
The venue name keeps its full ink color and gets an ultramarine band across its lower letters (64% to 76% of the line height, clear of the C and G openings, cloned across wrapped lines). The actions row shows the solid CANCELLED tag and no Register link; capacity is hidden.

## Do's and Don'ts

### Do:
- **Do** size venue names by date proximity: 62% width for the headliner, then 75%, 87% and 100% by tier.
- **Do** open every tier after the headliner with a wide-cap band on a 3px ink rule, and split entries with a 1px ink hairline.
- **Do** say every status in words with a tag (DEMO outlined, CANCELLED solid ink); color only reinforces it.
- **Do** lay out each drive as a two-column billing row from 960px, venue left, details right.
- **Do** keep numerals tabular and show times in the drive's own timezone.
- **Do** mark external Register links with the inline icon and screen-reader text.

### Don't:
- **Don't** use marigold for anything but Register and the functional signals listed under Colors.
- **Don't** put drives in stacked white cards, panels or shadowed containers.
- **Don't** add red, gore or clinical hospital cues to the palette or imagery.
- **Don't** set text in grey below WCAG AA; soft ink is the lightest text on the ground.
- **Don't** add a label above the venue name; the headliner's lead lives inline in the when line.
- **Don't** add decorative gradients; the only gradient is the hard-stopped cancelled band.
- **Don't** add motion beyond instant state changes.
