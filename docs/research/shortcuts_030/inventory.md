# Saved shortcut and driver inventory

Read-only Blender 5.0.1 inspection. See [analysis](../../shortcuts_030_research.md).

Downstream lists follow declared driver inputs transitively, not geometry/modifier or attachment dependencies.
Transform-variable links include relevant own scale components; world-space values also depend on parents.
A scalar FCurve index `[0]` is Blender channel metadata, not an array requirement for that property.
JSON additionally retains values, socket names, limits, vector modes, attachment policies and full FCurve mapping.

## Skeleton

Source: `E:\development\WIP_models\skeleton_comb_base.blend`

SHA256: `1049c9cef5d0e94735e20e1f3e313cdb845a67c6554ccf3a98e81da98b813ff2`

| ID | Owner / shortcut | Saved path | Resolved target | Incoming driver | Downstream drivers |
| --- | --- | --- | --- | --- | --- |
| SHORTCUT_1 | Ribs: Ribs Arc Radius | `bpy.data.objects["ribs_curve"]["Ribs Arc Radius"]` | `ribs_curve.["Ribs Arc Radius"]` | None | SK-D20, SK-D21, SK-D22, SK-D31, SK-D32 |
| SHORTCUT_3 | Sternum: Sternum Height | `bpy.data.objects["Sternum"]["Sternum Height"]` | `Sternum.["Sternum Height"]` | None | SK-D33 |
| SHORTCUT_4 | Ribs: Ribs Top Radius | `bpy.data.objects["ribs_profile_top"]["Ribs Top Radius"]` | `ribs_profile_top.["Ribs Top Radius"]` | None | SK-D26, SK-D27, SK-D28 |
| SHORTCUT_2 | Ribs: Ribs Arc Angle | `bpy.data.objects["ribs_geom"].modifiers["GeometryNodes"]["Socket_5"]` | `ribs_geom.modifiers["GeometryNodes"]["Socket_5"]` | None | SK-D31, SK-D32 |
| SHORTCUT_5 | Ribs: Ribs Bottom Radius | `bpy.data.objects["ribs_profile_bottom"]["Ribs Bottom Radius"]` | `ribs_profile_bottom.["Ribs Bottom Radius"]` | None | SK-D23, SK-D24, SK-D25 |
| SHORTCUT_6 | Ribs: Ribs Frontal Hook Position X | `af://object_rna/Ribs Frontal Hook/location[0]` | `Ribs Frontal Hook.location[0]` | None | None |
| SHORTCUT_7 | Ribs: Ribs Back Hook Position X | `af://object_rna/Ribs Back Hook/location[0]` | `Ribs Back Hook.location[0]` | None | None |
| SHORTCUT_9 | Ribs: Ribs Lower Angle | `bpy.data.objects["ribs_geom"].modifiers["GeometryNodes"]["Socket_10"]` | `ribs_geom.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_8 | Pubis: Pubis Arc Radius | `af://scp_bound_rna/SCP_8\|OBJ_3/["Pubis Arc Radius"]` | `pubis_arc.["Pubis Arc Radius"]` | None | SK-D05, SK-D06, SK-D07, SK-D08, SK-D10, SK-D11, SK-D12, SK-D13, SK-D14, SK-D16, SK-D17, SK-D18, SK-D19, SK-D29, SK-D30 |
| SHORTCUT_10 | Pubis: Pubis Arc Angle | `af://scp_bound_rna/SCP_8\|OBJ_2/["Pubis Arc Angle"]` | `pubis_geom.["Pubis Arc Angle"]` | None | SK-D19, SK-D29, SK-D30 |
| SHORTCUT_11 | Pubis: Pubis Arc Shrink | `af://scp_bound_rna/SCP_8\|OBJ_3/["Pubic Arc Shrink"]` | `pubis_arc.["Pubic Arc Shrink"]` | None | SK-D06, SK-D09, SK-D12, SK-D15, SK-D17 |
| SHORTCUT_12 | Ischium: Ischium Angle | `af://scp_bound_rna/SCP_9\|OBJ_2/rotation_euler[0]` | `ischium_geom.rotation_euler[0]` | None | None |
| SHORTCUT_13 | Ilium: Ilium Angle | `af://scp_bound_rna/SCP_12\|OBJ_2/rotation_euler[0]` | `ilium_geom.rotation_euler[0]` | None | None |
| SHORTCUT_14 | Ilium: Ilium Seg Angle | `af://scp_bound_rna/SCP_12\|OBJ_2/["Ilium Seg Angle"]` | `ilium_geom.["Ilium Seg Angle"]` | None | SK-D10 |
| SHORTCUT_15 | Humerus: Humerus Length | `af://scp_bound_rna/SCP_13\|OBJ_1/scale[0]` | `Humerus.scale[0]` | None | None |
| SHORTCUT_16 | Radius: Radius Length | `af://scp_bound_rna/SCP_14\|OBJ_1/scale[0]` | `Radius.scale[0]` | None | SK-D34 |
| SHORTCUT_17 | Carpals: Carpals Width | `af://scp_bound_rna/SCP_16\|OBJ_1/scale[2]` | `Carpals.scale[2]` | None | None |
| SHORTCUT_18 | Thumb: Thumb Base Thickness | `af://scp_bound_rna/SCP_17\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Thumb.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_19 | Thumb: Thumb Distal Length | `af://scp_bound_rna/SCP_17\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Thumb.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_20 | Thumb: Thumb Metacarpal Length | `af://scp_bound_rna/SCP_17\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Thumb.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_21 | Thumb: Thumb Metacarpal Thickness | `af://scp_bound_rna/SCP_17\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Thumb.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_22 | Thumb: Thumb Middle Length | `af://scp_bound_rna/SCP_17\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Thumb.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_23 | Thumb: Thumb Middle Thickness | `af://scp_bound_rna/SCP_17\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Thumb.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_24 | Thumb: Thumb Proximal Length | `af://scp_bound_rna/SCP_17\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Thumb.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_25 | Thumb: Thumb Tip Thickness | `af://scp_bound_rna/SCP_17\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Thumb.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_26 | Index: Index Base Thickness | `af://scp_bound_rna/SCP_18\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Index.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_27 | Index: Index Distal Length | `af://scp_bound_rna/SCP_18\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Index.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_28 | Index: Index Metacarpal Length | `af://scp_bound_rna/SCP_18\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Index.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_29 | Index: Index Metacarpal Thickness | `af://scp_bound_rna/SCP_18\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Index.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_30 | Index: Index Middle Length | `af://scp_bound_rna/SCP_18\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Index.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_31 | Index: Index Middle Thickness | `af://scp_bound_rna/SCP_18\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Index.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_32 | Index: Index Proximal Length | `af://scp_bound_rna/SCP_18\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Index.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_33 | Index: Index Tip Thickness | `af://scp_bound_rna/SCP_18\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Index.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_34 | Middle: Middle Base Thickness | `af://scp_bound_rna/SCP_19\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Middle.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_35 | Middle: Middle Distal Length | `af://scp_bound_rna/SCP_19\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Middle.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_36 | Middle: Middle Metacarpal Length | `af://scp_bound_rna/SCP_19\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Middle.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_37 | Middle: Middle Metacarpal Thickness | `af://scp_bound_rna/SCP_19\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Middle.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_38 | Middle: Middle Middle Length | `af://scp_bound_rna/SCP_19\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Middle.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_39 | Middle: Middle Middle Thickness | `af://scp_bound_rna/SCP_19\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Middle.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_40 | Middle: Middle Proximal Length | `af://scp_bound_rna/SCP_19\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Middle.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_41 | Middle: Middle Tip Thickness | `af://scp_bound_rna/SCP_19\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Middle.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_42 | Ring: Ring Base Thickness | `af://scp_bound_rna/SCP_20\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Ring.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_43 | Ring: Ring Distal Length | `af://scp_bound_rna/SCP_20\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Ring.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_44 | Ring: Ring Metacarpal Length | `af://scp_bound_rna/SCP_20\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Ring.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_45 | Ring: Ring Metacarpal Thickness | `af://scp_bound_rna/SCP_20\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Ring.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_46 | Ring: Ring Middle Length | `af://scp_bound_rna/SCP_20\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Ring.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_47 | Ring: Ring Middle Thickness | `af://scp_bound_rna/SCP_20\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Ring.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_48 | Ring: Ring Proximal Length | `af://scp_bound_rna/SCP_20\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Ring.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_49 | Ring: Ring Tip Thickness | `af://scp_bound_rna/SCP_20\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Ring.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_50 | Little: Little Base Thickness | `af://scp_bound_rna/SCP_21\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Little.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_51 | Little: Little Distal Length | `af://scp_bound_rna/SCP_21\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Little.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_52 | Little: Little Metacarpal Length | `af://scp_bound_rna/SCP_21\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Little.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_53 | Little: Little Metacarpal Thickness | `af://scp_bound_rna/SCP_21\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Little.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_54 | Little: Little Middle Length | `af://scp_bound_rna/SCP_21\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Little.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_55 | Little: Little Middle Thickness | `af://scp_bound_rna/SCP_21\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Little.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_56 | Little: Little Proximal Length | `af://scp_bound_rna/SCP_21\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Little.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_57 | Little: Little Tip Thickness | `af://scp_bound_rna/SCP_21\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Little.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_58 | Little_Toe: Little_Toe Base Thickness | `af://scp_bound_rna/SCP_32\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Little_Toe.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_59 | Little_Toe: Little_Toe Distal Length | `af://scp_bound_rna/SCP_32\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Little_Toe.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_60 | Little_Toe: Little_Toe Metacarpal Length | `af://scp_bound_rna/SCP_32\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Little_Toe.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_61 | Little_Toe: Little_Toe Metacarpal Thickness | `af://scp_bound_rna/SCP_32\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Little_Toe.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_62 | Little_Toe: Little_Toe Middle Length | `af://scp_bound_rna/SCP_32\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Little_Toe.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_63 | Little_Toe: Little_Toe Middle Thickness | `af://scp_bound_rna/SCP_32\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Little_Toe.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_64 | Little_Toe: Little_Toe Proximal Length | `af://scp_bound_rna/SCP_32\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Little_Toe.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_65 | Little_Toe: Little_Toe Tip Thickness | `af://scp_bound_rna/SCP_32\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Little_Toe.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_66 | Ring_Toe: Ring_Toe Base Thickness | `af://scp_bound_rna/SCP_31\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Ring_Toe.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_67 | Ring_Toe: Ring_Toe Distal Length | `af://scp_bound_rna/SCP_31\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Ring_Toe.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_68 | Ring_Toe: Ring_Toe Metacarpal Length | `af://scp_bound_rna/SCP_31\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Ring_Toe.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_69 | Ring_Toe: Ring_Toe Metacarpal Thickness | `af://scp_bound_rna/SCP_31\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Ring_Toe.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_70 | Ring_Toe: Ring_Toe Middle Length | `af://scp_bound_rna/SCP_31\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Ring_Toe.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_71 | Ring_Toe: Ring_Toe Middle Thickness | `af://scp_bound_rna/SCP_31\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Ring_Toe.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_72 | Ring_Toe: Ring_Toe Proximal Length | `af://scp_bound_rna/SCP_31\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Ring_Toe.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_73 | Ring_Toe: Ring_Toe Tip Thickness | `af://scp_bound_rna/SCP_31\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Ring_Toe.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_74 | Middle_Toe: Middle_Toe Base Thickness | `af://scp_bound_rna/SCP_30\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Middle_Toe.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_75 | Middle_Toe: Middle_Toe Distal Length | `af://scp_bound_rna/SCP_30\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Middle_Toe.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_76 | Middle_Toe: Middle_Toe Metacarpal Length | `af://scp_bound_rna/SCP_30\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Middle_Toe.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_77 | Middle_Toe: Middle_Toe Metacarpal Thickness | `af://scp_bound_rna/SCP_30\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Middle_Toe.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_78 | Middle_Toe: Middle_Toe Middle Length | `af://scp_bound_rna/SCP_30\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Middle_Toe.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_79 | Middle_Toe: Middle_Toe Middle Thickness | `af://scp_bound_rna/SCP_30\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Middle_Toe.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_80 | Middle_Toe: Middle_Toe Proximal Length | `af://scp_bound_rna/SCP_30\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Middle_Toe.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_81 | Middle_Toe: Middle_Toe Tip Thickness | `af://scp_bound_rna/SCP_30\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Middle_Toe.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_82 | Index_Toe: Index_Toe Base Thickness | `af://scp_bound_rna/SCP_29\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Index_Toe.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_83 | Index_Toe: Index_Toe Distal Length | `af://scp_bound_rna/SCP_29\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Index_Toe.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_84 | Index_Toe: Index_Toe Metacarpal Length | `af://scp_bound_rna/SCP_29\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Index_Toe.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_85 | Index_Toe: Index_Toe Metacarpal Thickness | `af://scp_bound_rna/SCP_29\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Index_Toe.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_86 | Index_Toe: Index_Toe Middle Length | `af://scp_bound_rna/SCP_29\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Index_Toe.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_87 | Index_Toe: Index_Toe Middle Thickness | `af://scp_bound_rna/SCP_29\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Index_Toe.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_88 | Index_Toe: Index_Toe Proximal Length | `af://scp_bound_rna/SCP_29\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Index_Toe.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_89 | Index_Toe: Index_Toe Tip Thickness | `af://scp_bound_rna/SCP_29\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Index_Toe.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_90 | Big_Toe: Big_Toe Base Thickness | `af://scp_bound_rna/SCP_28\|OBJ_1/modifiers["GeometryNodes"]["Socket_8"]` | `Big_Toe.modifiers["GeometryNodes"]["Socket_8"]` | None | None |
| SHORTCUT_91 | Big_Toe: Big_Toe Distal Length | `af://scp_bound_rna/SCP_28\|OBJ_1/modifiers["GeometryNodes"]["Socket_4"]` | `Big_Toe.modifiers["GeometryNodes"]["Socket_4"]` | None | None |
| SHORTCUT_92 | Big_Toe: Big_Toe Metacarpal Length | `af://scp_bound_rna/SCP_28\|OBJ_1/modifiers["GeometryNodes"]["Socket_12"]` | `Big_Toe.modifiers["GeometryNodes"]["Socket_12"]` | None | None |
| SHORTCUT_93 | Big_Toe: Big_Toe Metacarpal Thickness | `af://scp_bound_rna/SCP_28\|OBJ_1/modifiers["GeometryNodes"]["Socket_13"]` | `Big_Toe.modifiers["GeometryNodes"]["Socket_13"]` | None | None |
| SHORTCUT_94 | Big_Toe: Big_Toe Middle Length | `af://scp_bound_rna/SCP_28\|OBJ_1/modifiers["GeometryNodes"]["Socket_3"]` | `Big_Toe.modifiers["GeometryNodes"]["Socket_3"]` | None | None |
| SHORTCUT_95 | Big_Toe: Big_Toe Middle Thickness | `af://scp_bound_rna/SCP_28\|OBJ_1/modifiers["GeometryNodes"]["Socket_9"]` | `Big_Toe.modifiers["GeometryNodes"]["Socket_9"]` | None | None |
| SHORTCUT_96 | Big_Toe: Big_Toe Proximal Length | `af://scp_bound_rna/SCP_28\|OBJ_1/modifiers["GeometryNodes"]["Socket_2"]` | `Big_Toe.modifiers["GeometryNodes"]["Socket_2"]` | None | None |
| SHORTCUT_97 | Big_Toe: Big_Toe Tip Thickness | `af://scp_bound_rna/SCP_28\|OBJ_1/modifiers["GeometryNodes"]["Socket_10"]` | `Big_Toe.modifiers["GeometryNodes"]["Socket_10"]` | None | None |
| SHORTCUT_98 | Tibia: Tibia Length | `af://scp_bound_rna/SCP_24\|OBJ_1/scale[2]` | `Tibia.scale[2]` | None | SK-D01 |
| SHORTCUT_99 | Femur: Femur Length | `af://scp_bound_rna/SCP_22\|OBJ_1/scale[2]` | `Femur.scale[2]` | None | None |
| SHORTCUT_100 | Femur: Femur Knee Size | `af://scp_bound_rna/SCP_22\|OBJ_3/scale` | `femur_knee_hook.scale` | None | None |
| SHORTCUT_101 | Tarsal_Front: Tarsal_Front Scale | `af://scp_bound_rna/SCP_26\|OBJ_2/scale` | `tarsal_front_hook.scale` | None | None |
| SHORTCUT_102 | Tarsal_Back: Tarsal_Back Scale | `af://scp_bound_rna/SCP_27\|OBJ_3/scale` | `tarsal_back_hook.scale` | None | None |
| SHORTCUT_103 | Knee_Cap: Knee_Cap Size | `af://scp_bound_rna/SCP_33\|OBJ_1/scale` | `Knee_Cap.scale` | None | None |
| SHORTCUT_104 | Knee_Cap: Knee_Cap Protrusion | `af://scp_bound_rna/SCP_33\|OBJ_1/location[1]` | `Knee_Cap.location[1]` | None | None |
| SHORTCUT_105 | Hip Join: Hip Joint Distance | `af://scp_bound_rna/SCP_23\|OBJ_3/["AF Local X"]` | `hip_join_hook.["AF Local X"]` | None | SK-D02, SK-D03, SK-D04 |

