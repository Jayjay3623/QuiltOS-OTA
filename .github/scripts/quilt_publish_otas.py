"""Publish verified exact-base Quilt OTAs, then atomically update their feeds."""
import argparse,base64,hashlib,json,os,pathlib,re,subprocess,time,urllib.request
REPO='Jayjay3623/QuiltOS-OTA'
CONFIG={'cheetah':('privacy','1792829003','1793891372'),'panther':('android17','1793198660','1793892852'),'bluejay':('creator','1793774474','1793896340')}
SOURCE_TAG='sources-native-notices-1793891372-1793892852-1793896340'
SOURCE_SHA='5298703b11e3a6b5b42279146af33e3fbedb36db42e51e86f97140a8ae904a95'
p=argparse.ArgumentParser();p.add_argument('mode',choices=['create','upload','publish']);p.add_argument('--device',choices=list(CONFIG));a=p.parse_args()
assert os.environ['GITHUB_REPOSITORY']==REPO
base=os.environ['SOURCE_BASE'];assert re.fullmatch(r'https://[a-z0-9-]+\.trycloudflare\.com',base)
manifest_sha=os.environ['OTA_MANIFEST_SHA'];assert re.fullmatch(r'[0-9a-f]{64}',manifest_sha)
def gh(*args,json_output=False):
 result=subprocess.check_output(['gh',*args],text=True)
 return json.loads(result) if json_output else result

def refresh_base():
 global base
 response=gh('api','repos/'+REPO+'/contents/.github/quilt-artifact-transfer.json?ref=main',json_output=True)
 locator=json.loads(base64.b64decode(response['content']))
 assert locator['source_tag']==SOURCE_TAG and locator['source_manifest_sha256']==SOURCE_SHA
 assert re.fullmatch(r'https://[a-z0-9-]+\.trycloudflare\.com',locator['source_base'])
 base=locator['source_base']

def request(method,path,body):
 file=pathlib.Path('api-request.json');file.write_text(json.dumps(body))
 return gh('api','--method',method,path,'--input',str(file),json_output=True)

def fetch(url,path,expected,size=None):
 assert re.fullmatch(r'[A-Za-z0-9_.+-]+',path.name)
 for attempt in range(4):
  partial=path.with_name(path.name+'.part')
  try:
   total=0;digest=hashlib.sha256()
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Quilt-verified-OTA-publisher'}),timeout=90) as response,partial.open('wb') as f:
    for block in iter(lambda:response.read(1024*1024),b''):
     total+=len(block);assert total<2_000_000_000
     assert total<=(size if size is not None else 1024*1024)
     f.write(block);digest.update(block)
   assert digest.hexdigest()==expected
   if size is not None:assert total==size
   partial.replace(path);return path
  except Exception:
   partial.unlink(missing_ok=True)
   if attempt==3:raise
   refresh_base()
   time.sleep([2,5,15][attempt])

def download(row):
 name=row['asset'];assert re.fullmatch(r'[A-Za-z0-9_.+-]+',name) and re.fullmatch(r'[0-9a-f]{64}',row['sha256'])
 return fetch(base+'/assets/'+row['sha256']+'/'+name,pathlib.Path(name),row['sha256'],row['bytes'])

def release(tag):return gh('api','repos/'+REPO+'/releases/tags/'+tag,json_output=True)
def release_assets(rel):
 rows=[];page=1
 while True:
  batch=gh('api','repos/'+REPO+'/releases/'+str(rel['id'])+'/assets?per_page=100&page='+str(page),json_output=True);rows+=batch
  if len(batch)<100:return {x['name']:x for x in rows}
  page+=1

def verify_assets(actual,expected,allowed_extra=()):
 assert set(actual)-set(allowed_extra)==set(expected),(set(actual)-set(expected),set(expected)-set(actual))
 for name,row in expected.items():
  got=actual[name];assert got['state']=='uploaded' and got['size']==row['bytes'],name
  assert got.get('digest')=='sha256:'+row['sha256'],(name,got.get('digest'))

