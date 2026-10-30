// The report header's fields, 압축기 모델 and 시험 종류 (Product SSOT §7), in the setup's and the
// editor's 검사 정보. A new inspection's go out with "분석 시작"; once its folder exists, each change
// is saved at once, apart from the edits' "저장" (agent's choice, 2026-10-30).
import * as api from "./api.js";
import { el } from "./ui.js";

const KEYS = [["compressor_model", "압축기 모델"], ["test_type", "시험 종류"]];
const MAXIMUM_LENGTH = 60;  // domain/inspection.py MAXIMUM_HEADER_LENGTH
const SAVE_DELAY_MS = 500;

/** The two fields side by side; onInput(key, text) on every keystroke, onDone() when one is left. */
export function headerFields(header, onInput, onDone = () => {}) {
  return el("div", { class: "grid2" }, ...KEYS.map(([key, label]) => {
    const input = el("input", { "aria-label": label, maxlength: MAXIMUM_LENGTH, placeholder: "비워 두어도 됩니다" });
    input.value = header[key] ?? "";
    input.addEventListener("input", () => onInput(key, input.value));
    input.addEventListener("change", onDone);
    input.addEventListener("keydown", (event) => { if (event.key === "Enter") input.blur(); });
    return el("div", { class: "field" }, el("span", { class: "label" }, label), el("div", { class: "input" }, input),
      el("span", { class: "err", "data-err": key }));
  }));
}

/** Saves an existing inspection's header shortly after typing stops, one request at a time, so the
 * last text typed is the last one saved. */
export class HeaderSaver {
  constructor(onSaved, onFailed) {
    this.onSaved = onSaved;    // (inspection detail) => void
    this.onFailed = onFailed;  // (message) => void
    this.waiting = null;       // { id, header } not sent yet
    this.timer = 0;
    this.sent = Promise.resolve();
  }

  change(inspectionId, header) {
    this.waiting = { id: inspectionId, header: { ...header } };
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.flush(), SAVE_DELAY_MS);
  }

  /** Send what is waiting now; resolves when every save so far has answered. */
  flush() {
    clearTimeout(this.timer);
    const waiting = this.waiting;
    this.waiting = null;
    if (waiting) {
      this.sent = this.sent.then(async () => {
        try {
          const result = await api.call("POST", `/api/inspections/${encodeURIComponent(waiting.id)}/header`, waiting.header);
          if (result.ok) this.onSaved(result.data);
          else this.onFailed(result.data.error ?? `HTTP ${result.status}`);
        } catch (error) {
          this.onFailed(error.message);
        }
      });
    }
    return this.sent;
  }
}
