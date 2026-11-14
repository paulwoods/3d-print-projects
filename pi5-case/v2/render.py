"""
Render an exploded view of the case (lid lifted above the base) to render.png.

Run:  blender -b -P render.py

Reads pi5_case_base.stl and pi5_case_lid.stl from this directory. The lid is
positioned from the two parts' bounding boxes, so nothing here depends on the
dimensions in pi5_wall_case.py.
"""
import math
import os

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
GAP = 30.0                      # mm between the top of the base and the lid
VIEW_DIR = Vector((1.0, -1.0, 0.9))   # camera direction from the case: port end, USB-C side, above


def load(name):
    bpy.ops.wm.stl_import(filepath=os.path.join(HERE, name))
    return bpy.context.selected_objects[0]


def bounds(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    return lo, hi


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

base = load("pi5_case_base.stl")
lid = load("pi5_case_lid.stl")

# The lid is exported flipped for printing: turn it back over, then put it
# over the base (same outline, so the bounding boxes line up) and lift it.
lid.rotation_euler = (math.pi, 0, 0)
bpy.context.view_layer.update()
base_lo, base_hi = bounds(base)
lid_lo, _ = bounds(lid)
lid.location += Vector((base_lo.x - lid_lo.x, base_lo.y - lid_lo.y,
                        base_hi.z + GAP - lid_lo.z))

lime = bpy.data.materials.new("lime")
lime.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.22, 0.55, 0.03, 1)
for obj in (base, lid):
    obj.data.materials.append(lime)

world = bpy.data.worlds.new("world")
# The world lights the model with a bright colour but shows the camera a dark one.
nodes, links = world.node_tree.nodes, world.node_tree.links
ambient = nodes["Background"]
ambient.inputs["Color"].default_value = (0.9, 0.9, 0.9, 1)
backdrop = nodes.new("ShaderNodeBackground")
backdrop.inputs["Color"].default_value = (0.015, 0.015, 0.02, 1)
mix = nodes.new("ShaderNodeMixShader")
links.new(nodes.new("ShaderNodeLightPath").outputs["Is Camera Ray"], mix.inputs[0])
links.new(ambient.outputs[0], mix.inputs[1])
links.new(backdrop.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], nodes["World Output"].inputs["Surface"])
scene.world = world

sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(50), 0, math.radians(20))
scene.collection.objects.link(sun)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.clip_end = 10000       # the model is in mm, so it is hundreds of units across
cam.rotation_euler = VIEW_DIR.to_track_quat("Z", "Y").to_euler()
scene.collection.objects.link(cam)
scene.camera = cam

bpy.ops.object.select_all(action="DESELECT")
base.select_set(True)
lid.select_set(True)
bpy.ops.view3d.camera_to_view_selected()   # move the camera back until both parts fit

scene.view_settings.view_transform = "Standard"
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.filepath = os.path.join(HERE, "render.png")
bpy.ops.render.render(write_still=True)
