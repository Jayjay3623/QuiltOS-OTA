"""Publish only checksum-pinned Quilt source/notice assets, then verify GitHub digests."""
import argparse,hashlib,json,os,pathlib,re,subprocess,time,urllib.request
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
 for i,row in enumerate(selected):
  asset=download(row['asset'],row['sha256'],row['bytes'])
  subprocess.run(['gh','release','upload',tag,str(asset),'--repo',REPO,'--clobber'],check=True)
  asset.unlink();print('Verified and uploaded',i+1,'/',len(selected),row['asset'],flush=True)
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
