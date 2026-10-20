"""CPU-only provenance/split audit of pinned official ChartQA metadata."""
if not __debug__:
    raise SystemExit('Mandatory checks require ordinary Python.')
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()


def save(path,value):
    with path.open('xb') as f:
        f.write(encoded(value))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    assert path.is_file() and not path.is_symlink()
    return dict(bytes=path.stat().st_size,sha256=sha(path.read_bytes()))


def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def tree(value):
    assert isinstance(value,dict) and value.get('truncated') is False
    result = {}
    for row in value['tree']:
        name = row['path']
        assert PurePosixPath(name).name == name and name not in result
        assert row['type'] in ('blob','tree') and len(row['sha']) == 40
        result[name] = row
    return result


def summarize(documents,images,tables):
    """Keep QA strings/labels private; publish counts and identity-only findings."""
    catalog, summary = [], {}
    for split in ('train','val','test'):
        kinds, used, missing, no_table = {}, set(), set(), set()
        for kind in ('human','augmented'):
            rows = documents[(split,kind)]
            assert isinstance(rows,list) and rows
            kinds[kind] = len(rows)
            for i,row in enumerate(rows):
                assert {'imgname','query','label'} <= set(row)
                name, query, label = row['imgname'],row['query'],row['label']
                assert isinstance(name,str) and PurePosixPath(name).name == name and name.endswith('.png')
                assert isinstance(query,str) and query.strip()
                assert isinstance(label,(str,int,float)) and str(label).strip()
                used.add(name)
                if name not in images[split]:
                    missing.add(name)
                    continue
                if name[:-4]+'.csv' not in tables[split]:
                    no_table.add(name)
                qhash = sha(query.encode())
                uid = sha(f'{split}/{kind}/{i}/{images[split][name]}/{qhash}'.encode())
                catalog.append(dict(uid=uid,split=split,kind=kind,row_index=i,imgname=name,
                    image_git_blob_sha1=images[split][name],query_sha256=qhash,
                    label_sha256=sha(json.dumps(label,sort_keys=True).encode())))
        summary[split] = dict(QA_by_kind=kinds,QA_total=sum(kinds.values()),
            referenced_image_names=len(used),PNG_tree_images=len(images[split]),
            unique_referenced_image_blobs=len({images[split][n] for n in used if n in images[split]}),
            missing_image_names=sorted(missing),referenced_images_without_table=len(no_table))
    overlaps = {}
    for a,b in (('train','val'),('train','test'),('val','test')):
        aa = {x['image_git_blob_sha1'] for x in catalog if x['split'] == a}
        bb = {x['image_git_blob_sha1'] for x in catalog if x['split'] == b}
        overlaps[a+'__'+b] = sorted(aa & bb)
    pairs = defaultdict(list)
    for r in catalog:
        pairs[(r['image_git_blob_sha1'],r['query_sha256'])].append(r)
    repeated = [v for v in pairs.values() if len(v)>1]
    conflicts = [v for v in repeated if len({r['label_sha256'] for r in v})>1]
    by_image = Counter(r['image_git_blob_sha1'] for r in catalog)
    missing = sum(len(s['missing_image_names']) for s in summary.values())
    result = dict(splits=summary,QA_records=len(catalog),
        exact_image_blob_cross_split_overlap_counts={k:len(v) for k,v in overlaps.items()},
        exact_image_blob_cross_split_overlaps=overlaps,
        repeated_image_query_identity_groups=len(repeated),
        conflicting_exact_query_label_groups=len(conflicts),
        charts_with_multiple_QA=sum(n>1 for n in by_image.values()),
        max_QA_per_image_blob=max(by_image.values()),
        data_review_required=bool(missing or conflicts or any(overlaps.values())),
        image_bytes_downloaded=0,model_calls=0,GPU_starts=0,
        qualification='METADATA_ONLY;no perceptual/template/source independence or annotation correctness established')
    return catalog,result


def select(catalog,seed,counts):
    """Balanced question origin; one QA per byte-identity chart; no outcome use."""
    owners = defaultdict(set)
    for r in catalog:
        owners[r['image_git_blob_sha1']].add(r['split'])
    selections, used = {}, set()
    for split in ('train','val','test'):
        chosen = []
        for kind in ('human','augmented'):
            rows = [r for r in catalog if r['split']==split and r['kind']==kind
                    and len(owners[r['image_git_blob_sha1']])==1]
            rows.sort(key=lambda r:(sha(f'ReplayRAG-G0:{seed}:{r["uid"]}'.encode()),r['uid']))
            accepted = []
            for row in rows:
                if row['image_git_blob_sha1'] not in used:
                    accepted.append(row)
                    used.add(row['image_git_blob_sha1'])
                    if len(accepted)==counts[split]//2:
                        break
            assert len(accepted)==counts[split]//2, (split,kind,'Insufficient distinct charts')
            chosen.extend(accepted)
        selections[split] = chosen
    return dict(seed=seed,counts=counts,records=selections,
                status='IDENTITY_ONLY;not a frozen model/comparison contract;test outcomes not generated',
                grouping='Exact Git image-blob identity only;template/source-family grouping unresolved',
                models_used_for_selection=0)


