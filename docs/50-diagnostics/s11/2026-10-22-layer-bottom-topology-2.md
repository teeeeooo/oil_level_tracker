# LBT-2 — layer-bottom topology with a Foam-visible fill guard

**Status: FROZEN 2026-10-22 before any run.** The user chose every
recommendation ([decision](#decision--2026-10-22)) and answered review-013
([result](#review-013-result--2026-10-22)). The
[protocol](#protocol-frozen-2026-10-22), the tool
`tests/diagnostics/s11_layer_bottom_topology_2.py` and its tests are
committed together. Step 5 (B) of the Mac-only order in the
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

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`, `SEQUENCE-COMPOSITION`
- Failure-registry entries: `S11-F01`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F10`
- First harmful stage: G — `OIL-PHASE-FILL`: the 27 % proximity rule confirms a fill from an in-unit row under a visible Foam row (54.5 s Y820 under Y808). The 40 s condition — `OIL-SELECTOR`/`OIL-TRACKLET`: with the level's 39.5 s row withdrawn, a lower-structure tracklet wins in a frame outside the context. Foam changes — `SEQUENCE-COMPOSITION`: Foam publication follows Oil publication (`S11-F06`).
- Existing feature coverage: reuses LBT-1's witness, context, E1, support consumer, runner, controls and P0 bounds unchanged. F reuses the Foam material identity row, the 3 s seed-age limit and the lower separation (`foam_material_identity_tolerance + 2 px`) that already define `ORDERED_LOWER_INTERFACE`, and the existing fill confirmation profile. Top-exit v3 and the contested fill-owner gate stay OFF.
- Execution scope: desk review of LBT-1's kept `comparison.json`, `layers.json` and per-condition rows, and of the sample4 truth files. Review-013 material: one managed run decoded 34 sample4 frames and wrote raw ROI crops with a source-Y ruler; the user's reply was read from the marked image. Freeze: the tool and focused tests are committed with the protocol; the focused tests and ten resolver/phase suites (plain and under the wrapper, zero activations) ran before freezing. No LBT-2 population run has been made at the freeze.
- Logic-map impact: NONE — a draft protocol; no code or owner changes.
- Failure-registry impact: NONE — the readings map to existing entries (`S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`); no new mechanism or failure.
