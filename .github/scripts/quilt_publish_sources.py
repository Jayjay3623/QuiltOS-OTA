"""Publish only checksum-pinned Quilt source/notice assets, then verify GitHub digests."""
import argparse,hashlib,json,os,pathlib,re,subprocess,time,urllib.request,urllib.parse,urllib.error
REPO='Jayjay3623/QuiltOS-OTA'
BUILDS={'cheetah':'1793891372','panther':'1793892852','bluejay':'1793896340'}
EXPECTED_COUNT=399
EXPECTED_BYTES=4334223887
p=argparse.ArgumentParser();p.add_argument('mode',choices=['create','upload','publish']);p.add_argument('--shard',type=int,default=0);a=p.parse_args()
assert os.environ['GITHUB_REPOSITORY']==REPO
base=os.environ['SOURCE_BASE'];assert re.fullmatch(r'https://[a-z0-9-]+\.trycloudflare\.com',base)
tag=os.environ['SOURCE_TAG'];assert re.fullmatch(r'sources-native-notices-[0-9-]+',tag)
manifest_sha=os.environ['SOURCE_MANIFEST_SHA'];sums_sha=os.environ['SOURCE_SUMS_SHA']
def gh(*args,json_output=False):
 result=subprocess.check_output(['gh',*args],text=True)
 return json.loads(result) if json_output else result

def download(name,sha,size=None):
 assert re.fullmatch(r'[A-Za-z0-9_.+-]+',name) and re.fullmatch(r'[0-9a-f]{64}',sha)
 path=pathlib.Path(name);partial=path.with_name(name+'.part')
 for attempt in range(4):
  try:
   req=urllib.request.Request(base+'/assets/'+sha+'/'+name,headers={'User-Agent':'Quilt-source-publisher'})
   total=0;digest=hashlib.sha256()
   with urllib.request.urlopen(req,timeout=90) as response,partial.open('wb') as output:
    for data in iter(lambda:response.read(1024*1024),b''):
     total+=len(data);assert total<2_000_000_000
     if size is not None:assert total<=size
     output.write(data);digest.update(data)
   assert digest.hexdigest()==sha,(name,'SHA-256 mismatch')
   if size is not None:assert total==size,(name,'Size mismatch')
   partial.replace(path);return path
  except Exception:
   partial.unlink(missing_ok=True)
   if attempt==3:raise
   time.sleep([2,5,15][attempt])
manifest_path=download('SOURCE-ARTIFACTS.json',manifest_sha,148459)
manifest=json.loads(manifest_path.read_text())
assert manifest['builds']==BUILDS and manifest['asset_count']==EXPECTED_COUNT
assert len(manifest['assets'])==EXPECTED_COUNT and manifest['bytes']==EXPECTED_BYTES
assert sum(x['bytes'] for x in manifest['assets'])==EXPECTED_BYTES
assert len({x['asset'] for x in manifest['assets']})==EXPECTED_COUNT
assert all(set(x)=={'asset','sha256','bytes','group','delivery_path'} for x in manifest['assets'])
sums=download('SOURCE-SHA256SUMS',sums_sha,58780)
assert sums.read_text()==''.join(x['sha256']+'  '+x['asset']+'\n' for x in manifest['assets'])
if a.mode=='create':
 existing=subprocess.run(['gh','release','view',tag,'--repo',REPO,'--json','isDraft,tagName'],capture_output=True,text=True)
 if existing.returncode==0:assert json.loads(existing.stdout)['isDraft'],'Refuse to mutate an already published source release'
 else:
  notes='Source and license-notice delivery for Pixel 7 (panther 1793892852), Pixel 7 Pro (cheetah 1793891372), and Pixel 6a (bluejay 1793896340). The catalog fixes each asset SHA-256 and its original directory layout. Includes matching WebView source and combined object work, captured application/native/kernel sources, and final installed notices. Internal operational notes and SDK binaries are excluded. Component licenses apply individually. This is a source release, not an installable OTA. Independent rebuilds, physical-device installation, and formal commercial legal clearance are not claimed. OTA release notes must identify their exact supported baseline and link this source delivery.'
  subprocess.run(['gh','release','create',tag,'--repo',REPO,'--draft','--prerelease','--target',os.environ['GITHUB_SHA'],'--title','QuiltOS corrected three-device sources and notices','--notes',notes],check=True)
 subprocess.run(['gh','release','upload',tag,str(manifest_path),str(sums),'--repo',REPO,'--clobber'],check=True)
 print('Draft source release and pinned catalog prepared')
