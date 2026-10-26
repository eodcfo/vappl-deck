import {mkdtemp,readdir,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
const root=fileURLToPath(new URL('..',import.meta.url));
const scratch=await mkdtemp(join(tmpdir(),'vappl-model-compiler-'));
try {
 const result=spawnSync(process.execPath,[join(root,'node_modules/typescript/lib/tsc.js'),'--project',join(root,'tsconfig.model.json'),'--outDir',scratch],{cwd:root,encoding:'utf8'});
 if(result.error)throw result.error;
 if(result.status!==0)throw new Error(result.stdout+result.stderr);
 const files=(await readdir(scratch)).filter(file=>/\.js(?:\.map)?$/.test(file));
 if(files.length!==6)throw new Error('Expected the two generators and finance contract, with source maps.');
 for(const file of files){
  const expected=await readFile(join(scratch,file));
  const actual=await readFile(join(root,'model',file));
  if(!expected.equals(actual))throw new Error(`model/${file} differs from its TypeScript owner. Run npm run build:model.`);
 }
 const {financeModelSchema}:typeof import('../model/finance-contract.js')=createRequire(import.meta.url)('../model/finance-contract.js');
 financeModelSchema.parse(JSON.parse(await readFile(join(root,'model/pf_model.json'),'utf8')));
 console.log('Verified six model JavaScript/source-map outputs and the Python model JSON contract. No presentation or financial output was written.');
} finally {
 await rm(scratch,{recursive:true,force:true});
}
