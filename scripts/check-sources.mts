import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';
import { isBuiltin } from 'node:module';
import ts from 'typescript';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const checked = new Set<string>();
const strictFlags = ['noImplicitAny', 'noImplicitThis', 'strictNullChecks', 'strictFunctionTypes', 'strictBindCallApply', 'strictPropertyInitialization', 'alwaysStrict', 'useUnknownInCatchVariables', 'strictBuiltinIteratorReturn'] as const;
for (const name of ["tsconfig.json", "tsconfig.tools.json", "tsconfig.model.json"]) {
  const filename = resolve(root, name);
  const raw = ts.readConfigFile(filename, ts.sys.readFile);
  if (raw.error) throw new Error('Cannot read ' + filename);
  const config = ts.parseJsonConfigFileContent(raw.config, ts.sys, dirname(filename));
  if (config.errors.length || !config.options.strict || config.options.noCheck || strictFlags.some(flag => config.options[flag] === false)) throw new Error('Source checking must remain strict: ' + filename);
  for (const path of config.fileNames) if (!/\.[cm]?jsx?$/.test(path) || config.options.checkJs) checked.add(path);
}
const generated = new Map(readFileSync(resolve(root, 'generated-source-owners.txt'), 'utf8').trim().split('\n').filter(line => line && !line.startsWith('#')).map(line => {
  const [output, owner] = line.split('|');
  if (!output || !owner || !checked.has(resolve(root, owner))) throw new Error('Generated output lacks a strict owner: ' + line);
  return [resolve(root, output), owner];
}));
const files = ts.sys.readDirectory(root, ['.ts', '.tsx', '.mts', '.cts', '.js', '.jsx', '.mjs', '.cjs'], ['node_modules', '.agent-artifacts', 'dist', 'build', 'coverage']);
for (const path of files) {
  if (!checked.has(path) && !generated.has(path)) throw new Error('Maintained source is not checked: ' + relative(root, path));
  if (!checked.has(path)) continue;
  const source = ts.createSourceFile(path, ts.sys.readFile(path) ?? '', ts.ScriptTarget.Latest, true);
  function inspect(node: ts.Node) {
    if (node.kind === ts.SyntaxKind.AnyKeyword ||
      ((ts.isAsExpression(node) || ts.isTypeAssertionExpression(node)) && node.type.getText(source) !== 'const'))
      throw new Error('Unchecked escape in maintained source: ' + relative(root, path));
    if (relative(root, path).startsWith('web/') || relative(root, path).startsWith('player/src/')) {
      if ((ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) && node.moduleSpecifier && ts.isStringLiteral(node.moduleSpecifier) &&
        (isBuiltin(node.moduleSpecifier.text) || /^(?:server-only|@aws-sdk|mongoose)(?:$|\/)/.test(node.moduleSpecifier.text)))
        throw new Error('Browser source imports server dependency: ' + relative(root, path));
    }
    ts.forEachChild(node, inspect);
  }
  inspect(source);
  if (/^[ \t]*\/{2,3}[ \t]*@ts-(?:ignore|nocheck|expect-error)/im.test(source.text))
    throw new Error('Suppression in maintained source: ' + relative(root, path));

}
console.log(`${files.length} source/generated files have strict owners.`);