elif a.mode=='upload':
 assert 0<=a.shard<4
 selected=[x for i,x in enumerate(manifest['assets']) if i%4==a.shard]
 release=gh('api','repos/'+REPO+'/releases/tags/'+tag,json_output=True)
 assert release['draft'],'Refuse to change a published source release'
 endpoint=release['upload_url'].split('{',1)[0]
 assert endpoint=='https://uploads.github.com/repos/'+REPO+'/releases/'+str(release['id'])+'/assets'
 existing={};page=1
 while True:
  batch=gh('api','repos/'+REPO+'/releases/'+str(release['id'])+'/assets?per_page=100&page='+str(page),json_output=True)
  existing.update({x['name']:x for x in batch})
  if len(batch)<100:break
  page+=1
 class NoRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*args,**kwargs):raise RuntimeError('Refuse to redirect an authenticated upload')
 opener=urllib.request.build_opener(NoRedirect())
 last_upload=0.0
 for i,row in enumerate(selected):
  name=row['asset'];old=existing.get(name)
  if old and old['state']=='uploaded' and old['size']==row['bytes'] and old.get('digest')=='sha256:'+row['sha256']:
   print('Preserved verified uploaded asset',name,flush=True);continue
  if old:
   # Only this draft's expected asset is replaced; originals remain on the build VM.
   gh('api','--method','DELETE','repos/'+REPO+'/releases/assets/'+str(old['id']))
  asset=download(name,row['sha256'],row['bytes'])
  for attempt in range(4):
   delay=5-(time.monotonic()-last_upload)
   if delay>0:time.sleep(delay)
   try:
    with asset.open('rb') as content:
     req=urllib.request.Request(endpoint+'?'+urllib.parse.urlencode({'name':name}),data=content,method='POST',headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2026-03-10','Content-Type':'application/octet-stream','Content-Length':str(row['bytes']),'User-Agent':'Quilt-pinned-source-publisher'})
     with opener.open(req,timeout=600) as response:uploaded=json.load(response)
    last_upload=time.monotonic()
    assert uploaded['name']==name and uploaded['size']==row['bytes'] and uploaded['state']=='uploaded'
    assert uploaded.get('digest') in (None,'sha256:'+row['sha256'])
    break
   except urllib.error.HTTPError as error:
    last_upload=time.monotonic()
    if error.code not in (403,429) or attempt==3:raise
    # Respect server backoff and keep four shards below secondary write limits.
    time.sleep(max(60,min(300,int(error.headers.get('Retry-After','60')))))
  asset.unlink();print('Verified and uploaded',i+1,'/',len(selected),name,flush=True)
else:
 release=gh('api','repos/'+REPO+'/releases/tags/'+tag,json_output=True)
 assert release['draft'] and release['prerelease']
 assets=[];page=1
 while True:
  batch=gh('api','repos/'+REPO+'/releases/'+str(release['id'])+'/assets?per_page=100&page='+str(page),json_output=True)
  assets.extend(batch)
  if len(batch)<100:break
  page+=1
 expected={x['asset']:{'sha256':x['sha256'],'bytes':x['bytes']} for x in manifest['assets']}
 expected.update({'SOURCE-ARTIFACTS.json':{'sha256':manifest_sha,'bytes':148459},'SOURCE-SHA256SUMS':{'sha256':sums_sha,'bytes':58780}})
 actual={x['name']:x for x in assets};assert set(actual)-{'source-upload-verification.json'}==set(expected),(len(actual),len(expected),set(actual)-set(expected),set(expected)-set(actual))
 checks=[]
 for name,row in expected.items():
  asset=actual[name];assert asset['size']==row['bytes'] and asset['state']=='uploaded',name
  assert asset.get('digest')=='sha256:'+row['sha256'],(name,asset.get('digest'))
  checks.append({'asset':name,'github_asset_id':asset['id'],'bytes':asset['size'],'sha256':row['sha256'],'github_digest_matches':True})
 report={'scope':'GitHub release asset sizes and server-reported SHA-256 digests checked against the pinned source catalog; not a legal certification or independent rebuild','builds':BUILDS,'release':release['html_url'],'assets_verified':len(checks),'checks':checks,'complete':True}
 path=pathlib.Path('source-upload-verification.json');path.write_text(json.dumps(report,indent=2)+'\n')
 subprocess.run(['gh','release','upload',tag,str(path),'--repo',REPO,'--clobber'],check=True)
 subprocess.run(['gh','release','edit',tag,'--repo',REPO,'--draft=false'],check=True)
 print('Published checksum-verified source delivery:',release['html_url'])