### Exact drivers

| ID | Driven channel | Expression / operation | Variables |
| --- | --- | --- | --- |
| SK-D01 | `Fibula.scale[2]` | `AVERAGE(inputs)` | `scale ← Tibia.scale[2]` |
| SK-D02 | `hip_join_hook.location[0]` | `(1.1802628040313721)+(0.6767956018447876*afx)+(0*afy)+(0.73617100715637207*afz)` | `afx ← hip_join_hook.["AF Local X"]; afy ← hip_join_hook.["AF Local Y"]; afz ← hip_join_hook.["AF Local Z"]` |
| SK-D03 | `hip_join_hook.location[1]` | `(0.015050827525556087)+(0*afx)+(1*afy)+(0*afz)` | `afx ← hip_join_hook.["AF Local X"]; afy ← hip_join_hook.["AF Local Y"]; afz ← hip_join_hook.["AF Local Z"]` |
| SK-D04 | `hip_join_hook.location[2]` | `(0.91110622882843018)+(-0.73617100715637207*afx)+(0*afy)+(0.6767956018447876*afz)` | `afx ← hip_join_hook.["AF Local X"]; afy ← hip_join_hook.["AF Local Y"]; afz ← hip_join_hook.["AF Local Z"]` |
| SK-D05 | `ilium_arc.scale[0]` | `var` | `var ← ilium_arc.["Pubis Arc Radius"]` |
| SK-D06 | `ilium_arc.scale[1]` | `var*koef` | `var ← ilium_arc.["Pubis Arc Radius"]; koef ← ilium_arc.["Pubic Arc Shrink"]` |
| SK-D07 | `ilium_arc.scale[2]` | `var` | `var ← ilium_arc.["Pubis Arc Radius"]` |
| SK-D08 | `ilium_arc.["Pubis Arc Radius"][0]` | `var` | `var ← pubis_arc.["Pubis Arc Radius"]` |
| SK-D09 | `ilium_arc.["Pubic Arc Shrink"][0]` | `var` | `var ← pubis_arc.["Pubic Arc Shrink"]` |
| SK-D10 | `ilium_geom.scale[0]` | `angle * r / 2` | `angle ← ilium_geom.["Ilium Seg Angle"]; r ← ilium_arc.["Pubis Arc Radius"]` |
| SK-D11 | `ischium_curve.scale[0]` | `var` | `var ← ischium_curve.["Pubis Arc Radius"]` |
| SK-D12 | `ischium_curve.scale[1]` | `var*koef` | `var ← ischium_curve.["Pubis Arc Radius"]; koef ← ischium_curve.["Pubic Arc Shrink"]` |
| SK-D13 | `ischium_curve.scale[2]` | `var` | `var ← ischium_curve.["Pubis Arc Radius"]` |
| SK-D14 | `ischium_curve.["Pubis Arc Radius"][0]` | `var` | `var ← pubis_arc.["Pubis Arc Radius"]` |
| SK-D15 | `ischium_curve.["Pubic Arc Shrink"][0]` | `var` | `var ← pubis_arc.["Pubic Arc Shrink"]` |
| SK-D16 | `pubis_arc.scale[0]` | `var` | `var ← pubis_arc.["Pubis Arc Radius"]` |
| SK-D17 | `pubis_arc.scale[1]` | `var*koef` | `var ← pubis_arc.["Pubis Arc Radius"]; koef ← pubis_arc.["Pubic Arc Shrink"]` |
| SK-D18 | `pubis_arc.scale[2]` | `var` | `var ← pubis_arc.["Pubis Arc Radius"]` |
| SK-D19 | `pubis_geom.scale[0]` | `angle * r / 2` | `angle ← pubis_geom.["Pubis Arc Angle"]; r ← pubis_arc.["Pubis Arc Radius"]` |
| SK-D20 | `ribs_curve.scale[0]` | `r` | `r ← ribs_curve.["Ribs Arc Radius"]` |
| SK-D21 | `ribs_curve.scale[1]` | `r` | `r ← ribs_curve.["Ribs Arc Radius"]` |
| SK-D22 | `ribs_curve.scale[2]` | `r` | `r ← ribs_curve.["Ribs Arc Radius"]` |
| SK-D23 | `ribs_profile_bottom.scale[0]` | `var` | `var ← ribs_profile_bottom.["Ribs Bottom Radius"]` |
| SK-D24 | `ribs_profile_bottom.scale[1]` | `var` | `var ← ribs_profile_bottom.["Ribs Bottom Radius"]` |
| SK-D25 | `ribs_profile_bottom.scale[2]` | `var` | `var ← ribs_profile_bottom.["Ribs Bottom Radius"]` |
| SK-D26 | `ribs_profile_top.scale[0]` | `var` | `var ← ribs_profile_top.["Ribs Top Radius"]` |
| SK-D27 | `ribs_profile_top.scale[1]` | `var` | `var ← ribs_profile_top.["Ribs Top Radius"]` |
| SK-D28 | `ribs_profile_top.scale[2]` | `var` | `var ← ribs_profile_top.["Ribs Top Radius"]` |
| SK-D29 | `Sacrum.scale[0]` | `var ` | `var ← Sacrum.["Sacrum Width"]` |
| SK-D30 | `Sacrum.["Sacrum Width"][0]` | `r * sin(a/2) *0.67 * s` | `r ← pubis_arc.["Pubis Arc Radius"]; a ← pubis_geom.["Pubis Arc Angle"]; s ← Pubis WORLD_SPACE SCALE_AVG` |
| SK-D31 | `Sternum.["Sternum Width"][0]` | `r * sin (a/2)` | `r ← ribs_curve.["Ribs Arc Radius"]; a ← ribs_geom.modifiers["GeometryNodes"]["Socket_5"]` |
| SK-D32 | `Sternum.scale[1]` | `var ` | `var ← Sternum.["Sternum Width"]` |
| SK-D33 | `Sternum.scale[2]` | `var` | `var ← Sternum.["Sternum Height"]` |
| SK-D34 | `Ulna.scale[0]` | `var` | `var ← Radius WORLD_SPACE SCALE_X` |

