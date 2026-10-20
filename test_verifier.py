"""Synthetic Git tree identity and label-free export checks."""
if not __debug__:
    raise SystemExit('Mandatory checks require ordinary Python.')
import copy
import hashlib
import verify_audit as v


def main():
    entries = [dict(path='a.c', mode='100644', type='blob', sha='a' * 40),
               dict(path='a', mode='040000', type='tree', sha='b' * 40)]
    payload = b'100644 a.c\0' + bytes.fromhex('a' * 40) + b'40000 a\0' + bytes.fromhex('b' * 40)
    digest = hashlib.sha1(b'tree ' + str(len(payload)).encode() + b'\0' + payload).hexdigest()
    value = dict(tree=entries, truncated=False, sha=digest)
    assert set(v.check_tree(value)) == {'a', 'a.c'}
    changed = copy.deepcopy(value)
    changed['tree'][0]['sha'] = 'c' * 40
    try:
        v.check_tree(changed)
    except AssertionError:
        pass
    else:
        raise AssertionError('Tampered Git tree admitted')
    print('TEST_PASS: Git tree modes, directory ordering and tamper rejection')


if __name__ == '__main__':
    main()
