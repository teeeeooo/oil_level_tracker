// The report's drawing (adapters/report). It is joined after render.js into the report's one module
// script, so it calls render.js's functions directly and imports nothing. Each Glass's panel comes
// from the report's data; the plots are drawn at their size on the page, which A4 fixes.
{
  const panels = JSON.parse(document.getElementById("reportData").textContent);
  const fill = (svg, width, height, content) => {
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.innerHTML = content;
  };
  for (const box of document.querySelectorAll(".plots")) {
    const index = Number(box.dataset.index);
    const panel = panels[index];
    const view = fitView(panel);
    const graph = box.querySelector(".graph svg"), context = box.querySelector(".context svg"), axis = box.querySelector(".axis svg");
    const [gw, gh] = [graph.clientWidth, graph.clientHeight];
    fill(graph, gw, gh, graphSvg(panel, view, gw, gh, `graph${index}`) + marksSvg({ memos: panel.memos }, view, gw, gh, `graph${index}`));
    const [cw, ch] = [context.clientWidth, context.clientHeight];
    fill(context, cw, ch, contextSvg(panel, view, cw, ch, `context${index}`));
    fill(axis, axis.clientWidth, 32, axisSvg(view, axis.clientWidth, { times: panel.times, empty: panel.empty }));
  }
}
