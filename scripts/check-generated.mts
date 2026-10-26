import { mkdtemp, readdir, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const root = fileURLToPath(new URL('..', import.meta.url));
const output = process.argv[2];
if (!output) throw new Error('Pass the repository-relative compiler output directory.');
const scratch = await mkdtemp(join(tmpdir(), 'eod-compiler-output-'));
try {
  const result = spawnSync(process.execPath, [join(root, 'node_modules/typescript/lib/tsc.js'), '--project', join(root, 'tsconfig.json'), '--outDir', scratch], { cwd: root, encoding: 'utf8' });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(result.stdout + result.stderr);
  const files = (await readdir(scratch, { recursive: true })).filter(file => file.endsWith('.js'));
  if (!files.length) throw new Error('Compiler emitted no browser artifacts.');
  for (const file of files) {
    const expected = await readFile(join(scratch, file));
    const actual = await readFile(resolve(root, output, file));
    if (!expected.equals(actual)) throw new Error(`${output}/${file} differs from its TypeScript source. Rebuild before release.`);
  }
  console.log(`Verified ${files.length} browser artifacts against strict TypeScript compilation.`);
} finally {
  await rm(scratch, { recursive: true, force: true });
}
