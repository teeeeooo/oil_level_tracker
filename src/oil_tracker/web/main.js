// The page's entry: wires every screen, then opens the inspection list (Product SSOT §3).
import * as editor from "./editor.js";
import * as frame from "./frame.js";
import * as inspections from "./inspections.js";
import * as nav from "./nav.js";
import * as recipe from "./recipe.js";
import { notify } from "./ui.js";

async function start() {
  nav.wire();
  frame.wire();
  editor.init(inspections.showList, inspections.openSetup);
  inspections.init({
    openRecipes: recipe.showList,
    newRecipeWith: recipe.newRecipeWith,
    openEditor: editor.open,
  });
  try {
    await recipe.init(inspections.showList);
  } catch (error) {
    nav.show("inspectionsView");
    notify("inspectionsNotice", error.message, "error");
    return;
  }
  await inspections.showList();
}

start();
