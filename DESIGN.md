# DESIGN.md — Oil Level Tracker v2

These are the visual rules for every v2 screen and for the report.

- **Format:** the nine-section DESIGN.md format (Google Stitch; see
  VoltAgent/awesome-design-md).
- **Values:** Microsoft Fluent 2, light theme.
- **No Fluent library.** The front end is plain JavaScript with no build step,
  so it copies only the token values below as CSS custom properties.
- **Adding a value:** put any new colour, size or shadow here first.

## 1. Visual Theme & Atmosphere

- **A calm Windows measurement tool,** not a marketing page.
- **The data is the brightest, most colourful thing on screen:** the context
  image and the lines. Chrome around it is white and light neutral grey,
  separated by hairline strokes, with almost no shadow.
- **One accent colour (Fluent brand blue)** marks interaction: the selected
  tool, focus, primary buttons. Domain colours (§2.3) mean data and are
  never used for chrome.
- **Density:** the window is a working surface. Use compact Fluent sizes:
  - 32 px controls, or 24 px in toolbars;
  - 14 px body text, 12 px captions.
- **Light theme only** in the first version. The report is printed, and both
  share one palette.

## 2. Color Palette & Roles

### 2.1 Neutrals (Fluent 2 light)

| Token | Value | Role |
|---|---|---|
| `--bg-1` | `#FFFFFF` | panels, plot area, inputs |
| `--bg-2` | `#FAFAFA` | app background behind panels |
| `--bg-3` | `#F5F5F5` | toolbar, panel headers, table header rows |
| `--bg-4` | `#F0F0F0` | hover on subtle controls |
| `--bg-5` | `#EBEBEB` | pressed on subtle controls |
| `--fg-1` | `#242424` | primary text, axis labels, playhead |
| `--fg-2` | `#424242` | secondary text, icons |
| `--fg-3` | `#616161` | captions, units, tick labels |
| `--fg-disabled` | `#BDBDBD` | disabled text and icons |
| `--stroke-1` | `#D1D1D1` | control borders, panel dividers |
| `--stroke-2` | `#E0E0E0` | grid lines, table rules |
| `--stroke-3` | `#F0F0F0` | minor grid lines |

### 2.2 Brand / interaction

| Token | Value | Role |
|---|---|---|
| `--brand` | `#0F6CBD` | primary button, selected tool, focus, links |
| `--brand-hover` | `#115EA3` | hover on brand controls |
| `--brand-pressed` | `#0C3B5E` | pressed on brand controls |
| `--brand-tint` | `#EBF3FC` | selected rows and selected tool background |
| `--focus-outer` | `#000000` | focus ring outer (2 px) |
| `--focus-inner` | `#FFFFFF` | focus ring inner (1 px) |

### 2.3 Domain roles (data colours)

Use these on the graph, the context image, the video overlay and the report.
Nothing else may reuse them.

| Token | Value | Role |
|---|---|---|
| `--oil` | `#1F77D0` | Oil line |
| `--foam` | `#E8710A` | Foam line (always distinct from Oil) |
| `--reference` | `#616161` | reference line, 1.5 px, dash `6 4` |
| `--line-halo` | `rgba(255,255,255,0.9)` | 3 px halo under every line drawn over an image |
| `--full-band` | `rgba(31,119,208,0.10)` | automatic FULL stretch band; label "FULL" in `--oil` |
| `--empty-band` | `rgba(97,97,97,0.10)` | automatic EMPTY stretch band; label "EMPTY" in `--fg-3` |
| `--cannot-judge` | `#8A8A8A` | "cannot judge" stretch: 45° hatch, 1 px lines, 6 px apart, plus a `rgba(138,138,138,0.12)` fill |
| `--compressor` | `#8764B8` | compressor-start marker (vertical, 1.5 px, dash `4 3`, label at the top) |
| `--playhead` | `#242424` | playhead, 1 px, with a small triangle on the time axis |
| `--memo` | `#C19C00` | memo pin, a numbered circle with white text |
| `--glass-outline` | `rgba(255,255,255,0.9)` | Glass ellipse and zero line on frames (Recipe screen, video): 1 px, dash `4 3`, over a 1 px `--glass-shadow` line |
| `--glass-shadow` | `rgba(0,0,0,0.5)` | shadow line 1 px below every `--glass-outline` stroke |

### 2.4 Status (judgment and Glass check state)

| Token | Text | Background | Use |
|---|---|---|---|
| `--pass` | `#0E700E` | `#F1FAF1` | PASS |
| `--fail` | `#C50F1F` | `#FDF3F4` | FAIL |
| `--review` | `#BC4B09` | `#FFF9F5` | needs review, or overridden (the badge also says "덮어씀") |
| `--pending` | `#616161` | `#F5F5F5` | Glass not checked yet |

