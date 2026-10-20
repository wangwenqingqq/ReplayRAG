"""Synthetic identity and split-leakage regression checks; no benchmark downloads."""
if not __debug__:
    raise SystemExit('Mandatory checks require ordinary Python.')
import copy
import tempfile
from pathlib import Path
import audit_chartqa as a


def main():
    docs,images,tables={},{},{}
    for i,s in enumerate(('train','val','test')):
        images[s]={f'{n}.png':str(i*100+n).zfill(40) for n in range(20)}
        tables[s]={f'{n}.csv':'c'*40 for n in range(20)}
        for kind in ('human','augmented'):
            docs[(s,kind)]=[dict(imgname=f'{n}.png',query=f'question{n}',label=str(n)) for n in range(20)]
    catalog,result=a.summarize(docs,images,tables)
    assert result['QA_records']==120 and not result['data_review_required']
    assert result['charts_with_multiple_QA']==60 and result['repeated_image_query_identity_groups']==60
    assert a.select(catalog,7,dict(train=4,val=4,test=4))==a.select(catalog,7,dict(train=4,val=4,test=4))
    changed=copy.deepcopy(images);changed['val']['0.png']=changed['train']['0.png']
    _,r=a.summarize(docs,changed,tables)
    assert r['data_review_required'] and r['exact_image_blob_cross_split_overlap_counts']['train__val']==1
    changed=copy.deepcopy(docs);changed[('train','human')][0]['label']='wrong'
    _,r=a.summarize(changed,images,tables)
    assert r['conflicting_exact_query_label_groups']==1 and r['data_review_required']
    changed=copy.deepcopy(images);changed['train'].pop('0.png')
    _,r=a.summarize(docs,changed,tables)
    assert r['splits']['train']['missing_image_names']==['0.png'] and r['data_review_required']
    try:
        a.tree(dict(tree=[],truncated=True))
    except AssertionError:
        pass
    else:
        raise AssertionError('Truncated upstream tree admitted')
    assert a.git_blob(b'hello\n')=='ce013625030ba8dba906f756967f9e9ca394464a'
    with tempfile.TemporaryDirectory() as tmp:
        f=Path(tmp)/'x.json';a.save(f,dict(test=True))
        try:a.save(f,dict(test=False))
        except FileExistsError:pass
        else:raise AssertionError('Existing evidence overwritten')
    print('TEST_PASS:synthetic overlap/conflict/missing-image detection,deterministic grouped selection,Git identity,no overwrite')


if __name__=='__main__':
    main()
