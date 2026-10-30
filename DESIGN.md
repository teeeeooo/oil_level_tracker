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
| `--backdrop` | `rgba(0,0,0,0.4)` | behind a modal dialog |

### 2.2 Brand / interaction

| Token | Value | Role |
|---|---|---|
| `--brand` | `#0F6CBD` | primary button, selected tool, focus, links |
| `--brand-hover` | `#115EA3` | hover on brand controls |
| `--brand-pressed` | `#0C3B5E` | pressed on brand controls |
| `--brand-tint` | `#EBF3FC` | selected rows and selected tool background |
| `--focus-outer` | `#000000` | focus ring outer (2 px) |
| `--focus-inner` | `#FFFFFF` | focus ring inner (1 px) |
| `--range-fill` | `#FFE07A` | the analysis range band on the scrub bar: yellow, apart from the blue played part (user, 2026-10-29) |
| `--range-edge` | `#8F6A00` | that band's 2 px edges and its "시작" and "끝" marks |
| `--selection-band` | `rgba(15,108,189,0.12)` | a selected time range in the editor, over the graph and the image, between 1 px `--brand` edges |

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
| `--empty-mark` | `#E37D80` | an empty stretch of the Oil line (invalid until drawn): a 4 px bar on the time axis, and the label "빈 구간" in the graph |
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

### 2.7 Message bar (Fluent warning)

| Token | Value | Role |
|---|---|---|
| `--warning` | `#BC4B09` | the warning icon in a message bar |
| `--warning-bg` | `#FFF9F5` | a message bar's background |
| `--warning-border` | `#FDCFB4` | a message bar's 1 px bottom edge |

A message bar warns about the data a screen works on, such as a source
video that changed (A9). It never stands in for a judgment status (§2.4).

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
  - 32 px high, radius 4, padding 0 8: a 20 px icon followed by the tool
    name in Body 1, gap 6. The tooltip names the shortcut. Icons alone
    were hard to tell apart (user, 2026-10-29).
  - Undo, redo and the transport buttons stay 32 × 32 icons with a
    tooltip.
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
  - An inspection's state (분석 완료, 분석 안 됨, 분석 실패) is not a
    judgment: its badge uses the `--pending` colours, and a reason follows
    it in Caption 1 (`--error` for a failure).
- **Time field:** an input holding `mm:ss.s`, followed by a small "지금"
  button that puts in the time on screen.
  - It also takes plain seconds or `h:mm:ss`. Once entered (Enter, or
    leaving the field), it shows the value as `mm:ss.s` (user,
    2026-10-29).
  - An empty field shows the placeholder `mm:ss.s`.
- **Progress bar:** 4 px, radius 2, `--brand` on `--stroke-2`, with the
  percentage and the time left below it.
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
  - the speed field (below);
  - a range-repeat toggle;
  - the time in `mm:ss.s`.
- **Speed field** (the Recipe screen and the editor): a freeform Fluent
  combobox, 80 px wide, styled like an input, with `×` as its unit.
  - Its chevron opens a menu of presets: 0.5×, 1×, 2×, 3×, 4×. The menu
    takes the menu shadow (§6).
  - Any speed from 0.1× to 16× can be typed. It applies on Enter or when
    the field loses focus. `2`, `2x`, `×2` and `*2` all mean 2×.
  - A value outside the range is clamped to it. Text that is not a number,
    or Esc, restores the current speed.
- **Help:**
  - every toolbar ends with a subtle 32 × 32 help button: a "?" icon with
    the tooltip "도움말 (F1)";
  - the button, F1 or `?` opens a modal dialog, 560 px wide, on
    `--backdrop`. It has a Subtitle 2 title, Body 1 Strong group headings,
    and two columns: the key or mouse action, and what it does;
  - Esc, "닫기" or a click outside closes it;
  - **a screen shows a hint inline only when it must be read every time,**
    such as the save hint on the Recipe screen. Keys, mouse actions and
    tips go into the help.
