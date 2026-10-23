# LBT-2 — layer-bottom topology with a Foam-visible fill guard

**Status: COMPLETE — outcome P: no stop rule fired under the frozen N
([result](#results-and-decision)).** The user chose every recommendation
([decision](#decision--2026-10-22)) and answered review-013
([result](#review-013-result--2026-10-22)). After the result the user answered
the 52 s/54.5 s question: the two readings use different Foam/Oil boundaries
([answer](#user-answer-two-boundaries--2026-10-23)), and the user chose the strict
one for the Oil output ([decision](#decision--2026-10-23)). The
[protocol](#protocol-frozen-2026-10-22), the tool
`tests/diagnostics/s11_layer_bottom_topology_2.py` and its tests were frozen
together at `1447cd6` before the run. Step 5 (B) of the Mac-only order in the
[Work Plan](../../00-project/work-plan.md), started by the user on 2026-10-22.
This draft reads only LBT-1's kept records and the sample4 truth files. It makes
no run, detector change or new output. It succeeds
[LBT-1](2026-10-20-layer-bottom-topology.md#results-and-decision).

## Why a second protocol

LBT-1 gave the best sample4 baseline of the layered-Foam line, and closed on
three open items:
1. **G, fill geometry:** a layer bottom inside the 27 % entrance band was read as
   a completed fill;
2. **Foam coupling (`S11-F06`):** Foam publication followed Oil publication in a
   few withdrawal conditions;
3. **40 s:** one withdrawal condition newly selected the opposed Y865.5.

Two earlier decisions shape the successor:
- **Option (b) (user, 2026-10-20):** a Foam change no longer stops the run by
  itself. It is judged against truth or a human review, and only a wrong change
  stops.
- **The Foam-visible fill guard (option A, 2026-10-20):** the user proposed "do
  not infer FULL while a Foam layer is visible above the level". It was deferred
  because defining the observable top (B) might make it unnecessary.

B did not make it unnecessary. In
[OTR-1](2026-10-21-full-observable-top-review.md#decision-record--2026-10-21)
the user chose D2 = S: the 27 % proximity rule (T1–T3) stays as the cap, and
top-exit only adds a FULL publication route. G therefore still occurs on
sample4, and OTR-1 records it as a separate follow-up.

## Desk readings from LBT-1's kept records

Closed run `sample/output/s11-layer-bottom-topology-20261020-001`: the
`comparison.json` controls, `layers.json` and the per-condition rows. sample4
geometry: ellipse top Y798, height 104, so the 27 % band ends at Y826.

**G at 54.5 s.**
- **The unit top moves for one frame:** B is Y828 at 54.0 s, Y820 at 54.5 s and
  Y829 at 55.0 s.
- **The Y820 row:** it belongs to tracklet 100:0021 and holds
  `ordered_lower_interface` authority, 12 px below the Foam row Y808. It ends an
  anchored fill chain inside the band, giving `FILL_SPAN_CONFIRMED`
  (`unknown_fill_anchored`).
- **The cap:** 54.5–56 s become UNKNOWN (`FILLED_CAP_VETO`). The ordinary run
  published Y851–852 there.
- **After 54.5 s F would not act:** no Foam row is present at 55 s, and at
  55.5–56 s the Foam rows (Y837–838) lie below the unit. Whether a later row
  would confirm a fill cannot be read from the kept report.

**The 40 s condition (`all_oil-f001185`, all Oil at 39.5 s withdrawn).**
- **The two arms:** the ordinary arm keeps the level's tracklet (1:0000) at 40–41.5 s
  (Y831–836). LBT-1 selects the lower-structure tracklet 80:0014 at
  40–40.5 s (Y865.5/864), then returns to 1:0000 at 41.5 s.
- **Why E1 cannot act:** 40 s is outside the context, because the Foam row (Y840)
  is not above the unit (B Y832). At 40.5 s the frame is in context, but E1
  removes only rows above B, and Y864 is below it.
- **The same condition elsewhere:** LBT-1 also fixed two of its points. At 52 s
  the wrong Y862 became the accepted Y833, and at 44 s a gap became Y842
  (accepted Y844).

**Net over the 246 conditions (controls only).**

| Change | Count |
|---|---|
| Opposed control newly selected | 1 (40 s Y865.5, `all_oil-f001185`) |
| Opposed control no longer selected | 685, in 231 conditions: 40 s Y865.5 in 227, 42 s Y868 in 229, 44 s Y822 in 229 |

**Foam changes against each condition's ordinary arm.**
- **Where:** six conditions (LBT-1's text says five): `all_oil-f001170`,
  `all_oil-f001380`, `all_foam-f001200`, `all_foam-f001290`, `all_foam-f001350`
  and `all_foam-f001560`.
- **Added:** 12 Foam values, at 44–46 s and 52.5–53 s (Y808–820).
- **Removed:** 3 Foam values, at 41.0 s (Y819), 44.5 s (Y820) and 46.0 s (Y812).
- **Truth:** none at these frames (see below), so option (b) needs a human
  review before they can be judged.

**Truth near the layered window.**
- **P0 controls** (target correspondence): the level is Y833–844 at 38–52 s.
- **Official `sample4.oiltruth`** (2026-08-01, five frames): FOAMING_VISIBLE at
  every frame. At 49 s Oil is Y855 and the Foam front Y824; at 56 s Oil is
  Y858.5 and the Foam front Y810.
- **The two disagree** by 14 px or more around 49–52 s. P0 is the current evaluation
  authority. **54.5–56 s are unassessed in P0**, and the official truth there
  is closer to the ordinary Y851–852 than to the unit.

## Decisions for the user

1. **G:** add F as LBT-2's third change (recommended; the user's own 10/20
   proposal)? The alternatives are OTR-1's option T, a broader rule that needs
   Windows controls first, or no change, accepting the false cap as a known
   limit.
2. **Stop policy.**
   - **S, LBT-1's rule:** any opposed or wrong target newly selected in any
     condition, or any wrong Foam change, closes the run. The prediction is
     that it closes again on the 40 s condition, and probably on the three
     Foam removals if review-013 shows Foam there.
   - **N, the P0 net procedure** (adopted 2026-10-20): the baseline must gain
     no A. The 245 conditions are scored A/B/C/U against their ordinary arms
     and compared net. Every new A or wrong Foam change is listed with its
     owner, not waived. The run closes if the baseline gains an A or the net
     does not improve.
   - **Recommended: N.** The single-condition rule has closed TPA-1, LBQ-1 and
     LBT-1 on the same small stress set. N still reports the 40 s A by name.
3. **Review-013 before the run:** prepare the sample4 39.5–56 s crops and ask
   Q1 and Q2?
4. **Controls:** add sample5 and sample7 as descriptive guard controls?

After the answers, the protocol, tool and tests are frozen in one commit before
any run.

## Decision — 2026-10-22

The user chose every recommendation:
1. **F** is LBT-2's third change.
2. **Stop policy N**, the P0 net procedure.
3. **Review-013 before the run.** The material is prepared (managed run
   `sample/output/s11-review013-sample4-20261022-001`); Q2 asks for an open
   reading rather than a choice between the two candidates.
4. **sample5 and sample7** join the descriptive controls.

The user answered review-013 the same day; the protocol below is frozen with
the answers.

## Review-013 result — 2026-10-22

[Reply record](2026-10-22-review-013-sample4-reply.json), with the
[user-marked zoom](2026-10-22-review-013-sample4-user-marking.png) kept byte for
byte.
- **Q1:** a Foam layer is visible above the Oil in all 34 frames, 39.5–56.0 s.
- **Q2:** the user dotted the surface ("대략적으로"). Read as source Y:

  | Frame | Marked surface | Near the centre (x 575–615) |
  |---|---|---|
  | 54.5 s | Y849–859 | Y857–859 |
  | 55.0 s | Y843–859 | Y853–859 |
  | 55.5 s | Y847–859 | Y855–859 |
  | 56.0 s | Y850–860 | Y859–860 |

**Against the other readings:**
- **Agree:** the official truth at 56 s (Oil Y858.5) and the ordinary output
  (Y851–852) lie on the marked surface.
- **The 2026-10-09 labels:** Y833 (54.0 s), Y837 (55.5 s) and Y838 (56.0 s) are
  internal Foam texture, above the marked surface.
- **The unit:** at Y820–829 it lies 20–30 px above the surface, inside the Foam.
- **Open:** at 52 s the references put the level at Y833 (accepted) and call
  Y862 wrong (CAF-1). The user marks the surface at Y857–860 near the centre
  2.5 s later. Either the level moves in between, or the readings describe
  different boundaries. LBT-2 applies each judgment at its own frame and does
  not resolve this.
  **Answered 2026-10-23:** different boundaries ([answer](#user-answer-two-boundaries--2026-10-23)).

## Protocol (frozen 2026-10-22)

Run with `.venv/bin/python -m tests.diagnostics.s11_layer_bottom_topology_2 --work <work>`
in a managed run.

**Unchanged from LBT-1:**
- the [LBW-3 witness](2026-10-20-layer-bottom-witness-3.md#changed-unit-one-change-only);
- the ordered-lower context;
- E1 (no Oil above the layer bottom in context);
- the context-limited support consumer.

**F — the Foam-visible fill guard (`OIL-PHASE-FILL`).**
- **Rule:** the fill confirmation T1 (OPEN/FILLING → FILLED_BARRIER by span) is
  withheld while the chain's last row lies at least the existing lower
  separation (`foam_material_identity_tolerance + 2 px`) below that frame's Foam
  material identity row, seeded within 3 s.
- **Same relation as before:** row, seed age and separation are the values that
  define `ORDERED_LOWER_INTERFACE`. The LBW-3 unit is not used.
- **Where:** a wrapper on `_fill_confirmation_profile`, whose only caller is the
  T1 qualification. The refill closures T2/T3, the releases and every other
  transition are untouched. Once no recent Foam row lies above the last row, a
  chain confirms as today.
- **Why it is physically sound:** FULL in the truth means Oil fills the Glass
  and no boundary is visible. A visible Foam layer above the level shows that
  the Glass is not Oil-full at that moment.

**Accepted risks, recorded before running:**
- **A stopgap:** a level that stays near the top *without* Foam still gets the
  false cap. That needs a change to the cap rule itself (OTR-1's option T, a
  provisional cap), which needs Windows FULL-suffix controls.
- **False Foam (`S11-F07`):** a false Foam row above a real full level would
  withhold a true fill confirmation (`S11-F05`). The Windows BASE refill has no
  Foam in its truth, so no effect is expected there. Only a Windows run can
  show it.
- **The 40 s condition** is not addressed by any change here.

**Execution:**
- **sample4 (development):** the P5 capture check, then the baseline and the
  frozen 245 SOI withdrawals under the wrapper.
- **Descriptive:**
  - base_sample_1 0–14.4 s and sample2 0–2 s, confirmed UNKNOWN, as in LBT-1;
  - sample5 0–54.8 s and sample7 0–44.378 s, confirmed EMPTY with their frozen
    ROI Recipes. These are fills with Foam or froth, so they would show any
    guard activation.
- **Not part of this approval:** Windows, top-exit v3 and the fill-owner gate.

**Contract checks:**
- **Done before freezing:**
  - LBT-2's focused tests (39) and LBT-1's (13) pass;
  - ten resolver, phase, authority and tracklet suites pass plainly and under
    the wrapper (320 each), with zero E1, support or F activations.
- **In the run, before results are read:**
  - the P5 capture;
  - the inert features change nothing;
  - with F off, the baseline equals LBT-1's kept baseline (rows and events);
  - the runner reproduces the saved SOI rows, and its row and event
    verification passes.

**References, all user judgments.** C1 is 5.2 px (5 % of the 104 px diameter).

| Source | Accepted | Wrong |
|---|---|---|
| LBT-1's frozen controls | 38 s Y844, 40 s Y841, 42 s Y839, 42.5 s Y835, 44 s Y844, 49.5 s Y841 (practical), 52 s Y833 | 38 s Y880/882/887, 40 s Y865.5, 42 s Y868, 44 s Y822 |
| LBQ-1 | | 42.5 s Y805 |
| CAF-1 | | 51.0 s Y861.5, 51.5 s Y862, 52.0 s Y862 |
| 2026-10-09 reply (internal Foam texture) | | 54.0 s Y833, 55.5 s Y837, 56.0 s Y838 |
| Review-013 Q2, marked surface ± C1 | 54.5 s Y844.2–864.3, 55.0 s Y837.4–864.3, 55.5 s Y841.7–864.6, 56.0 s Y844.6–865.4 | outside the band |

**Scoring, per condition, reference frame and arm:**
- **C:** inside the band, or within C1 of an accepted value.
- **A:** within C1 of a wrong value, or a published value outside the band.
- **B:** no published Oil where an accepted value or a band exists.
- **U:** any other published value.
- **Pairs:** a unit is *worse* when the trial gains an A or loses a C, and
  *better* when it loses an A or gains a C; otherwise it is the same.
- **Foam, option (b) against Q1:** Q1 has Foam visible in every frame of
  39.5–56.0 s. A Foam value added there is right, one removed there is wrong,
  and a moved value or a change outside the window is U.

**Stop rules N.** The run closes without promotion on any of:
- a failed contract check;
- the baseline gains an A;
- over the 245 withdrawal conditions, worse units are at least as many as
  better ones;
- wrong Foam changes are at least as many as right ones, when any is wrong.

Every worse unit and wrong Foam change is listed with its owner.

**Outcome classes:**
- **P:** no stop rule fired. S2 may be proposed later.
- **G':** a fill is still confirmed under a recent Foam row.
- **M:** the SFR-1 mixing returns.
- **L:** a later owner keeps publication wrong.

No tuning, widening or time/Y/Glass exception follows the results.

**Expected, recorded before the run:**
- **Up to 54.0 s:** the baseline equals LBT-1's.
- **54.5–56 s:** F withholds the 54.5 s confirmation. The in-unit rows there
  (Y820–829) lie in the Foam by review-013 and the 10/09 labels.
  - If the selection publishes them, the baseline gains an A and N stops (L).
  - If it publishes the marked surface, those frames become C.
- **The 40 s condition:** `all_oil-f001185` keeps Y865.5 (one worse unit),
  against LBT-1's 685 removed opposed selections.
- **Foam:** under Q1, LBT-1's 12 additions are right and its 3 removals wrong.

**Windows (S2):** step 7 only. Review-012 comes first, then a separate go.

## Results and decision

Tool `1447cd6`. Managed run `sample/output/s11-layer-bottom-topology-2-20261022-001`
(closed; 13 files kept, the ordinary baseline CSVs reused from SOI).
- `comparison.json` SHA-256 `1c8fa3e7ef85b86a22818ab5b717ad17604993212cb6c2c29845a46333bd6884`
- `evaluation.json` SHA-256 `736542b6852546c8e2209ca3783084b23b0f38b3858e096f65affed975c01f7f`
- `layers.json` SHA-256 `544c636594c10c0fededcf01a539ade9ba2a66ee163a5e92a8f54ce2e0658a26`

**Contracts: all PASS.**
- Before freezing: focused tests 39 and 13; ten suites 320, plainly and under
  the wrapper, with zero activations.
- In the run:
  - the sample4 capture equals P5;
  - the inert features change nothing;
  - **with F off, the baseline equals LBT-1's kept baseline** (rows and events);
  - the ordinary arm reproduces all 246 SOI records; 55,596 rows and 14,498
    event links verify.

**Verdict under N: no stop rule fired → outcome P.**

| Rule | Result |
|---|---|
| The baseline gains an A | none |
| Worse ≥ better over the 245 conditions | 8 worse against 800 better (2,618 the same) |
| Wrong Foam changes ≥ right ones | 3 wrong against 12 right |

**Baseline against the ordinary arm.**

| Reference | Ordinary | LBT-2 | Unit |
|---|---|---|---|
| 40 s Y841 / opposed Y865.5 | Y865.5 (A) | Y831 (U) | better |
| 42 s Y839 / opposed Y868 | Y868 (A) | Y835 (C) | better |
| 44 s Y844 / opposed Y822 | Y822 (A) | Y842 (C) | better |
| 54.5–56 s, review-013 surface | Y851–852 (C) | Y851–852 (C) | same |

- **F acted once in the baseline:** at 54.5 s it withheld the confirmation from
  the Y820 row under the Foam row Y808. No fill was confirmed anywhere, so
  54.5–56 s stay open and publish the review-013 surface through tracklet
  89:0017. Outcome G is gone; no G' was seen.
- **Report extrema:** the wrong minimum 42 s Y868 disappears. The extrema
  become max 51.5 s Y828 and min 2.0 s Y858 (an unchanged pre-Foam value), as
  in LBT-1.
- **Mixing:** only LBT-1's out-of-context rows of tracklet 1:0000 at 39.5–40 s,
  where the Foam row lies below the unit. The SFR-1 mixing does not return (no
  M).

**Population.**
- **E1's gains stand:** 685 opposed selections removed in 231 conditions, as in
  LBT-1.
- **F:** it acted in 234 of 246 conditions, each time at the same 54.5 s row
  (Y820 under Y808).
- **Worse units, all listed with owners.** None involves F; LBT-1 published the
  same values in these conditions.

  | Condition | Frames | LBT-2 | Ordinary arm | Owner |
  |---|---|---|---|---|
  | `all_oil-f001185` | 40 s | Y865.5 (A) | Y831 (U) | lower-structure tracklet 80:0014, outside the context |
  | `all_oil-f001620` (all Oil at 54.0 s withdrawn) | 54.5, 55.0, 56.0 s | Y820, Y829, Y874 (A) | Y851 (C) | tracklet 89:0017 |
  | `all_foam-f001620` (all Foam at 54.0 s withdrawn) | 54.0, 54.5, 55.0, 56.0 s | Y828, Y820, Y829, Y873 (A) | none, then Y851 (C) | tracklet 89:0017 |

  In the two 54.0 s conditions, the established tracklet links to the nearer
  row inside the Foam once its 54.0 s observation is missing
  (`OIL-TRACKLET`, `S11-F04`).
- **Foam (option (b) against Q1):**
  - right: 12 Foam values added, at 44–46 s and 52.5–53 s, in five conditions;
  - wrong: 3 removed, at 41.0 s (`all_foam-f001200`) and 44.5/46.0 s
    (`all_foam-f001350`), where Foam publication follows Oil (`S11-F06`).

  These are the same changes as LBT-1's.

**Descriptive controls.**

| Control | Initial state | Unit frames | E1 / support / F | Change |
|---|---|---|---|---|
| base_sample_1 0–14.4 s | UNKNOWN | 0 of 30 | 0 / 0 / 0 | none |
| sample2 0–2 s | UNKNOWN | 2 of 5 | 13 / 2 / 0 | 2.0 s Y603 → no output, as in LBT-1 |
| sample5 0–54.8 s | EMPTY | 10 of 111 | 0 / 0 / 0 | none |
| sample7 0–44.378 s | EMPTY | 0 of 90 | 0 / 0 / 0 | none |

**Post-hoc comparison, not part of the verdict.** LBT-1's kept population
scored by the same frozen rules stops: 921 worse against 784 better. 912 of its
worse units are the false cap's C → B at 54.5–56 s in 228 conditions. F removes
exactly these.

**Reading.**
- **F does what it was designed for.** It removes the false fill cap under a
  visible Foam layer without touching another transition. The baseline keeps
  E1's gains at 40–44 s and returns to the review-013 surface at 54.5–56 s.
- **Limits, named and not waived:**
  1. 40 s: the lower structure wins after a withdrawn 39.5 s observation (one
     condition, outside the context).
  2. 54.0–56 s: association into the Foam after a withdrawn 54.0 s observation
     (two conditions).
  3. Foam removals at 41.0/44.5/46.0 s (two conditions, `S11-F06`).
  4. sample2 2.0 s Y603 → no output (descriptive; the provisional truth calls
     2.0 s full-like).
  5. The open 52 s versus 54.5 s level question in the
     [review-013 result](#review-013-result--2026-10-22).
     Answered 2026-10-23: two boundaries
     ([answer](#user-answer-two-boundaries--2026-10-23)); the user chose the
     strict one ([decision](#decision--2026-10-23)).
- **Next, as frozen:** P allows proposing Windows S2 in step 7. Review-012 (the
  unread Accum frames 672–677.5 s) comes first, then a separate go. No tuning
  or widening follows.

S11 ACTIVE / O2 OPEN / FIELD FAIL is unchanged by this local result.

## User answer: two boundaries — 2026-10-23

Asked after the result whether the level moves between 52 s (accepted Y833)
and 54.5 s (marked Y857–860 near the centre), or the two readings describe
different boundaries. Reply, verbatim:

> 두 판단이 서로 다른 경계를 본 거야. foam을 엄격하게 구분하면 Y=833까지만 foam이고 나머지는 oil로 판정한거고, foam을 러프하게 구분하면 Y=857-860 까지를 foam이라고 본거고

**What it settles.** The level does not move. The scene holds two Foam/Oil
boundaries, and each judgment used one:
- **Strict:** Foam reaches only about Y833; everything below is Oil.
- **Rough:** Foam reaches about Y857–860; the zone in between counts as Foam.

No owner says yet which boundary the Oil output follows. The
[SSOT spec](../../rotary_oil_level_tracker_ssot_spec.md) asks for the real Oil
surface to be told apart from Foam and defines the Foam front as the top of the
foam/bubbly-oil region, but it does not place the Oil surface inside such a
layer.

**The references mix both.** The answer covers 52 s and 54.5 s; the rest of
this table is the assistant's reading of each record against Y833 and
Y857–860.

| Boundary | References |
|---|---|
| Strict | P0 52 s Y833 (accepted) and 49.5 s Y841 (practical). CAF-1's wrong Y861.5–862 at 51.0–52.0 s lies at the rough depth. |
| Rough | Official `sample4.oiltruth` (2026-08-01): Oil Y848.5–860.5 at 0, 15, 30, 49 and 56 s. Review-013 Q2 at 54.5–56 s. The 2026-10-09 reply, which puts Foam on both sides of Y833–838 at 54–56 s; LBT-2 scored these values as wrong Oil. |
| Not recorded | The 38–44 s accepted values and the 40 s rejection (2026-10-07): no rough reading exists there. |

The 14 px gap between P0 and the official truth around 49–52 s
([desk readings](#desk-readings-from-lbt-1s-kept-records)) is this split.
Values above both boundaries (42.5 s Y805, 44 s Y822) and the tentative lower
rim (42 s Y868) are wrong under either.

**The output follows both.** Baseline Oil Y in the kept population:

| Time | Ordinary | LBT-2 |
|---|---|---|
| 46.0–49.5 s | Y833–840 | Y833–840 |
| 50.0–51.5 s | none | Y828–833 |
| 52.0–53.5 s | Y829–833 | Y829–833 |
| 54.0 s | none | Y844 |
| 54.5–56.0 s | Y851–852 | Y851–852 |

The output steps 18 px down within one second at 54 s, where the level does
not move. Under either single definition one side of the step is wrong:
- **strict:** Y851–852 at 54.5–56 s lie 18–19 px below Y833;
- **rough:** Y833 at 49 s lies 22 px above the official Y855, and Y833 at 52 s
  lies 24–27 px above Y857–860.

**What it means for LBT-2.** The verdict stays as recorded: N was frozen with
these references, and nothing is re-scored. A read-only recount of the kept
population with the frozen `references`, `outcome` and `transition`
reproduces 800 better, 8 worse and 2,618 the same, and places them:

| Frames | Better | Worse | Reference basis |
|---|---|---|---|
| 40–44 s | 705 | 1 | 2026-10-07 and LBQ-1 values; 685 of the better units remove a rejected value |
| 49.5–52 s | 63 | 0 | strict |
| 54.0–56 s | 32 | 7 | rough |

- **The net does not hinge on the choice.** 458 of the 685 removals (42–44 s)
  drop values that are wrong under either definition. The 63 strict-based and
  39 rough-based units are small beside them.
- **54–56 s flips under strict.** If the strict boundary stays near Y833, the
  scored-A Y828 (54.0 s) and Y829 (55.0 s) in the two 54.0 s conditions lie
  within C1 of it, while the scored-C Y851–852 lie 18–19 px below it. Both
  baseline arms would then be wrong at 54.5–56 s. Under rough, the 63 units at
  49.5–52 s reverse instead.
- **F's premise holds under either.** Both readings put Foam above the level at
  54.5 s, so the Glass is not Oil-full there.

**What the choice decides:**
- the Oil target the detector must hold through 54 s, where the current output
  changes boundary;
- how sample4's references are labelled for the next comparison;
- which boundary review-012 asks for in Windows Accum 672–677.5 s, the reviewed
  layered-Foam interval.

**Decision for the user: which boundary does the Oil output follow?**
- **S, strict:** Oil starts below the dense Foam (Y833 here), and the bubbly
  zone is Oil. It matches P0, the current evaluation authority, and the output
  through 53.5 s. Needs a strict reading at 54.5–56 s. The official file's Oil
  values, review-013 Q2 and the 2026-10-09 reading stay as rough readings.
- **R, rough:** Oil is the top of the clear oil (Y857–860 here), and the bubbly
  zone belongs to Foam. It matches the official file, review-013 and the output
  from 54.5 s. Needs P0's 49.5–52 s values and CAF-1's 51–52 s judgment
  re-labelled.
- **Both, no switch:** either boundary scores C, but one episode keeps one
  boundary. Needs a new continuity rule in the P0 contract.

**Recommended: S.** In the user's words the strict reading separates Foam
rigorously and review-013's reading loosely. S keeps P0 as it is; only
54–56 s needs a new reading. R is right if the product needs the clear-oil level without the
bubbly zone.

## Decision — 2026-10-23

The user chose **S, strict** ("엄격으로 가자"). The rule is recorded in the
[product spec](../../rotary_oil_level_tracker_ssot_spec.md#다층-유체의-추적-대상),
the [P0 contract](../../30-validation/s11-interface-observability-witness-validation.md#oil-reference-boundary-inside-a-foam-layer--2026-10-23)
and the [Windows reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).

**sample4 Oil references under S:**

| Status | References |
|---|---|
| Kept | P0's accepted values at 38–52 s and their wrong values; LBQ-1 42.5 s Y805; CAF-1's 51.0–52.0 s Y861.5–862. The 38–44 s values count as strict, since no rough reading exists there. |
| Rough, not Oil references | The official file's Oil values; review-013 Q2. The 2026-10-09 values Y833–838 stay "not the Foam front" but are no longer wrong Oil. |
| Missing | 54.0–56.0 s, to be read by review-014. Read 2026-10-23: see the [review-014 result](#review-014-result--2026-10-23). |

**Known error under S:** both baseline arms publish the rough boundary at
54.5–56 s (Y851–852, 18–19 px below Y833), so the output changes boundary at
54 s. Its first harmful stage is not located. LBT-2's verdict is unchanged.
Narrowed by the [review-014 result](#review-014-result--2026-10-23): the error
is 54.0–54.5 s only.

**Next:** [review-014](2026-10-23-review-014-sample4.json) reads the strict
boundary at 52.0–56.0 s on one raw x5 [zoom](2026-10-23-review-014-sample4-zoom.png)
(managed run `sample/output/s11-review014-sample4-20261023-001`, no overlay);
52.0 s checks consistency with the answer's Y833. Its reply sets the strict
references at 54.0–56.0 s.

## Review-014 result — 2026-10-23

The user marked the strict boundary on every frame of the
[zoom](2026-10-23-review-014-sample4-zoom.png) and replied, verbatim:
"경계 표시해서 첨부했고." The
[marked image](2026-10-23-review-014-sample4-user-marking.png) is kept byte for
byte; the [reply record](2026-10-23-review-014-sample4-reply.json) holds the
per-mark source coordinates. Each frame's reference band is the marks' Y range
between x 575 and 615 (the Glass centre), widened by C1 (5.2 px).

| Time | Strict marks, x 575–615 | Both baseline arms | Under S |
|---|---|---|---|
| 52.0 s | Y835.9–836.0 | Y833 | right |
| 52.5 s | Y832.8–834.3 | Y829 | right |
| 53.0 s | Y832.4–833.4 | Y829 | right |
| 53.5 s | Y835.0–836.5 | Y833 | right |
| 54.0 s | Y831.1–831.6 | LBT-2 Y844; ordinary none | LBT-2 about 13 px below |
| 54.5 s | Y833.9–835.7 | Y851 | 15–17 px below |
| 55.0 s | Y853.7–856.0 | Y851 | right |
| 55.5 s | Y854.0–857.7 | Y852 | right |
| 56.0 s | Y853.9–857.4 | Y851 | right |

**52.0 s check:** Y835.9–836.0 lies 3 px from the user's Y833, inside C1, so
the readings are used as asked.

**What it shows:**
- **The strict boundary moves at 55 s.** It holds near Y833 through 54.5 s,
  then lies about 20 px lower from 55.0 s.
- **The two boundaries meet from 55 s.** Review-013's rough marks at 55.0–56.0 s
  (Y852.5–860.2 at the centre) lie within 3–5 px of the strict ones. At 54.5 s
  they still differ by about 23 px.
- **The known error narrows to 54.0–54.5 s** (an uncertain reference; see the
  follow-up below). The output drops to the lower
  boundary one sample before the strict boundary moves: Y844 at 54.0 s (LBT-2
  arm) and Y851 at 54.5 s (both arms). From 55.0 s the published Y851–852 is
  right under S.
- **The two 54.0 s withdrawal conditions under S:**
  - 54.0 s Y828 is right;
  - 54.5 s Y820 and 55.0 s Y829 are above the band, so wrong;
  - 56.0 s Y873–874 is below it, so wrong.

  So the
  [two-boundary answer's](#user-answer-two-boundaries--2026-10-23) "54–56 s
  flips under strict" holds for 54.0 s only. LBT-2's verdict and recount are
  unchanged; nothing is re-scored.

**References under S:** the strict sample4 Oil references now cover 52.0–56.0 s
at the bands above, in the
[P0 contract](../../30-validation/s11-interface-observability-witness-validation.md#oil-reference-boundary-inside-a-foam-layer--2026-10-23).

**Follow-up answer (user, 2026-10-23), verbatim:**

> 사실 보기 나름인거같음. 53.5s 까지는 촘촘한 경계가 확실하게 구분되는데, 54s부터는 촘촘한 경계가 무너지기 시작해서 정확하게 어디라고 특정하기 어려움. 다만 55s에서는 확연하게 그 경계가 보이지 않아서 foam 영역의 최하단을 표시함.

**Reference confidence, by this answer:**
- **52.0–53.5 s, clear:** the dense-Foam bottom is distinct.
- **54.0–54.5 s, uncertain:** the dense boundary starts to break up. The marks
  are approximate, so the early drop there is not a decisive error.
- **55.0–56.0 s, no dense boundary:** the marks are the bottom of the Foam
  region.

So "the strict boundary moves at 55 s" above is a change of what is visible,
not a measured 20 px step: the dense boundary breaks up over 54–55 s.

**Open, for the user:** the 54.0–54.5 s early drop. Its first harmful stage is
not located. LBT-2's F action at 54.5 s (Y820 under the Foam row Y808) and the
54.0 s association limit sit in the same second.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`, `SEQUENCE-COMPOSITION`
- Failure-registry entries: `S11-F01`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F10`
- First harmful stage: G — `OIL-PHASE-FILL`: the 27 % proximity rule confirms a fill from an in-unit row under a visible Foam row (54.5 s Y820 under Y808). The 40 s condition — `OIL-SELECTOR`/`OIL-TRACKLET`: with the level's 39.5 s row withdrawn, a lower-structure tracklet wins in a frame outside the context. Foam changes — `SEQUENCE-COMPOSITION`: Foam publication follows Oil publication (`S11-F06`).
- Existing feature coverage: reuses LBT-1's witness, context, E1, support consumer, runner, controls and P0 bounds unchanged. F reuses the Foam material identity row, the 3 s seed-age limit and the lower separation (`foam_material_identity_tolerance + 2 px`) that already define `ORDERED_LOWER_INTERFACE`, and the existing fill confirmation profile. Top-exit v3 and the contested fill-owner gate stay OFF.
- Execution scope: desk review of LBT-1's kept `comparison.json`, `layers.json` and per-condition rows, and of the sample4 truth files. Review-013 material: one managed run decoded 34 sample4 frames and wrote raw ROI crops with a source-Y ruler; the user's reply was read from the marked image. Freeze: the tool and focused tests are committed with the protocol; the focused tests and ten resolver/phase suites (plain and under the wrapper, zero activations) ran before freezing. Run: one managed development run at `1447cd6` (sample4 baseline and 245 SOI conditions under the wrapper, the layer report, the N evaluation, and four descriptive controls through the ordinary analysis entry); no Windows run, top-exit or fill-owner gate. After the result (2026-10-23): a read-only recount of the kept population with the frozen evaluation functions, grouped by frame; no run and no output files. Review-014 material (2026-10-23): one managed run decoded 9 sample4 frames (52.0–56.0 s) and wrote a raw x5 zoom with a source-Y ruler. Review-014 reply (2026-10-23): the marks were read by differencing the marked image against the clean zoom, and compared with the kept LBT-2 trial baseline CSV and this record's ordinary-arm values; no run and no output files.
- Logic-map impact: NONE — a diagnostic wrapper under tests/diagnostics; no production code, owner or edge changes.
- Failure-registry impact: NONE — a diagnostic wrapper with no runtime mechanism; its limits map to existing entries (`S11-F04` association after a withdrawn row, `S11-F06` Foam following Oil, `S11-F05` for the guard's false-Foam risk) and are recorded here.
