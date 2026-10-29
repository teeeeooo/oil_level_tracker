// Which screen is on show, its help (DESIGN.md §4 "Help") and where keys go.
import { $, typing } from "./ui.js";
import * as frame from "./frame.js";

const screens = new Map();  // view id -> { help title, onKey(event), onHelp() }
let current = null;

export function register(viewId, screen) {
  screens.set(viewId, screen);
}

export function show(viewId) {
  for (const node of document.querySelectorAll(".view")) node.hidden = node.id !== viewId;
  current = viewId;
}

export function currentView() {
  return current;
}

export function openHelp() {
  const screen = screens.get(current);
  for (const section of document.querySelectorAll("#help [data-help]")) section.hidden = section.dataset.help !== current;
  $("helpTitle").textContent = `도움말 · ${screen?.title ?? ""}`;
  frame.stopPlayback();
  frame.toggleSpeedMenu(false);
  $("help").showModal();
}

function onKey(event) {
  if (document.querySelector("dialog[open]")) return;  // a dialog takes its own keys; Esc closes help
  if (event.key === "F1" || (event.key === "?" && !typing())) {
    event.preventDefault();
    openHelp();
    return;
  }
  if (event.key === "Escape" && !$("speedMenu").hidden) {
    frame.toggleSpeedMenu(false);
    return;
  }
  screens.get(current)?.onKey?.(event);
}

export function wire() {
  for (const button of document.querySelectorAll(".help-open")) button.addEventListener("click", openHelp);
  const help = $("help");
  $("helpClose").addEventListener("click", () => help.close());
  help.addEventListener("click", (event) => {  // a click on the backdrop lands on the dialog itself
    const box = help.getBoundingClientRect();
    const inside = event.clientX >= box.left && event.clientX <= box.right && event.clientY >= box.top && event.clientY <= box.bottom;
    if (!inside) help.close();
  });
  document.addEventListener("keydown", onKey);
}