refresh_base()
manifest_path=fetch(base+'/assets/'+manifest_sha+'/OTA-ARTIFACTS.json',pathlib.Path('OTA-ARTIFACTS.json'),manifest_sha)
assert manifest_path.stat().st_size<1024*1024
manifest=json.loads(manifest_path.read_text());assert manifest['all_three_host_verified'] and not manifest['physical_device_installation_tested']
assert manifest['source_tag']==SOURCE_TAG and manifest['source_manifest_sha256']==SOURCE_SHA
assert len(manifest['devices'])==3 and {x['device'] for x in manifest['devices']}==set(CONFIG)
for device in manifest['devices']:
 d=device['device'];variant,old,new=CONFIG[d]
 assert (device['variant'],device['base_incremental'],device['target_incremental'])==(variant,old,new)
 assert device['tag']==d+'-native-notices-'+new and len(device['assets'])==3
 assert len(device['feeds'])==2 and {x['body']['base_incremental'] for x in device['feeds']}=={old,new}
 assert device['assets'][0]['asset']=='quilt-'+d+'-'+new+'-from-'+old+'.zip'
 for entry in device['feeds']:
  body=entry['body'];assert body['schema_version']==1 and body['device']==d and body['variant']==variant
  assert body['base_incremental'] in (old,new)
  assert entry['path']=='docs/api/v2/'+d+'/'+variant+'/'+body['base_incremental']+'.json'
  if body['base_incremental']==new:assert body['response']==[]
  else:
   assert len(body['response'])==1;offer=body['response'][0];ota=device['assets'][0]
   assert (offer['device'],offer['variant'],offer['base_incremental'],offer['incremental'])==(d,variant,old,new)
   assert offer['no_wipe'] is True and offer['sha256']==ota['sha256'] and offer['size']==ota['bytes']
   assert offer['url']=='https://github.com/'+REPO+'/releases/download/'+device['tag']+'/'+ota['asset']
   assert offer['installation']=='user_confirmation' and len(offer['payload_properties'])==4
   assert 0<offer['payload_offset']<offer['size'] and 0<offer['payload_size']<offer['size']
# Source availability and every source-asset digest are checked before OTA publication.
source=release(SOURCE_TAG);assert not source['draft'] and source['prerelease']
source_actual=release_assets(source);source_manifest_asset=source_actual['SOURCE-ARTIFACTS.json']
assert source_manifest_asset.get('digest')=='sha256:'+SOURCE_SHA
source_manifest_path=fetch(source_manifest_asset['browser_download_url'],pathlib.Path('SOURCE-ARTIFACTS.json'),SOURCE_SHA,148459)
source_manifest=json.loads(source_manifest_path.read_text());assert source_manifest['asset_count']==399
expected_sources={x['asset']:x for x in source_manifest['assets']}
expected_sources.update({'SOURCE-ARTIFACTS.json':{'sha256':SOURCE_SHA,'bytes':148459},'SOURCE-SHA256SUMS':{'sha256':'55f9bc7e2a6f4dfbb53427abaa3e395a878d937b971b3b54c222f69cfc23ba0f','bytes':58780}})
verify_assets(source_actual,expected_sources,{'source-upload-verification.json'})
metadata={'asset':'OTA-ARTIFACTS.json','sha256':manifest_sha,'bytes':manifest_path.stat().st_size}
if a.mode=='create':
 for device in manifest['devices']:
  existing=subprocess.run(['gh','release','view',device['tag'],'--repo',REPO,'--json','isDraft'],capture_output=True,text=True)
  if existing.returncode==0:
   if not json.loads(existing.stdout)['isDraft']:
    verify_assets(release_assets(release(device['tag'])),{x['asset']:x for x in device['assets']+[metadata]},{device['device']+'-github-upload-verification.json'})
   continue
  subprocess.run(['gh','release','create',device['tag'],'--repo',REPO,'--draft','--prerelease','--target',os.environ['GITHUB_SHA'],'--title',device['title'],'--notes',device['notes']],check=True)
 print('Three drafts prepared; published sources verified')
elif a.mode=='upload':
 assert a.device
 device=next(x for x in manifest['devices'] if x['device']==a.device);rel=release(device['tag'])
 if not rel['draft']:
  verify_assets(release_assets(rel),{x['asset']:x for x in device['assets']+[metadata]},{device['device']+'-github-upload-verification.json'})
 else:
  subprocess.run(['gh','release','upload',device['tag'],str(manifest_path),'--repo',REPO,'--clobber'],check=True)
  for row in device['assets']:
   path=download(row);subprocess.run(['gh','release','upload',device['tag'],str(path),'--repo',REPO,'--clobber'],check=True);path.unlink()
 print('Verified OTA assets uploaded:',a.device)