## Skull

Source: `E:\development\WIP_models\skull_muscles.blend`

SHA256: `4855042f259135c569c3e89b50df5d0441e6794bef5e774aebf924fd8372287e`

| ID | Owner / shortcut | Saved path | Resolved target | Incoming driver | Downstream drivers |
| --- | --- | --- | --- | --- | --- |
| SHORTCUT_1 | Cranium: Cranium Lobe Width | `bpy.data.objects["frontal_lobe_hook"].scale[0]` | `frontal_lobe_hook.scale[0]` | None | None |
| SHORTCUT_2 | Nasal: Nasal Inner Width | `bpy.data.objects["Nasal Frontal Hook"].scale[0]` | `Nasal Frontal Hook.scale[0]` | None | None |
| SHORTCUT_3 | Nasal: Nasal Outer Width | `bpy.data.objects["Nasal Back Hook"].scale[0]` | `Nasal Back Hook.scale[0]` | None | None |
| SHORTCUT_4 | Maxilla: Maxilla Lower Radius | `bpy.data.objects["maxilla_bottom_curve"].scale` | `maxilla_bottom_curve.scale` | None | None |
| SHORTCUT_5 | Maxilla: Maxilla Top Radius | `bpy.data.objects["maxilla_top_curve"].scale` | `maxilla_top_curve.scale` | None | None |
| SHORTCUT_6 | Maxilla: Maxilla Bottom Location Y | `bpy.data.objects["maxilla_bottom_curve"].location[1]` | `maxilla_bottom_curve.location[1]` | None | None |
| SHORTCUT_7 | Maxilla: Maxilla Top Location Y | `bpy.data.objects["maxilla_top_curve"].location[1]` | `maxilla_top_curve.location[1]` | None | None |
| SHORTCUT_8 | Cheekbone_Front: Cheekbone_Front Protrusion | `bpy.data.objects["Cheekbone_SuperHook"]["AF Local X"]` | `Cheekbone_SuperHook.["AF Local X"]` | None | CR-D04, CR-D05, CR-D06 |
| SHORTCUT_9 | Mandible_Side: Mandible_Side Base Size | `bpy.data.objects["mandible_side_base_hook"].scale` | `mandible_side_base_hook.scale` | None | None |
| SHORTCUT_10 | Ajar_Cartilage: Ajar_Cartilage Protrusion | `bpy.data.objects["ajar_side_hook"]["AF Local Y"]` | `ajar_side_hook.["AF Local Y"]` | None | CR-D01, CR-D02, CR-D03 |
| SHORTCUT_11 | Brow_Ridge: Brow_Ridge Location Y | `bpy.data.objects["front_brow_ridge_hook"].location[1]` | `front_brow_ridge_hook.location[1]` | None | None |

