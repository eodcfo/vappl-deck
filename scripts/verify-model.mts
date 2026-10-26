import {readFileSync,writeFileSync,mkdirSync,existsSync,readdirSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync,execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const root=fileURLToPath(new URL('..',import.meta.url));
const {financeModelSchema}:typeof import('../model/finance-contract.js')=createRequire(import.meta.url)('../model/finance-contract.js');
const source=readFileSync(join(root,'model/pf_model.json'),'utf8');
const model=financeModelSchema.parse(JSON.parse(source));
const artifact=join(root,'.agent-artifacts','model-verification',`${new Date().toISOString().replaceAll(':','-')}-${process.pid}`);
mkdirSync(artifact,{recursive:true});
const valid=JSON.stringify(model);
const nullable=structuredClone(model);
const nullableKeys=new Set(['irr_pct','project_irr_pct','spread_over_debt_pct','payback_years','money_multiple','dscr','min_dscr','avg_dscr','min_dscr_post_moratorium','avg_dscr_post_moratorium','achieved_min_dscr']);
function clearMetrics(value:unknown){
 if(!value || typeof value!=='object')return;
 for(const [key,child] of Object.entries(value)){
  if(nullableKeys.has(key))Reflect.set(value,key,null);else clearMetrics(child);
 }
}
clearMetrics(nullable);
const {'Karnal Phase 1 — term loan':karnalAllocation,...withoutKarnalAllocation}=model.cgtmse_allocation.single_borrower_plan;
const {rv,...withoutRv}=model;
const fixtures:{name:string;json:string;valid:boolean}[]=[
 {name:'valid-producer-json',json:source,valid:true},
 {name:'nullable-metrics',json:JSON.stringify(nullable),valid:true},
 {name:'missing-allocation',json:JSON.stringify({...model,cgtmse_allocation:{...model.cgtmse_allocation,single_borrower_plan:withoutKarnalAllocation}}),valid:false},
 {name:'malformed-json',json:'{ broken',valid:false},
 {name:'missing-project',json:JSON.stringify(withoutRv),valid:false},
 {name:'missing-financing',json:JSON.stringify({...model,ggv:{...model.ggv,financing:undefined}}),valid:false},
 {name:'numeric-string',json:JSON.stringify({...model,meta:{...model.meta,bank_rate_pct:'11.5'}}),valid:false},
 {name:'wrong-units',json:JSON.stringify({...model,meta:{...model.meta,units:'INR crore'}}),valid:false},
 {name:'wrong-producer',json:JSON.stringify({...model,meta:{...model.meta,generator:'other.py'}}),valid:false},
 {name:'empty-years',json:JSON.stringify({...model,rv:{...rv,years:[]}}),valid:false},
 {name:'short-series',json:JSON.stringify({...model,ggv:{...model.ggv,years:model.ggv.years.slice(0,2)}}),valid:false},
 {name:'nonfinite-number',json:valid.replace(/"bank_rate_pct":-?[\d.]+/, '"bank_rate_pct":1e999'),valid:false},
 {name:'invalid-null',json:JSON.stringify({...model,karnal:{...model.karnal,capex_total:null}}),valid:false},
];
const networkGuard=join(root,'scripts/model-network-guard.mts');
const controlLog=join(artifact,'network-control-attempts.log');
const control=spawnSync(process.execPath,['--import',networkGuard,'--eval',"require('node:https').get('https://network-control.example.invalid')"],{cwd:root,encoding:'utf8',env:{PATH:process.env.PATH,PPTX_NETWORK_LOG:controlLog}});
writeFileSync(join(artifact,'network-control.stderr.log'),control.stderr||'');
const guardProved=control.status!==0&&existsSync(controlLog)&&readFileSync(controlLog,'utf8').includes('https.get');
if(!guardProved)throw new Error('The Node network guard did not reject the control request.');
const reports=[];
for(const fixture of fixtures){
 const input=join(artifact,fixture.name+'.json'),output=join(artifact,fixture.name+'-output');
 writeFileSync(input,fixture.json);
 const networkLog=join(artifact,fixture.name+'.network.log');
 const args=['--import',networkGuard,join(root,'model/build_pptx.js')];
 const run=spawnSync(process.execPath,args,{cwd:root,encoding:'utf8',timeout:60_000,env:{PATH:process.env.PATH,PPTX_MODEL_PATH:input,PPTX_OUTPUT_DIRECTORY:output,PPTX_NETWORK_LOG:networkLog}});
 writeFileSync(join(artifact,fixture.name+'.stdout.log'),run.stdout||'');
 writeFileSync(join(artifact,fixture.name+'.stderr.log'),run.stderr||'');
 const present=existsSync(output),count=present?readdirSync(output).filter(file=>file.endsWith('.pptx')).length:0;
 const networkAttempts=existsSync(networkLog)?readFileSync(networkLog,'utf8').trim().split('\n').filter(Boolean).length:0;
 const passed=networkAttempts===0&&!run.error&&(fixture.valid?run.status===0&&count===5:run.status!==0&&!present);
 reports.push({name:fixture.name,command:[process.execPath,...args],expectedValid:fixture.valid,exit:run.status,error:run.error?.message,outputDirectoryCreated:present,presentations:count,networkAttempts,passed});
}
const owned=['model/build_pptx.ts','model/pptx_lib.ts','model/finance-contract.ts','model/build_pptx.js','model/pptx_lib.js','model/finance-contract.js','model/pf_model.py','model/pf_model.json','tsconfig.model.json','scripts/verify-model.mts','scripts/model-network-guard.mts'];
const sourceHashes=Object.fromEntries(owned.map(file=>[file,createHash('sha256').update(readFileSync(join(root,file))).digest('hex')]));
writeFileSync(join(artifact,'report.json'),JSON.stringify({kind:'isolated-generator-process-e2e',revision:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),node:process.version,sourceHashes,reports,ownedOutputRoot:artifact,nodeNetworkGuardControlPassed:guardProved},null,2)+'\n');
console.log(`${reports.filter(row=>row.passed).length}/${reports.length} generator process cases pass. Evidence: ${join(artifact,'report.json')}`);
if(reports.some(row=>!row.passed))process.exitCode=1;
