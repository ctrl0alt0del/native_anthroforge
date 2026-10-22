"""Read saved shortcut and driver data without registering addon runtime handlers."""
import bpy
import hashlib
import json
import sys
from pathlib import Path


def register_properties():
    sys.path.insert(0, 'C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons')
    from anthroforge.properties.scp_properties import (
        AF_SCP_BoundObject_Property, AF_SCP_Property, AF_SCP_System_Property)
    from anthroforge.properties.shortcut_properties import (
        AF_DataShortcutOverride_Property, AF_DataShortcut_Property, AF_DataShortcut_System_Property)
    for cls in (AF_SCP_BoundObject_Property, AF_SCP_Property, AF_SCP_System_Property,
                AF_DataShortcutOverride_Property, AF_DataShortcut_Property, AF_DataShortcut_System_Property):
        bpy.utils.register_class(cls)
    bpy.types.Object.af_scp_system = bpy.props.PointerProperty(type=AF_SCP_System_Property)
    bpy.types.Object.af_shortcut_system = bpy.props.PointerProperty(type=AF_DataShortcut_System_Property)


def root_rows():
    return {o.name: dict(shortcuts=[shortcut_row(s) for s in o.af_shortcut_system.shortcuts],
                         scps=[plain(s) for s in o.af_scp_system.scps])
            for o in bpy.data.objects if o.af_shortcut_system.shortcuts}


def shortcut_row(shortcut):
    from anthroforge.core.shortcuts.resolver import resolve_shortcut
    row = attrs(shortcut, ('id', 'name', 'owner_type', 'owner_id', 'data_path',
                           'vector_mode', 'owner_backsolve'))
    resolved = resolve_shortcut(shortcut.id_data, bpy.context, shortcut.data_path)
    row['resolved'] = attrs(resolved, ('prop_name', 'index', 'value_type', 'array_length', 'subtype', 'error'))
    row['resolved'].update(resolved_details(resolved))
    row['overrides'] = [attrs(o, ('target_scp_id', 'parent_anchor_mode', 'child_anchor_mode',
                                   'follow_rotation_mode', 'rotation_strategy')) for o in shortcut.overrides]
    return row


def resolved_details(target):
    if not target.owner:
        return {}
    owner = target.owner
    path = '' if isinstance(owner, bpy.types.ID) else owner.path_from_id()
    leaf = target.prop_name
    path += ('.' if path and not leaf.startswith('[') else '') + leaf
    if target.index >= 0:
        path += f'[{target.index}]'
    return dict(id=plain(owner.id_data), path=path,
                captured=resolve(owner.id_data, path))


def plain(value):
    if isinstance(value, bpy.types.ID):
        return {'id': value.name_full, 'type': value.id_type}
    if isinstance(value, (str, float, int, bool)) or value is None:
        return value
    if hasattr(value, 'items'):
        return {str(k): plain(v) for k, v in value.items()}
    try:
        return [plain(v) for v in value]
    except TypeError:
        return repr(value)


def attrs(value, names):
    return {name: plain(getattr(value, name)) for name in names if hasattr(value, name)}


def resolve(owner, path):
    try:
        return {'value': plain(owner.path_resolve(path))}
    except Exception as exc:
        return {'error': str(exc)}


def target(value):
    row = attrs(value, ('id', 'id_type', 'data_path', 'bone_target', 'transform_type',
                        'transform_space', 'rotation_mode', 'use_fallback_value', 'fallback_value'))
    if value.id and value.data_path:
        row['resolved'] = resolve(value.id, value.data_path)
    return row


def driver(owner, curve):
    value = curve.driver
    row = attrs(curve, ('data_path', 'array_index', 'mute', 'is_valid', 'extrapolation'))
    row.update(owner=plain(owner), driver=attrs(value, ('type', 'expression', 'use_self',
                                                      'is_valid', 'is_simple_expression')))
    row['variables'] = [dict(name=v.name, type=v.type, targets=[target(t) for t in v.targets])
                        for v in value.variables]
    row['resolved'] = resolve(owner, curve.data_path)
    row['modifiers'] = [dict(type=m.type, **attrs(m, ('mode', 'coefficients', 'mute')))
                        for m in curve.modifiers]
    row['keys'] = [attrs(p, ('co', 'handle_left', 'handle_right', 'interpolation',
                            'handle_left_type', 'handle_right_type')) for p in curve.keyframe_points]
    row['mapping_probe'] = [[t, curve.evaluate(t)] for t in (-2, -0.5, 0, 0.5, 1, 2, 10)]
    return row


def datablocks():
    for prop in bpy.data.bl_rna.properties:
        if prop.type != 'COLLECTION':
            continue
        for item in getattr(bpy.data, prop.identifier):
            yield item
            if getattr(item, 'node_tree', None):
                yield item.node_tree


def all_drivers():
    rows, seen = [], set()
    for item in datablocks():
        if item.as_pointer() in seen:
            continue
        seen.add(item.as_pointer())
        animation = getattr(item, 'animation_data', None)
        rows.extend(driver(item, f) for f in animation.drivers if True) if animation else None
    return rows


def modifier(value):
    row = dict(name=value.name, type=value.type,
               properties=plain(value) if value.type == 'NODES' else {})
    if value.type == 'NODES' and value.node_group:
        row['group'] = value.node_group.name
        row['inputs'] = [attrs(i, ('name', 'identifier', 'socket_type', 'default_value',
                                   'min_value', 'max_value', 'subtype', 'description'))
                         for i in value.node_group.interface.items_tree
                         if i.item_type == 'SOCKET' and i.in_out == 'INPUT']
    return row


def object_row(obj):
    custom = {k: plain(v) for k, v in obj.items() if not k.startswith('af_')}
    ui = {}
    for key in custom:
        try:
            ui[key] = plain(obj.id_properties_ui(key).as_dict())
        except Exception:
            pass
    return dict(name=obj.name, type=obj.type, data=plain(obj.data), custom=custom, ui=ui,
                modifiers=[modifier(m) for m in obj.modifiers], curves=curve_data(obj))


def curve_data(obj):
    if obj.type != 'CURVE':
        return []
    return [dict(type=s.type, closed=s.use_cyclic_u, resolution=s.resolution_u,
                 bezier=[attrs(p, ('co', 'handle_left', 'handle_right',
                                  'handle_left_type', 'handle_right_type')) for p in s.bezier_points],
                 points=[list(p.co) for p in s.points]) for s in obj.data.splines]


def main():
    source, output = map(Path, sys.argv[sys.argv.index('--') + 1:])
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    register_properties()
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    roots = root_rows()
    report = dict(source=str(source), sha256=before, blender=bpy.app.version_string,
                  roots=roots, drivers=all_drivers(), objects=[object_row(o) for o in bpy.data.objects])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('CAPTURED', source.name, 'roots', len(roots), 'drivers', len(report['drivers']))


main()