else:
 validated=[]
 for device in manifest['devices']:
  rel=release(device['tag']);actual=release_assets(rel);expected={x['asset']:x for x in device['assets']+[metadata]};report_name=device['device']+'-github-upload-verification.json'
  verify_assets(actual,expected,{report_name})
  validated.append((device,rel,expected,report_name))
 for device,rel,expected,report_name in validated:
  if rel['draft']:
   report={'scope':'Published source inventory and GitHub OTA asset digests checked before feed changes; no physical installation or legal certification claimed','device':device['device'],'base_incremental':device['base_incremental'],'target_incremental':device['target_incremental'],'source_release':source['html_url'],'source_assets_verified':401,'assets':[{k:row[k] for k in ['asset','sha256','bytes']} for row in expected.values()],'complete':True}
   path=pathlib.Path(report_name);path.write_text(json.dumps(report,indent=2)+'\n');subprocess.run(['gh','release','upload',device['tag'],str(path),'--repo',REPO,'--clobber'],check=True)
   subprocess.run(['gh','release','edit',device['tag'],'--repo',REPO,'--draft=false'],check=True)
 for device in manifest['devices']:
  public=release(device['tag']);assert not public['draft'] and public['prerelease']
 # All release assets are public and verified before any client sees an offer.
 feeds=[entry for device in manifest['devices'] for entry in device['feeds']]
 assert len(feeds)==6 and len({x['path'] for x in feeds})==6
 for attempt in range(3):
  head=gh('api','repos/'+REPO+'/git/ref/heads/main',json_output=True)['object']['sha'];tree=gh('api','repos/'+REPO+'/git/commits/'+head,json_output=True)['tree']['sha'];changes=[]
  for entry in feeds:
   current=subprocess.run(['gh','api','repos/'+REPO+'/contents/'+entry['path']+'?ref='+head],capture_output=True,text=True)
   if current.returncode==0:
    old=json.loads(base64.b64decode(json.loads(current.stdout)['content']));new=entry['body']
    assert all(old[k]==new[k] for k in ['schema_version','device','variant','base_incremental'])
    if old==new:continue
    if old.get('response'):
     assert new['response'],'Refuse to erase a newer target feed'
     assert max(int(x['incremental']) for x in old['response'])<=int(new['response'][0]['incremental']),'Refuse to overwrite a newer release'
   else:assert '404' in current.stderr,current.stderr
   changes.append({'path':entry['path'],'mode':'100644','type':'blob','content':json.dumps(entry['body'],indent=2)+'\n'})
  if not changes:break
  new_tree=request('POST','repos/'+REPO+'/git/trees',{'base_tree':tree,'tree':changes})['sha']
  commit=request('POST','repos/'+REPO+'/git/commits',{'message':'Publish verified exact-base notice-corrected OTA offers for all three devices [skip actions]','tree':new_tree,'parents':[head]})['sha']
  patch=pathlib.Path('api-request.json');patch.write_text(json.dumps({'sha':commit,'force':False}));result=subprocess.run(['gh','api','--method','PATCH','repos/'+REPO+'/git/refs/heads/main','--input',str(patch)],capture_output=True,text=True)
  if result.returncode==0:break
  if attempt==2:raise RuntimeError('Could not fast-forward the atomic feed update: '+result.stderr)
 else:raise AssertionError('Feed commit failed')
 # Verify public endpoint bodies, rather than only the commit response.
 for entry in feeds:
  url='https://raw.githubusercontent.com/'+REPO+'/main/'+entry['path']
  for attempt in range(20):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Quilt-release-verifier','Cache-Control':'no-cache'}),timeout=30) as response:body=json.load(response)
    if body==entry['body']:break
   except OSError:pass
   if attempt==19:raise AssertionError('Public feed differs: '+entry['path'])
   time.sleep(15)
 print('Published and verified all three OTA releases and all six exact-base feeds.')
