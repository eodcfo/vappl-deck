# Repository map

- Browser TypeScript: `web/`. Browser JavaScript in `assets/` is generated, preserve it as deployment output and rebuild instead of editing it.
- Run `npm run check` for strict source/tool checking and compiler-output equivalence. It starts no application or provider.
- Build with `npm run build:web` using Node 22.18+.
- Preserve unrelated dirty changes and existing deployment behavior. No commit, push or deployment is implicit.
- `model/pf_model.py` owns financial calculations; `model/pf_model.json` is its exchange artifact. `model/render.py` owns generated financial HTML. Preserve INR lakh/crore units.

- Presentation owners are `model/build_pptx.ts`, `model/pptx_lib.ts` and `model/finance-contract.ts`. Rebuild their JavaScript/source maps with `npm run build:model`. `npm run check` verifies compiler-output equivalence.
- `npm run verify:model` runs isolated local generator processes and retains repeatable evidence. It does not write existing presentations. `npm run build:pptx` intentionally regenerates `pptx/`; use explicit owned `PPTX_OUTPUT_DIRECTORY` for verification. See [the presentation source map](docs/presentation-generators.md).