A status is always shown as text plus colour, never colour alone.

### 2.5 Frame chrome

Used around and on top of video frames (Recipe screen, editor video).

| Token | Value | Role |
|---|---|---|
| `--frame-bg` | `#1B1F23` | area behind a frame that does not fill its box |
| `--frame-caption-bg` | `rgba(0,0,0,0.45)` | label chip on a frame (Glass name, "0"), white Caption 1 text |

### 2.6 Validation (Fluent palette red)

| Token | Value | Role |
|---|---|---|
| `--error` | `#BC2F32` | field error message and problem count |
| `--error-border` | `#D13438` | 1 px border of an input with an error |

These mark input errors. They never stand in for FAIL (§2.4).

## 3. Typography Rules

- **Families:**
  - UI: `"Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif`.
  - Numbers in tables and on axes: the same family with
    `font-variant-numeric: tabular-nums`.
  - Monospace (hashes, paths): `"Cascadia Mono", Consolas, monospace`.
- **Korean** text uses the same stack. Windows falls back to Malgun Gothic,
  so no extra font is bundled.

| Ramp | Size / line | Weight | Use |
|---|---|---|---|
| Caption 1 | 12 / 16 | 400 | tick labels, units, hints |
| Body 1 | 14 / 20 | 400 | default text, inputs |
| Body 1 Strong | 14 / 20 | 600 | panel titles, table headers |
| Subtitle 2 | 16 / 22 | 600 | dialog and section titles |
| Subtitle 1 | 20 / 28 | 600 | report title, judgment badge text |
| Title 3 | 24 / 32 | 600 | report header (print) |

Do not use sizes outside this ramp.

## 4. Component Stylings

- **Buttons:**
  - 32 px high, radius 4, padding 0 12, Body 1.
  - Primary: `--brand` fill, white text.
  - Secondary: `--bg-1` fill, 1 px `--stroke-1`.
  - Subtle (toolbar): transparent, `--bg-4` on hover.
  - Disabled: `--fg-disabled`.
- **Tool buttons:**
  - 32 × 32, radius 4, a 20 px icon, and a tooltip with the shortcut.
  - The selected tool gets a `--brand-tint` fill and a `--brand` icon.
  - Only one tool is selected at a time.
- **Inputs:**
  - 32 px high, radius 4, 1 px `--stroke-1`.
  - The bottom border is 1 px `--fg-3`, becoming 2 px `--brand` on focus.
  - Units sit in `--fg-3` after the value.
- **Select (Glass picker):** like an input. Each item shows the Glass name and
  its status badge.
- **Badges:** 20 px high, radius 4, Caption 1 at weight 600, using the
  status colours.
- **Panels:**
  - `--bg-1` on `--bg-2`, with a 1 px `--stroke-1` divider between panels;
    no cards with shadows.
  - The header is 32 px, `--bg-3`, Body 1 Strong.
- **Plot:**
  - plot area `--bg-1`;
  - grid `--stroke-2` and `--stroke-3`;
  - axis line `--stroke-1`;
  - ticks Caption 1 in `--fg-3`.
  - **Editable range numbers:** the first and last time-axis numbers look
    like ticks. They become an inline input on click.
  - **Lines:** Oil and Foam are 2 px with round joins. A hovered or grabbed
    line is 3 px. The grab-width preview is a translucent band of the line
    colour at 15 % opacity.
- **Transport:**
  - subtle 32 px buttons for previous frame, play/pause and next frame;
  - a speed segmented control (1× 4× 16×);
  - a range-repeat toggle;
  - the time in `mm:ss.s`.
- **Frame view (Recipe screen):**
  - the frame fits its box on `--frame-bg`, with wheel zoom and Shift-drag
    pan;
  - unselected Glasses use the `--glass-outline` style in §2.3;
  - the selected Glass has a 1.5 px solid `--glass-outline` ellipse and
    zero line, over the same shadow line;
  - the Glass name sits above the ellipse in a `--frame-caption-bg` chip;
  - **the interaction follows v1:**
    - eight resize handles on the ellipse's bounding box (four corners,
      four edge midpoints): 8 × 8 px squares, `--bg-1` fill, 1 px
      `--brand` border;
    - dragging inside the ellipse moves the Glass with its zero line;
    - the zero line is the chord of the ellipse at its height. It is
      dragged up and down by the line itself, through a 14 px hit band,
      with a vertical-resize cursor. It sits above the ellipse, so
      grabbing it never moves the Glass;
    - a drag stops the zero line at the ellipse's top and bottom.
      Resizing the ellipse pulls the zero line back inside;
  - new in v2: arrow keys move the selected Glass 1 px (Shift: 10 px).
