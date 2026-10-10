'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const {releaseAsset,download,unpack,validateResult,workspaceFile,summary}=require('./run');
const version='0.3.5',name=`fw-mem-guard-${version}-linux-x64.tar.gz`;
const metadata=()=>({tag_name:'v'+version,draft:false,assets:[{name,size:3,digest:'sha256:'+'a'.repeat(64),browser_download_url:`https://github.com/itainover-create/fw-mem-guard/releases/download/v${version}/${name}`}]});
test('Action requires exact release and digest; rejects hostile URLs, missing/duplicate assets and oversized download',()=>{
 assert.equal(releaseAsset(metadata(),version).name,name);
 for(const change of [m=>m.draft=true,m=>m.tag_name='v0.3.4',m=>m.assets=[],m=>m.assets.push(m.assets[0]),m=>delete m.assets[0].digest,m=>m.assets[0].browser_download_url='https://example.com/cli',m=>m.assets[0].size=1024**3]){const m=metadata();change(m);assert.throws(()=>releaseAsset(m,version));}
 assert.throws(()=>releaseAsset(metadata(),'latest'));assert.throws(()=>releaseAsset(metadata(),'../../secret'));
});
test('Action verifies actual downloaded bytes before execution',async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fwmg-action-test-')),original=global.fetch;
 try{
  const bytes=Buffer.from('abc');global.fetch=async()=>new Response(bytes,{status:200});
  const a=metadata().assets[0];a.digest='sha256:'+crypto.createHash('sha256').update(bytes).digest('hex');
  await download(a,path.join(dir,'ok'));assert.equal(fs.readFileSync(path.join(dir,'ok'),'utf8'),'abc');
  a.digest='sha256:'+'0'.repeat(64);await assert.rejects(()=>download(a,path.join(dir,'bad')),/verification failed/);
  a.size=2;await assert.rejects(()=>download(a,path.join(dir,'too-large')),/exceeds/);
  global.fetch=async()=>new Response('missing',{status:404});await assert.rejects(()=>download(a,path.join(dir,'missing')),/HTTP 404/);
 }finally{global.fetch=original;fs.rmSync(dir,{recursive:true,force:true});}
});
test('Action preserves exit 2 valid report, rejects invalid JSON, unknown schemas and execution errors',()=>{
 const report={schemaVersion:1,status:'pass',baseline:{flash:1,ram:1},current:{flash:2,ram:2},delta:{flash:1,ram:1},violations:[]};
 const result=()=>({status:0,stdout:JSON.stringify(report),stderr:''});
 assert.equal(validateResult(result()).status,'pass');
 for(const r of [{...result(),status:1},{...result(),status:2},{...result(),stderr:'error'},{...result(),stdout:'PASS'},{...result(),stdout:JSON.stringify({...report,schemaVersion:2})}])assert.throws(()=>validateResult(r));
 const fail={...report,status:'budget_exceeded',violations:[{memory:'ram',metric:'growth_bytes',actual:1,limit:0}]};
 assert.equal(validateResult({status:2,stdout:JSON.stringify(fail),stderr:''}).status,'budget_exceeded');
 assert.doesNotMatch(summary({...report,contributors:{objects:[{name:'/secret/local/path'}]}}),/secret/);
});
test('Action paths reject traversal and workflow-output injection',()=>{
 const root=path.resolve(os.tmpdir(),'workspace');assert.equal(workspaceFile(root,'directory/my project.fwmg.json'),path.join(root,'directory/my project.fwmg.json'));
 for(const p of ['../escape','/etc/passwd','report\nexit-code=0',''])assert.throws(()=>workspaceFile(root,p));
});
test('Action rejects archive symlinks and wrong root before extraction',{skip:process.platform==='win32'},()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fwmg-action-tar-'));
 try{
  const root=`fw-mem-guard-${version}-linux-x64`;fs.mkdirSync(path.join(dir,root));fs.symlinkSync('/tmp',path.join(dir,root,'link'));
  const archive=path.join(dir,'test.tar.gz');assert.equal(spawnSync('tar',['-czf',archive,'-C',dir,root]).status,0);
  assert.throws(()=>unpack(archive,dir,version),/Unsafe/);
  fs.unlinkSync(path.join(dir,root,'link'));fs.writeFileSync(path.join(dir,root,'safe'),'ok');
  assert.equal(spawnSync('tar',['-czf',archive,'-C',dir,root]).status,0);
  assert.throws(()=>unpack(archive,dir,'9.9.9'),/Unsafe/);
  assert.equal(unpack(archive,dir,version),path.join(dir,root));
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
