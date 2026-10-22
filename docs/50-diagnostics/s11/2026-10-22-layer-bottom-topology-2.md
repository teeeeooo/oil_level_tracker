# LBT-2 — layer-bottom topology with a Foam-visible fill guard

**Status: DRAFT 2026-10-22 — not frozen; awaits the user's
[decisions](#decisions-for-the-user).** Step 5 (B) of the Mac-only order in the
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

## Proposed protocol (draft)

**Unchanged from LBT-1:**
- the [LBW-3 witness](2026-10-20-layer-bottom-witness-3.md#changed-unit-one-change-only);
- the ordered-lower context;
- E1 (no Oil above the layer bottom in context);
- the context-limited support consumer.

**New, F — the Foam-visible fill guard (`OIL-PHASE-FILL`).**
- **Rule:** a fill chain cannot confirm a fill while a recent Foam row lies above
  its last row in that frame. "Recent and above" means a Foam material identity
  row whose seed age is ≤ 3 s, with the last row at or below it plus the
  existing lower separation (`foam_material_identity_tolerance + 2 px`).
- **Same relation as before:** this is the relation that already defines
  `ORDERED_LOWER_INTERFACE`. The LBW-3 unit is not needed.
- **Scope:** only the fill confirmation (T1–T3) is withheld. Other transitions
  (drain, release, refill closure, the top-exit route) are untouched. Once no
  recent Foam row lies above the last row, a chain confirms as today.
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

**Pre-run human review, review-013 (sample4, local).** Review-012 stays reserved
for the Windows Accum frames 672–677.5 s.
- **Material:** ROI crops of sample4 39.5–56 s every 0.5 s, without detector
  overlays, prepared before any LBT-2 output exists.
- **Q1, Foam:** at which frames is a Foam layer visible above the Oil? This is
  the reference option (b) judges Foam changes against.
- **Q2, Oil at 54.5–56 s:** is the level near the unit (about Y820–830), near
  the official truth (about Y851–858), or not visible? The guard will change
  these unassessed frames, so P0 asks one targeted question; asking it before
  the run keeps it blind.

**Execution, as in LBT-1 plus two descriptive controls:**
- **sample4 (development):** the P5 capture check, then the baseline and the
  frozen 245 SOI withdrawals under the wrapper.
- **Descriptive:** base_sample_1 0–14.4 s and sample2 0–2 s (as in LBT-1),
  plus sample5 (water) and sample7 (milk froth) over their full windows. These
  are fills with Foam or froth, so they would show any guard activation.
- **Not part of this approval:** Windows, top-exit v3 and the fill-owner gate.

**Contract checks before reading results:**
- with F off, the output equals LBT-1's;
- F withholds a confirmation only under a recent Foam row above the last row,
  and never touches another transition;
- out-of-context and Foam-free frames are unchanged;
- the existing phase, resolver, authority and tracklet suites run under the
  wrapper with activation counts.

**Evaluation:**
- **Unchanged:** P0 C1 ±5.2 px and LBT-1's controls.
- **Foam changes:** judged against review-013 Q1, under option (b).
- **54.5–56 s:** judged against review-013 Q2.
- **Stop policy:** the user's choice, below.

**Outcome classes:**
- **P:** publication recovered and no stop rule fired. S2 may be proposed later.
- **G':** a fill is still confirmed under Foam.
- **M:** the SFR-1 mixing returns.
- **L:** another later owner keeps publication wrong.

No tuning, widening or time/Y/Glass exception follows the results.

**Windows (S2):** step 7 only. Review-012 comes first, then a separate go.

**Predicted from the readings:**
- the baseline equals LBT-1's up to 54.0 s;
- at 54.5 s F withholds the confirmation; what 54.5–56 s then publish (in-unit
  rows about Y820–829, other rows, or nothing) is not predicted;
- `all_oil-f001185` keeps its 40 s Y865.5;
- the Foam changes stay close to LBT-1's, and may grow at 54.5–56 s where Oil
  becomes published.

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

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`, `SEQUENCE-COMPOSITION`
- Failure-registry entries: `S11-F01`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F10`
- First harmful stage: G — `OIL-PHASE-FILL`: the 27 % proximity rule confirms a fill from an in-unit row under a visible Foam row (54.5 s Y820 under Y808). The 40 s condition — `OIL-SELECTOR`/`OIL-TRACKLET`: with the level's 39.5 s row withdrawn, a lower-structure tracklet wins in a frame outside the context. Foam changes — `SEQUENCE-COMPOSITION`: Foam publication follows Oil publication (`S11-F06`).
- Existing feature coverage: reuses LBT-1's witness, context, E1, support consumer, runner, controls and P0 bounds unchanged. F reuses the Foam material identity row, the 3 s seed-age limit and the lower separation (`foam_material_identity_tolerance + 2 px`) that already define `ORDERED_LOWER_INTERFACE`, and the existing fill confirmation profile. Top-exit v3 and the contested fill-owner gate stay OFF.
- Execution scope: desk review of LBT-1's kept `comparison.json`, `layers.json` and per-condition rows, and of the sample4 truth files; no run, capture or new output. The proposed run is described but not approved.
- Logic-map impact: NONE — a draft protocol; no code or owner changes.
- Failure-registry impact: NONE — the readings map to existing entries (`S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`); no new mechanism or failure.