def run(work,authenticated=False):
    c = json.loads((HERE/'AUDIT_CONTRACT.json').read_text())
    work.mkdir()
    (work/'raw').mkdir()
    sources = {n:identity(HERE/n) for n in ('audit_chartqa.py','test_audit.py','AUDIT_CONTRACT.json')}
    save(work/'REGISTERED.json',dict(before_download=True,source_files=sources,
        contract_sha256=identity(HERE/'AUDIT_CONTRACT.json')['sha256'],
        python=platform.python_version(),github_api_authenticated=authenticated,GPU_starts=0,model_calls=0))
    total, observations = 0, {}
    token = None
    if authenticated:
        result = subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',
                                capture_output=True,text=True,check=True)
        token = dict(x.split('=',1) for x in result.stdout.splitlines() if '=' in x)['password']
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl):
            return None
    opener=urllib.request.build_opener(NoRedirect)
    def fetch(name,url):
        nonlocal total
        with (work/'REQUESTS.jsonl').open('a') as f:
            f.write(json.dumps(dict(label=name,url=url,before_request=True))+'\n')
        host=urllib.parse.urlparse(url).hostname
        assert host in ('api.github.com','raw.githubusercontent.com') and url.startswith('https://')
        headers={'User-Agent':'ReplayRAG-dataset-audit','Accept':'application/vnd.github+json'}
        if token and host=='api.github.com':
            headers['Authorization']='Bearer '+token
        req = urllib.request.Request(url,headers=headers)
        with opener.open(req,timeout=60) as response:
            data = response.read(c['max_single_download_bytes']+1)
        assert len(data)<=c['max_single_download_bytes']
        total += len(data)
        assert total<=c['max_total_download_bytes']
        with (work/'raw'/name).open('xb') as f:
            f.write(data)
        observations[name] = dict(url=url,bytes=len(data),sha256=sha(data))
        return data
    def get_tree(label,ref):
        value = json.loads(fetch(label+'.json',f'https://api.github.com/repos/vis-nlp/ChartQA/git/trees/{ref}'))
        return tree(value)
    try:
        root = get_tree('root_tree',c['upstream_commit'])
        base = get_tree('dataset_tree',root['ChartQA Dataset']['sha'])
        documents,images,tables = {},{},{}
        for split in ('train','val','test'):
            assert base[split]['sha'] == c['split_trees'][split]
            nodes = get_tree(split+'_tree',base[split]['sha'])
            for role in ('png','tables'):
                entries = get_tree(split+'_'+role+'_tree',nodes[role]['sha'])
                assert all(x['type']=='blob' and x['mode']=='100644' for x in entries.values())
                if role=='png':
                    images[split] = {n:x['sha'] for n,x in entries.items() if n.endswith('.png')}
                else:
                    tables[split] = {n:x['sha'] for n,x in entries.items() if n.endswith('.csv')}
            for kind in ('human','augmented'):
                name=f'{split}_{kind}.json'
                expected=c['QA_files'][name]
                assert nodes[name]['sha']==expected['git_blob_sha1'] and nodes[name]['size']==expected['bytes']
                path=urllib.parse.quote('ChartQA Dataset/'+split+'/'+name,safe='/')
                data=fetch(name,f'https://raw.githubusercontent.com/vis-nlp/ChartQA/{c["upstream_commit"]}/{path}')
                assert len(data)==expected['bytes'] and git_blob(data)==expected['git_blob_sha1']
                documents[(split,kind)] = json.loads(data)
        catalog,result = summarize(documents,images,tables)
        with (work/'PRIVATE_CATALOG.jsonl').open('x') as f:
            for r in catalog:
                f.write(json.dumps(r,sort_keys=True)+'\n')
        selection = select(catalog,c['selection_seed'],c['identity_probe_counts'])
        save(work/'PILOT_SELECTION.json',selection)
        result.update(completed=True,upstream_commit=c['upstream_commit'],source_files=sources,
            contract_sha256=identity(HERE/'AUDIT_CONTRACT.json')['sha256'],
            download_bytes=total,requests=len(observations),
            pilot_selection_sha256=identity(work/'PILOT_SELECTION.json')['sha256'])
        save(work/'AUDIT_RESULTS.json',result)
        save(work/'DOWNLOADS.json',observations)
        assert sources == {n:identity(HERE/n) for n in sources}
        census={str(p.relative_to(work)):identity(p) for p in sorted(work.rglob('*')) if p.is_file()}
        save(work/'CENSUS.json',dict(files=census))
        print(json.dumps({k:result[k] for k in ('QA_records','requests','download_bytes','exact_image_blob_cross_split_overlap_counts','conflicting_exact_query_label_groups','data_review_required','GPU_starts')},sort_keys=True))
    except BaseException as error:
        save(work/'FAILURE.json',dict(error=repr(error),model_calls=0,GPU_starts=0))
        raise


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--github-auth',action='store_true',help='Use existing Git credential helper in memory for GitHub API only.')
    args=p.parse_args()
    run(args.work.resolve(),args.github_auth)