- **Switch** (an on/off view option, such as "배경 제거 보기"): a 28 × 16
  track, radius 8, with a 1 px `--fg-3` border and a 10 px `--fg-2` knob;
  on, the track is `--brand` and the knob white. Its label follows it in
  Caption 1. From the confirmed editor mock-up.
- **Key chip** (in the help): 20 px high and at least 20 px wide, padding
  0 6, radius 4, `--bg-3` fill, 1 px `--stroke-1`, Caption 1 at weight 600.
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
  - text that is not a number is not applied; the drawing keeps the last
    value;
  - a number that breaks a rule is applied and drawn. The Python check
    marks it, so no rule is copied into JavaScript;
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
  - Updated for V2-3 and confirmed by the user on 2026-10-29
    ([editor.html](design/mockup/editor.html)).
  - **Top toolbar, 48 px:**
    - on the left: "← 검사 목록", then the title (the inspection name, with
      the save state and the video name below it);
    - the tools: 잡아끌기 (G), 연필 (P), 점 잇기 (L), 범위 (R), 메모 (M),
      이동 (H); then undo and redo;
    - the Glass picker in the middle;
    - 저장, 제출 and help on the right.
  - **Source warning (A9):** when opening the editor finds the source video
    changed, missing or unreadable, a message bar spans the window under
    the toolbar: `--warning-bg` with a 1 px `--warning-border` bottom edge,
    a `--warning` icon, the message and "다시 확인" (subtle, small). It
    stays until a check finds the video the same. The check runs in the
    background each time the editor opens; nothing shows while it runs.
  - **Main area:**
    - **Left column, flexible width:**
      - the graph (about 45 % of the height);
      - the context image (about 45 %);
      - a 32 px shared time axis with the playhead and editable range
        numbers. Empty stretches of the Oil line show as `--empty-mark`
        bars along its top edge.
      - The graph and the image always share the same time scale and
        horizontal scroll, which stay inside the analysed range. "전체
        보기" (small) in the graph's header returns to the whole range and
        the Glass's height (user, 2026-10-30).
      - A selected range is a `--selection-band` over both, with 1 px
        `--brand` edges that can be dragged.
    - **Right column, 360 px:**
      - the video, cropped to the Glass with the lines drawn over it, and
        its transport (frame steps, play, the speed field, range repeat,
        the time);
      - **편집:** the line kind the pencil and the point line draw (Oil,
        Foam, 참조); the grab width with `[` `]`; the grab shape
        (부드럽게, 뾰족하게, or Alt while dragging); the pencil's "수평·수직"
        switch; the snap switch with its reach. Below them, the selected
        range with "<line> 선 지우기 (Delete)" naming the chosen line,
        "판단 불가 (U)" and "판단 불가 풀기", wrapping inside the column, or
        the point line in progress with its keys. Another tool lets the
        range go;
      - **Glass:** the empty stretches, "cannot judge", the valid share
        against the Recipe's minimum, FULL and EMPTY, and "이전/다음 빈
        구간" (N);
      - the judgment panel (computed result, override, reason; V2-4);
      - **메모:** the Glass's memos in time order, each a 20 px numbered
        `--memo` pin, its time (Caption 1, `--fg-3`) and its text; a click
        brings the time into view and opens the memo;
      - **분석:** the range, the compressor start (dragged on the graph),
        the Recipe copy, and "범위 바꿔 다시 분석…". With unsaved edits it
        asks to save them first: the re-analysis keeps the saved edits.
      - **Memos:** the memo tool (M) opens the memo dialog at a click on the
        graph or the context image, for a new memo at that time and
        height; a click on a pin opens that memo. On the graph a pin is a
        10 px `--memo` circle with its number in white Caption 1 at weight
        600, 22 px above its point (below it near the top) on a 1 px stem.
        The memo dialog (480 px) has the time in its title, a text area
        of up to 500 characters with its count, and "삭제" (subtle, for an
        existing memo), "취소" and "확인" (primary, or Ctrl+Enter). Undo
        covers adding, changing and deleting.
      - **The compressor marker** moves with the grab tool: a press within
        5 px of it (a line under the pointer comes first; the cursor shows
        `ew-resize`) drags it in 0.1 s steps inside the analysis range.
        The 분석 panel shows the time it was moved from. A re-analysis
        starts from the moved time.