### Exact drivers

| ID | Driven channel | Expression / operation | Variables |
| --- | --- | --- | --- |
| CR-D01 | `ajar_side_hook.location[0]` | `(0.15051068365573883)+(0.40069356560707092*afx)+(-0.91621214151382446*afy)+(3.2752311085459951e-08*afz)` | `afx ← ajar_side_hook.["AF Local X"]; afy ← ajar_side_hook.["AF Local Y"]; afz ← ajar_side_hook.["AF Local Z"]` |
| CR-D02 | `ajar_side_hook.location[1]` | `(-1.1452047824859619)+(0.91621214151382446*afx)+(0.40069356560707092*afy)+(2.4680884891381538e-08*afz)` | `afx ← ajar_side_hook.["AF Local X"]; afy ← ajar_side_hook.["AF Local Y"]; afz ← ajar_side_hook.["AF Local Z"]` |
| CR-D03 | `ajar_side_hook.location[2]` | `(0.99860882759094238)+(-3.573656570665662e-08*afx)+(2.0118591237405781e-08*afy)+(1*afz)` | `afx ← ajar_side_hook.["AF Local X"]; afy ← ajar_side_hook.["AF Local Y"]; afz ← ajar_side_hook.["AF Local Z"]` |
| CR-D04 | `Cheekbone_SuperHook.location[0]` | `(0.65592086315155029)+(0.68440604209899902*afx)+(0.72910106182098389*afy)+(0*afz)` | `afx ← Cheekbone_SuperHook.["AF Local X"]; afy ← Cheekbone_SuperHook.["AF Local Y"]; afz ← Cheekbone_SuperHook.["AF Local Z"]` |
| CR-D05 | `Cheekbone_SuperHook.location[1]` | `(-0.71829688549041748)+(-0.72910106182098389*afx)+(0.68440604209899902*afy)+(0*afz)` | `afx ← Cheekbone_SuperHook.["AF Local X"]; afy ← Cheekbone_SuperHook.["AF Local Y"]; afz ← Cheekbone_SuperHook.["AF Local Z"]` |
| CR-D06 | `Cheekbone_SuperHook.location[2]` | `(0.88610434532165527)+(0*afx)+(0*afy)+(1*afz)` | `afx ← Cheekbone_SuperHook.["AF Local X"]; afy ← Cheekbone_SuperHook.["AF Local Y"]; afz ← Cheekbone_SuperHook.["AF Local Z"]` |
