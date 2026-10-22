"""Create reviewable evidence from read-only Blender captures."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/research/shortcuts_030'
OUT.mkdir(parents=True, exist_ok=True)


def key(owner, path, index=-1):
    match = re.search(r'\[(\d+)\]$', path)
    return (owner['type'], owner['id'], path[:match.start()] if match else path,
            int(match[1]) if match else index)


def matches(left, right):
    return left[:3] == right[:3] and (left[3] < 0 or right[3] < 0 or left[3] == right[3])


def inputs(driver):
    result = []
    for var in driver['variables']:
        for item in var['targets']:
            if var['type'] == 'SINGLE_PROP':
                result.append(key(item['id'], item['data_path']))
            elif var['type'] == 'TRANSFORMS' and item['transform_type'].startswith('SCALE_'):
                axis = item['transform_type'][6:]
                result.append(key(item['id'], 'scale', 'XYZ'.index(axis) if axis in 'XYZ' else -1))
    return result


def affected(start, drivers):
    seen, reached = {start}, set()
    changed = True
    while changed:
        changed = False
        for f in drivers:
            if f['id'] in reached or not any(matches(a, b) for a in seen for b in inputs(f)):
                continue
            reached.add(f['id'])
            seen.add(key(f['owner'], f['data_path'], f['array_index']))
            changed = True
    return sorted(reached)


def target_kind(item):
    path = item['resolved']['path']
    if path.startswith('modifiers['):
        return 'Geometry Nodes input'
    return 'Custom property' if path.startswith('[') else 'Transform'


def socket(item, objects):
    path = item['resolved']['path']
    match = re.fullmatch(r'modifiers\["(.+)"\]\["(.+)"\]', path)
    if not match:
        return None
    obj = objects[item['resolved']['id']['id']]
    mod = next(m for m in obj['modifiers'] if m['name'] == match[1])
    found = next(i for i in mod['inputs'] if i['identifier'] == match[2])
    return dict(group=mod['group'], **found)


def shortcut(s, names, drivers, objects):
    row = dict(s, owner_name=names[s['owner_id']], target_kind=target_kind(s))
    target = key(s['resolved']['id'], s['resolved']['path'])
    row['incoming_drivers'] = [f['id'] for f in drivers if matches(target,
                               key(f['owner'], f['data_path'], f['array_index']))]
    row['downstream_drivers'] = affected(target, drivers)
    row['socket'] = socket(s, objects)
    obj = objects[s['resolved']['id']['id']]
    leaf = s['resolved']['prop_name'].strip('[]"')
    row['custom_ui'] = obj['ui'].get(leaf)
    return row


def dataset(stem, prefix):
    d = json.loads((ROOT / f'build/shortcuts-030/{stem}.json').read_text())
    drivers = [dict(f, id=f'{prefix}-D{i:02d}') for i, f in enumerate(d['drivers'], 1)]
    objects = {o['name']: o for o in d['objects']}
    root = d['roots']['AF_ROOT']
    names = {s['id']: s['name'] for s in root['scps']}
    shortcuts = [shortcut(s, names, drivers, objects) for s in root['shortcuts']]
    controls = [o for o in d['objects'] if o['curves'] and o['custom']]
    scps = [dict(id=s['id'], name=s['name'], bound_objects=s['bound_objects']) for s in root['scps']]
    return dict(source=d['source'], sha256=d['sha256'], blender=d['blender'],
                shortcuts=shortcuts, drivers=drivers, scps=scps, curve_controls=controls)


def code(value):
    return '`' + str(value).replace('|', '\\|') + '`'


def location(owner, path, index=-1):
    suffix = f'[{index}]' if index >= 0 else ''
    return f'{owner["id"]}.{path}{suffix}'


def shortcut_line(s):
    resolved = s['resolved']
    target = location(resolved['id'], resolved['path'])
    links = ', '.join(s['downstream_drivers']) or 'None'
    incoming = ', '.join(s['incoming_drivers']) or 'None'
    return f'| {s["id"]} | {s["owner_name"]}: {s["name"]} | {code(s["data_path"])} | {code(target)} | {incoming} | {links} |'


def variable(v):
    t = v['targets'][0]
    source = location(t['id'], t['data_path']) if v['type'] == 'SINGLE_PROP' else (
        f'{t["id"]["id"]} {t["transform_space"]} {t["transform_type"]}')
    return f'{v["name"]} ← {source}'


def driver_line(f):
    output = location(f['owner'], f['data_path'], f['array_index'])
    expression = f['driver']['expression'] if f['driver']['type'] == 'SCRIPTED' else 'AVERAGE(inputs)'
    variables = '; '.join(variable(v) for v in f['variables'])
    return f'| {f["id"]} | {code(output)} | {code(expression)} | {code(variables)} |'


def section(name, d):
    rows = [f'## {name}', '', f'Source: `{d["source"]}`', '', f'SHA256: `{d["sha256"]}`', '']
    rows += ['| ID | Owner / shortcut | Saved path | Resolved target | Incoming driver | Downstream drivers |',
             '| --- | --- | --- | --- | --- | --- |']
    rows += [shortcut_line(s) for s in d['shortcuts']]
    rows += ['', '### Exact drivers', '', '| ID | Driven channel | Expression / operation | Variables |',
             '| --- | --- | --- | --- |']
    rows += [driver_line(f) for f in d['drivers']]
    return rows + ['']


def main():
    data = dict(skeleton=dataset('skeleton_comb_base', 'SK'), skull=dataset('skull_muscles', 'CR'))
    (OUT / 'inventory.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    rows = ['# Saved shortcut and driver inventory', '',
            'Read-only Blender 5.0.1 inspection. See [analysis](../../shortcuts_030_research.md).', '',
            'Downstream lists follow declared driver inputs transitively, not geometry/modifier or attachment dependencies.',
            'Transform-variable links include relevant own scale components; world-space values also depend on parents.',
            'A scalar FCurve index `[0]` is Blender channel metadata, not an array requirement for that property.',
            'JSON additionally retains values, socket names, limits, vector modes, attachment policies and full FCurve mapping.', '']
    for name, d in data.items():
        rows += section(name.title(), d)
        print(name, 'shortcuts', len(d['shortcuts']), 'drivers', len(d['drivers']),
              'kinds', Counter(s['target_kind'] for s in d['shortcuts']))
    (OUT / 'inventory.md').write_text('\n'.join(rows), encoding='utf-8')


main()