- **Inspection list:** the first screen.
  - **Toolbar, 48 px:** the title "검사" on the left; "Recipe", "새 검사"
    (primary) and help on the right.
  - **Body:** one panel with a table: the inspection, the Recipe, the
    creation time and the state (badge and reason). A row opens with
    "열기".
    - The inspection cell shows its name with the video name below it, or
      the video name alone when it has no name; then the folder name
      (monospace caption).
  - **Below the table:** the Inspections folder path, with "폴더 열기".
- **Recipe picker:** a 720 px dialog after the video is picked.
  - The video name, its frame size and its length.
  - The Recipe table, as in the Recipe list. A Recipe of another frame size
    is greyed out (`--fg-disabled`) with the reason below its name, and
    cannot be picked.
  - Footer: "이 영상으로 새 Recipe 만들기" (subtle) on the left; "취소" and
    "다음" (primary) on the right.
- **Analysis setup:** minimum 1280 × 800, laid out like the Recipe screen.
  - **Top toolbar, 48 px:** "← 검사 목록" and the title (새 검사 · video
    name, with the state and the Recipe below) on the left; the problem
    count in `--error`, "분석 시작" (primary) and help on the right.
  - **Left column:** a 32 px header with the video name, frame size and
    length; the frame view with the Recipe screen's Glass editing (§4);
    a 40 px transport whose scrub bar shows the analysis range (a
    `--range-fill` band with `--range-edge` edges, between "시작" and "끝"
    marks in `--range-edge`) and the compressor start ("기동", in
    `--compressor`), then the time and the speed field.
  - **Right column, 360 px:**
    - 검사 이름, marked "선택": a text field. Its caption says that the
      name shows in the list and names the folder, and how the folder is
      named without one. Once the folder exists, the field is read-only
      (user, 2026-10-29);
    - Recipe: its name and each Glass with its mode, and "바꾸기";
    - 분석 범위: start and end time fields, with the length and the number
      of samples below;
    - 압축기 기동: a time field, with whether it is required;
    - Glass 위치, "이 검사에만 적용": the Glass list (a changed Glass shows
      a "Recipe와 다름" badge), the selected Glass's position fields and
      "Recipe 위치로 되돌리기".
  - **Keys:** `[` and `]` set the range start and end to the time on
    screen; they are the same in Korean input mode.
  - **Re-analysis** (from the editor's "범위 바꿔 다시 분석…"): the same
    screen, with "← 편집기" instead of "← 검사 목록" and "다시 분석" as the
    primary button. Under 분석 범위, a caption lists the saved edits the
    new range would drop; "다시 분석" asks first when it drops any. The
    editor opens again when the analysis is done or on "← 편집기".
- **Analysis progress:** a 480 px dialog over the setup: the video, the
  Glass count and the range; the progress bar; a caption that the result
  opens when done and that cancelling keeps the settings; "취소".
- **Recipe list:** the same window.
  - **Toolbar, 48 px:** "← 검사 목록" and the title "Recipe" on the left;
    "새 Recipe" (primary) and help on the right.
  - **Body:** one panel with a table: name, Glass names, frame size,
    modified date. A row opens on double-click or with "열기".
  - **Below the table:**
    - files that could not be read, each with its reason, in `--error`;
    - the Recipes folder path, with a "폴더 열기" button.
- **Recipe screen:** minimum 1280 × 800.
  - **Top toolbar, 48 px:**
    - "← 목록" and the Recipe name with its save state, on the left;
    - "영상 열기" next to them;
    - the problem count in `--error`, "저장" (primary) and help, on the
      right.
  - **Main area:**
    - **Left column, flexible width:**
      - a 32 px header: the source video name, the saved reference-frame
        time, and the hint "저장하면 지금 보이는 프레임이 기준이 됩니다";
      - the frame view (§4);
      - a 40 px transport: previous frame, play/pause, next frame, a
        scrub bar with a "기준" mark at the saved reference time, the
        time in `mm:ss.s`, and the speed field (§4).
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
