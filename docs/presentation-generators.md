# Presentation source and model boundary

`model/pf_model.py` owns financial assumptions and calculations. Its exchange artifact is `model/pf_model.json`. `model/render.py` renders financial HTML. `model/build_pptx.ts` and `model/pptx_lib.ts` render the five PowerPoint presentations. JavaScript and source maps beside these TypeScript files are checked-in compiler output so the existing `node model/build_pptx.js` command still works.

`model/finance-contract.ts` validates the Python JSON before creating an output directory or presentation. Known project, financing, scenario, allocation and yearly-series fields are required; numeric strings, nonfinite numbers, wrong producer/unit metadata and insufficient series are rejected. Optional financial results such as undefined IRR, payback and DSCR remain nullable. The schema checks exchange structure; it does not independently calculate or certify financial results. Update it alongside intentional producer-shape changes.

Money stays in INR lakh unless a producer field explicitly ends in `_cr`. The shared `cr`/`crN` formatters divide lakh values by 100 for crore display. Percentages and multiples use separate formatters. Rendering retains the existing display aggregation and rounding; it does not add another financial calculation engine.

Use Node 22.18 or newer with `npm ci --ignore-scripts`.

| Command | Result |
| --- | --- |
| `npm run build:model` | Emit the two generators, contract and their source maps |
| `npm run check` | Strict browser/tool/model checks; compare browser and model output against fresh compilation; validate current Python JSON. Writes no financial or presentation output |
| `npm run verify:model` | Run the actual generator in isolated processes against valid and malformed local JSON; keep presentations, per-case logs, source hashes, revision and report under `.agent-artifacts/model-verification/` |
| `npm run build:pptx` | Rebuild JavaScript, then regenerate `pptx/*.pptx` from the model |

For isolated or alternate output, set `PPTX_MODEL_PATH` to an inspected local JSON fixture and `PPTX_OUTPUT_DIRECTORY` to an owned disposable directory. Verification retains only its own fixture/output directory as evidence. It uses a restricted child-process environment and a Node network guard for sockets, HTTP(S), HTTP/2, datagrams and fetch. A blocked HTTPS control call proves the guard before the generator runs; every generator case must make zero network attempts. Delete only that run directory when its evidence is no longer required.

The migration evidence is retained under `.agent-artifacts/typescript-program/`. An isolated copy of the original Python source reproduced the checked-in JSON exactly. Both original JavaScript generators and their TypeScript replacements generated five real presentations containing 55 slides. Every uncompressed XML/chart/layout/workbook part, including nested Excel packages, matched byte for byte after normalizing only creation/modification timestamps. ZIP container timestamps and compression metadata were compared through their uncompressed contents. Original and replacement files, raw differences, part hashes and diagnostics are retained. Both runs reported no overflow or overlap. Existing `pptx/` files and financial Python/JSON sources were preserved.

This establishes generator and package equivalence. Native PowerPoint/LibreOffice rendering, font substitution and printed-page appearance were not exercised. No financial assumptions, deployment, commit or live data/provider action was changed by this migration.
