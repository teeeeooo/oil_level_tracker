# Golden Video Regression Structure

Real golden fixtures are intentionally not fabricated. Add short, redistributable clips under `tests/golden/<case>/` with:

- `video.*`
- `recipe.oilrecipe`
- `annotations.json`
- `README.md` containing source/license/test conditions

`annotations.json` should contain timestamp, expected FillState, acceptable oil-air/foam y range, expected event and whether low confidence is acceptable. Integration tests should compare ranges rather than exact pixels and should preserve the original clip hash in the annotation file.
