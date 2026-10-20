"""Offline evidence closure; never runs a model or modifies the original audit."""
if not __debug__:
    raise SystemExit('Mandatory checks require ordinary Python.')
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import audit_chartqa as a


def load(path):
    return json.loads(path.read_bytes())


def check_tree(value):
    entries = a.tree(value)
    # Reconstruct the Git tree object, including Git's directory sorting rule.
    rows = sorted(entries.values(), key=lambda r: (r['path'] + ('/' if r['type'] == 'tree' else '')).encode())
    payload = b''.join((r['mode'].lstrip('0') + ' ' + r['path']).encode() + b'\0'
                       + bytes.fromhex(r['sha']) for r in rows)
    actual = hashlib.sha1(b'tree ' + str(len(payload)).encode() + b'\0' + payload).hexdigest()
    assert actual == value['sha'], 'Git tree object identity mismatch'
    return entries


def verify(work, commit_metadata):
    c = load(a.HERE / 'AUDIT_CONTRACT.json')
    census = load(work / 'CENSUS.json')['files']
    actual = {str(p.relative_to(work)): a.identity(p)
              for p in sorted(work.rglob('*')) if p.is_file() and p.name != 'CENSUS.json'}
    assert actual == census, 'Raw evidence census mismatch'
    reg, result = load(work / 'REGISTERED.json'), load(work / 'AUDIT_RESULTS.json')
    assert reg['before_download'] and reg['source_files'] == result['source_files']
    for name, expected in reg['source_files'].items():
        assert a.identity(a.HERE / name) == expected, 'Executed source changed'
    assert reg['contract_sha256'] == a.identity(a.HERE / 'AUDIT_CONTRACT.json')['sha256']
    downloads = load(work / 'DOWNLOADS.json')
    requests = [json.loads(row) for row in (work / 'REQUESTS.jsonl').read_text().splitlines()]
    assert len(downloads) == len(requests) == result['requests'] == 17
    assert set(downloads) == {p.name for p in (work / 'raw').iterdir()}
    for request in requests:
        name = request['label']
        assert request['before_request'] and request['url'] == downloads[name]['url']
        assert a.identity(work / 'raw' / name) == {k: downloads[name][k] for k in ('bytes', 'sha256')}
    assert sum(r['bytes'] for r in downloads.values()) == result['download_bytes']
    commit = load(commit_metadata)
    assert commit['sha'] == c['upstream_commit']
    root_value = load(work / 'raw/root_tree.json')
    # GitHub echoes the commit ref in this response's sha field. Resolve the
    # actual tree object with a separately retained commit metadata lookup.
    assert root_value['sha'] == c['upstream_commit']
    root = check_tree(dict(root_value, sha=commit['tree']['sha']))
    base_value = load(work / 'raw/dataset_tree.json')
    assert root['ChartQA Dataset']['sha'] == base_value['sha']
    base = check_tree(base_value)
    docs, images, tables = {}, {}, {}
    independent_pairs = defaultdict(set)
    image_splits = defaultdict(set)
    for split in ('train', 'val', 'test'):
        value = load(work / 'raw' / (split + '_tree.json'))
        assert base[split]['sha'] == c['split_trees'][split] == value['sha']
        nodes = check_tree(value)
        for role, target, suffix in (('png', images, '.png'), ('tables', tables, '.csv')):
            value = load(work / 'raw' / (split + '_' + role + '_tree.json'))
            assert value['sha'] == nodes[role]['sha']
            target[split] = {n: r['sha'] for n, r in check_tree(value).items() if n.endswith(suffix)}
        for kind in ('human', 'augmented'):
            name = split + '_' + kind + '.json'
            data = (work / 'raw' / name).read_bytes()
            expected = c['QA_files'][name]
            assert len(data) == expected['bytes']
            assert a.git_blob(data) == expected['git_blob_sha1'] == nodes[name]['sha']
            docs[(split, kind)] = json.loads(data)
            for row in docs[(split, kind)]:
                blob = images[split][row['imgname']]
                image_splits[blob].add(split)
                independent_pairs[(blob, row['query'])].add(json.dumps(row['label'], sort_keys=True))
    catalog, recomputed = a.summarize(docs, images, tables)
    for k, v in recomputed.items():
        assert result[k] == v, 'Aggregate mismatch: ' + k
    assert catalog == [json.loads(r) for r in (work / 'PRIVATE_CATALOG.jsonl').read_text().splitlines()]
    selection = load(work / 'PILOT_SELECTION.json')
    assert selection == a.select(catalog, c['selection_seed'], c['identity_probe_counts'])
    assert a.identity(work / 'PILOT_SELECTION.json')['sha256'] == result['pilot_selection_sha256']
    conflicts = {k for k, labels in independent_pairs.items() if len(labels) > 1}
    assert len(conflicts) == result['conflicting_exact_query_label_groups']
    row_by_id = {r['uid']: docs[(r['split'], r['kind'])][r['row_index']] for r in catalog}
    picked, collision_counts, seen = [], {}, set()
    for split, rows in selection['records'].items():
        collisions = 0
        for row in rows:
            blob = row['image_git_blob_sha1']
            assert blob not in seen and image_splits[blob] == {split}
            seen.add(blob)
            collisions += (blob, row_by_id[row['uid']]['query']) in conflicts
            # Label hashes are evaluator-only and must never reach solver artifacts.
            picked.append({k: v for k, v in row.items() if k != 'label_sha256'})
        collision_counts[split] = collisions
    assert not any(collision_counts.values()), 'Candidate pool needs label review'
    closure = dict(status='PASS_METADATA_CLOSURE_ONLY', raw_census_sha256=a.identity(work / 'CENSUS.json')['sha256'],
        raw_files_verified=len(census), raw_downloads_verified=len(downloads),
        supplemental_commit_metadata=a.identity(commit_metadata),
        upstream_commit=commit['sha'], root_tree_sha1=commit['tree']['sha'],
        independent_label_variant_groups=len(conflicts), candidate_pool_sizes=selection['counts'],
        candidate_pool_label_variant_collisions=collision_counts, candidate_charts_unique=len(seen),
        global_data_review_required=result['data_review_required'],
        annotation_correctness='UNREVIEWED', template_source_independence='UNKNOWN',
        model_calls=0, GPU_starts=0, verifier_source=a.identity(Path(__file__)))
    return closure, dict(status=selection['status'], seed=selection['seed'],
                         grouping=selection['grouping'], counts=selection['counts'], records=picked)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit', type=Path, required=True)
    p.add_argument('--commit-metadata', type=Path, required=True, help='Retained upstream Git commit API JSON.')
    p.add_argument('--output', type=Path, required=True, help='Fresh export directory.')
    args = p.parse_args()
    closure, public_selection = verify(args.audit.resolve(), args.commit_metadata.resolve())
    args.output.mkdir(parents=True)
    a.save(args.output / 'CLOSURE.json', closure)
    a.save(args.output / 'CANDIDATE_IDENTITIES.json', public_selection)
    for name in ('AUDIT_RESULTS.json', 'CENSUS.json', 'DOWNLOADS.json', 'REGISTERED.json'):
        a.save(args.output / name, load(args.audit / name))
    print(json.dumps(closure, sort_keys=True))