- **Field errors:**
  - the message sits under the input in Caption 1 `--error`, and the input
    border becomes `--error-border`;
  - an invalid number is not applied; the drawing keeps the last valid
    value;
  - saving is blocked while any error remains.
- **Tables (report and panels):**
  - Body 1;
  - header row `--bg-3`, Body 1 Strong;
  - rows separated by `--stroke-2`;
  - numbers right-aligned.

## 5. Layout Principles

- **Spacing scale:** 2, 4, 6, 8, 12, 16, 20, 24, 32 px. Panel padding is 12;
  gaps between controls are 8.
- **Editor window:** minimum 1280 × 800.
  - **Top toolbar, 48 px:**
    - tools on the left (grab, pencil, cannot judge, memo, pan);
    - the Glass picker in the middle;
    - Save and Submit on the right.
  - **Main area:**
    - **Left column, flexible width:**
      - the graph (about 45 % of the height);
      - the context image (about 45 %);
      - a 32 px shared time axis with the playhead and editable range
        numbers.
      - The graph and the image always share the same time scale and
        horizontal scroll.
    - **Right column, 360 px:**
      - the video, cropped to the Glass with the lines drawn over it, and
        its transport;
      - the judgment panel (computed result, override, reason);
      - the selection panel;
      - the memo list.
- **Recipe list:** the same window.
  - **Toolbar, 48 px:** the title "Recipe" on the left; "새 Recipe"
    (primary) on the right.
  - **Body:** one panel with a table: name, Glass names, frame size,
    modified date. A row opens on double-click or with "열기".
  - **Below the table:**
    - files that could not be read, each with its reason, in `--error`;
    - the Recipes folder path, with a "폴더 열기" button.
- **Recipe screen:** minimum 1280 × 800.
  - **Top toolbar, 48 px:**
    - "← 목록" and the Recipe name with its save state, on the left;
    - "영상 열기" next to them;
    - the problem count in `--error` and "저장" (primary), on the right.
  - **Main area:**
    - **Left column, flexible width:**
      - a 32 px header: the source video name, the saved reference-frame
        time, and the hint "저장하면 지금 보이는 프레임이 기준이 됩니다";
      - the frame view (§4);
      - a 40 px transport: previous frame, play/pause, next frame, a
        scrub bar with a "기준" mark at the saved reference time, and the
        time in `mm:ss.s`.
    - **Right column, 360 px:**
      - the Recipe name;
      - the Glass list, with "+ 추가";
      - the selected Glass:
        - its name;
        - the position in px (centre, radii, zero line);
        - the judgment rule, showing only the fields its mode uses.
- **Report:** A4 landscape. In order:
  1. the header block;
  2. the judgment;
  3. the graph and the context image, at full width;
  4. the criteria and key-time tables;
  5. the memo list.

## 6. Depth & Elevation

- **The surfaces are flat.** Only floating UI gets a shadow:
  - menus and tooltips: `0 0 2px rgba(0,0,0,.12), 0 4px 8px rgba(0,0,0,.14)`;
  - dialogs: `0 0 2px rgba(0,0,0,.12), 0 8px 16px rgba(0,0,0,.14)`.
- **Radius:**
  - 4 px for controls;
  - 8 px for dialogs;
  - 0 for panels and plots.

## 7. Do's and Don'ts

**Do:**
- Keep Oil and Foam colours fixed everywhere.
- Halo every line drawn over an image.
- Say status in words.
- Keep the graph and the context image aligned to the same pixel time scale.

**Don't:**
- Use brand blue for data.
- Use the domain colours for buttons.
- Add gradients, glass or blur effects.
- Use shadows on panels.
- Clip a line or marker at the plot edge. Inset the plot so a line at the
  Glass top or bottom stays fully visible.
- Make a plain drag on empty space pan the view.

## 8. Responsive Behavior

- **Desktop only.** The minimum window is 1280 × 800.
- **Below 1440 px wide,** the right column stays 360 px and the left column
  shrinks.
- **Below 900 px high,** the graph and the image share the height equally.
- **Print** follows the report layout in §5. It ignores the window size.

## 9. Agent Prompt Guide

- **Tokens:** use the CSS custom properties in §2 by name. Never hard-code a
  hex value in a component.
- **Before writing a screen:** check §5 for where it goes and §4 for the
  control styles.
- **New data visuals** take a domain role from §2.3. If none fits, add one
  here first.
- **Text** uses the ramp in §3. UI labels are Korean; tokens and code
  identifiers are English.
