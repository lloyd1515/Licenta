import re, sys
def load(path):
    out, cur, name = {}, None, None
    for line in open(path):
        m = re.match(r'^[0-9a-f]+ <([^>]+)>:$', line.rstrip())
        if m:
            name = m.group(1); cur = out.setdefault(name, []); continue
        if line.startswith('Disassembly of section'):
            name = None; cur = None; continue
        if cur is not None and line.strip():
            cur.append(line.rstrip('\n'))
    return out
def get(d, fn):
    lit = next((k for k in d if k.startswith(fn + '-0x')), None)
    return (d.get(lit, []) if lit else []), d.get(fn, [])
if __name__ == '__main__':
    d = load(sys.argv[1])
    for fn in sys.argv[2:]:
        lit, body = get(d, fn)
        print('########', fn); print('\n'.join(lit)); print('  --'); print('\n'.join(body))
