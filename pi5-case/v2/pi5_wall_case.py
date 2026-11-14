"""
Raspberry Pi 5 wall-mount case
  - 52Pi U2500 HAT (dual 2.5GbE + M.2 NVMe, USB bridge) stack, no cooler
  - Stack is held by 4x M2.5 x 16 button-head screws from the BACK of the case,
    through the Pi, into the U2500's female standoffs
  - USB/Ethernet end points DOWN when hung
  - Two keyhole slots in the back for wall screws (#6/#8 pan head or 4 mm)

Coordinates (mm): Pi PCB lies in X/Y with its corner at (0,0).
  X = 0..85  (USB/Ethernet end at X = 85 -> "down" on the wall)
  Y = 0..56  (Y = 0 edge has USB-C power + 2x micro-HDMI; Y = 56 is the GPIO side)
  Z = 0      is the back of the case (flat against the wall)

Run:  pip install manifold3d trimesh numpy
      python3 pi5_wall_case.py      -> pi5_case_base.stl, pi5_case_lid.stl
"""
from manifold3d import Manifold, set_circular_segments
import numpy as np
import trimesh

set_circular_segments(64)

# ---------------------------------------------------------------- parameters
WALL        = 2.4    # side wall thickness
FLOOR       = 6.4    # back thickness (holds the keyhole head channel)
STANDOFF_H  = 5.0    # floor -> underside of Pi PCB (microSD + underside parts)
PCB_T       = 1.4    # Pi 5 PCB thickness
HAT_TOP     = 18.55  # measured: Pi PCB top -> U2500 PCB top
ABOVE_HAT   = 8.45 + 2.0   # measured HAT PCB top -> top of RJ45 jacks, + air gap

# interior clearances around the 85 x 56 board
GAP_X_TOP   = 6.0    # X- end (top on the wall): room for the PCIe ribbon loop
GAP_X_USB   = 0.5    # X+ end: ports poke into the wall opening
GAP_Y       = 1.5

# Pi mounting holes (M2.5)
PI_HOLES    = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
STANDOFF_D  = 6.5
SCREW_D     = 2.9    # M2.5 clearance, screw enters from the back of the case
SCREW_L     = 16.0   # M2.5 x 16 button head
HEAD_D      = 5.0    # counterbore for the head (button head ~4.7 dia)
HEAD_DEPTH  = 1.8    # counterbore depth (head ~1.3 tall) -> back stays flat on wall

# lid screws (M3) in external corner bosses
BOSS_R      = 4.5
LID_PILOT_D = 2.6    # M3 self-tapping / thread-forming into plastic
LID_CLEAR_D = 3.4
LID_T       = 2.4
LIP_H       = 1.5
LIP_W       = 1.2
FIT         = 0.25   # lid lip clearance

# keyholes (on the back). Slot runs toward X- (up on the wall) from the entry hole.
KEY_ENTRY_D = 9.5    # screw head passes through here
KEY_SHANK_W = 4.6    # screw shank slides in this slot
KEY_SLOT_L  = 10.0   # travel from entry centre to resting position
KEY_BACK_T  = 2.0    # material between wall and screw head
KEY_HEAD_T  = 3.0    # head channel depth
KEY_X       = [22.0, 79.0]   # entry-hole centres (board X coords)
KEY_Y       = 28.0

# ---------------------------------------------------------------- derived
PCB_Z0   = FLOOR + STANDOFF_H
PCB_Z1   = PCB_Z0 + PCB_T
HAT_Z1   = PCB_Z1 + HAT_TOP
TOP_Z    = HAT_Z1 + ABOVE_HAT                 # top of walls / underside of lid

IX0, IX1 = -GAP_X_TOP, 85 + GAP_X_USB         # interior extents
IY0, IY1 = -GAP_Y, 56 + GAP_Y
OX0, OX1 = IX0 - WALL, IX1 + WALL             # outer extents
OY0, OY1 = IY0 - WALL, IY1 + WALL
BOSSES   = [(OX0, OY0), (OX1, OY0), (OX0, OY1), (OX1, OY1)]


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def slot_x(x0, x1, y, z0, z1, w):
    """Rounded-end slot running along X (stadium), extruded in Z."""
    r = w / 2
    return (box(x0, x1, y - r, y + r, z0, z1)
            + cyl(x0, y, z0, z1, w) + cyl(x1, y, z0, z1, w))


# ---------------------------------------------------------------- base
def base():
    shell = box(OX0, OX1, OY0, OY1, 0, TOP_Z)
    for bx, by in BOSSES:
        shell += cyl(bx, by, 0, TOP_Z, 2 * BOSS_R)
    shell -= box(IX0, IX1, IY0, IY1, FLOOR, TOP_Z + 1)

    # Pi standoffs, drilled through to the back with a counterbore for the head
    for hx, hy in PI_HOLES:
        shell += cyl(hx, hy, FLOOR - 0.01, PCB_Z0, STANDOFF_D)
        shell -= cyl(hx, hy, -1, PCB_Z0 + 1, SCREW_D)
        shell -= cyl(hx, hy, -1, HEAD_DEPTH, HEAD_D)

    # lid screw pilots
    for bx, by in BOSSES:
        shell -= cyl(bx, by, TOP_Z - 12, TOP_Z + 1, LID_PILOT_D)

    cut = Manifold()
    # X+ end: USB 3 / USB 2 / Ethernet (open to the top -> no long bridge, doubles as air intake)
    cut += box(IX1 - 1, OX1 + 1, 1.0, 55.0, PCB_Z0 - 0.5, TOP_Z + 1)
    # Y=0 side: USB-C power + 2x micro-HDMI (one slot, room for plug overmoulds)
    cut += box(3.0, 48.0, OY0 - 1, IY0 + 1, PCB_Z0 - 0.5, PCB_Z1 + 9.0)
    # X- end: microSD (under the PCB) + power button / ribbon access
    cut += box(OX0 - 1, IX0 + 1, 10.0, 46.0, PCB_Z0 - 4.0, PCB_Z1 + 5.0)
    # X- end upper exhaust slits (top of the case on the wall -> chimney airflow)
    for i in range(5):
        y = 8 + i * 10
        z0 = PCB_Z1 + 8
        cut += box(OX0 - 1, IX0 + 1, y - 1.25 + 3, y + 1.25 + 3, z0, TOP_Z - 3)
    # side vents, long slits run along X (vertical when hung)
    for z in np.arange(PCB_Z1 + 3, TOP_Z - 4, 4.5):
        for xa, xb in [(8, 28), (34, 54), (60, 78)]:            # GPIO side
            cut += box(xa, xb, IY1 - 1, OY1 + 1, z, z + 2.2)
        cut += box(54, 78, OY0 - 1, IY0 + 1, z, z + 2.2)        # HDMI side, past ports
    shell -= cut

    # keyholes: entry hole + shank slot through the back layer,
    # head channel above it, solid cap between channel and the Pi
    for kx in KEY_X:
        rest = kx - KEY_SLOT_L
        shell -= cyl(kx, KEY_Y, -1, KEY_BACK_T + 0.01, KEY_ENTRY_D)
        shell -= slot_x(rest, kx, KEY_Y, -1, KEY_BACK_T + 0.01, KEY_SHANK_W)
        shell -= slot_x(rest, kx, KEY_Y, KEY_BACK_T, KEY_BACK_T + KEY_HEAD_T,
                        KEY_ENTRY_D + 0.3)
    return shell


# ---------------------------------------------------------------- lid
def lid():
    # modelled in place (sits on top of the walls); flipped for printing later
    plate = box(OX0, OX1, OY0, OY1, TOP_Z, TOP_Z + LID_T)
    for bx, by in BOSSES:
        plate += cyl(bx, by, TOP_Z, TOP_Z + LID_T, 2 * BOSS_R)
    # locating lip that drops inside the walls (skips the open USB end)
    lx0, lx1 = IX0 + FIT, IX1 - 3
    ly0, ly1 = IY0 + FIT, IY1 - FIT
    lip = box(lx0, lx1, ly0, ly1, TOP_Z - LIP_H, TOP_Z + 0.01)
    lip -= box(lx0 + LIP_W, lx1 - LIP_W, ly0 + LIP_W, ly1 - LIP_W, TOP_Z - LIP_H - 1, TOP_Z + 1)
    plate += lip
    for bx, by in BOSSES:
        plate -= cyl(bx, by, TOP_Z - 5, TOP_Z + LID_T + 1, LID_CLEAR_D)
    # vent slots, run along X (vertical when hung), over the HAT/SSD
    for i in range(9):
        y = 6 + i * 5.5
        plate -= slot_x(4, 74, y, TOP_Z - 5, TOP_Z + LID_T + 1, 2.6)
    return plate


# ---------------------------------------------------------------- drill template
TEMPLATE_T  = 1.2
MARK_D      = 3.0    # pencil / awl hole at each final screw position

def template():
    """Plate matching the case back. Holes mark where the screws END UP
    (resting end of each keyhole), so mark through them and drill there."""
    from manifold3d import CrossSection
    plate = box(OX0, OX1, OY0, OY1, 0, TEMPLATE_T)
    for bx, by in BOSSES:
        plate += cyl(bx, by, 0, TEMPLATE_T, 2 * BOSS_R)
    for kx in KEY_X:
        rest = kx - KEY_SLOT_L
        plate -= cyl(rest, KEY_Y, -1, TEMPLATE_T + 1, MARK_D)
        # crosshair slits for marking the centre lines
        plate -= box(rest - 0.5, rest + 0.5, KEY_Y - 12, KEY_Y - 3, -1, TEMPLATE_T + 1)
        plate -= box(rest - 0.5, rest + 0.5, KEY_Y + 3, KEY_Y + 12, -1, TEMPLATE_T + 1)
        plate -= box(rest - 12, rest - 3, KEY_Y - 0.5, KEY_Y + 0.5, -1, TEMPLATE_T + 1)
        plate -= box(rest + 3, rest + 12, KEY_Y - 0.5, KEY_Y + 0.5, -1, TEMPLATE_T + 1)
    # "UP" arrow cut-out pointing toward X- (top of the case when hung)
    mid = (KEY_X[0] + KEY_X[1]) / 2 - KEY_SLOT_L
    arrow = CrossSection([[
        (mid - 10, KEY_Y), (mid, KEY_Y - 8), (mid, KEY_Y - 3), (mid + 12, KEY_Y - 3),
        (mid + 12, KEY_Y + 3), (mid, KEY_Y + 3), (mid, KEY_Y + 8)]])
    plate -= arrow.extrude(TEMPLATE_T + 2).translate([0, 0, -1])
    return plate


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=True)


if __name__ == "__main__":
    b = to_trimesh(base())
    # base prints back-down as modelled; move to origin
    b.apply_translation(-b.bounds[0])
    b.export("pi5_case_base.stl")

    l = to_trimesh(lid())
    # flip so the flat outer face is on the bed, lip pointing up
    l.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    l.apply_translation(-l.bounds[0])
    l.export("pi5_case_lid.stl")

    t = to_trimesh(template())
    t.apply_translation(-t.bounds[0])
    t.export("pi5_drill_template.stl")

    for name, m in [("base", b), ("lid", l), ("template", t)]:
        print(f"{name}: {np.round(m.extents, 1)} mm, watertight={m.is_watertight}, "
              f"volume={m.volume / 1000:.1f} cm3")
    print(f"PCB top z={PCB_Z1:.1f}, HAT top z={HAT_Z1:.1f}, wall top z={TOP_Z:.1f}")
    print(f"Stack screw thread into HAT standoff: {SCREW_L - (PCB_Z1 - HEAD_DEPTH):.1f} mm")
    print(f"Wall screw spacing: {KEY_X[1] - KEY_X[0]:.1f} mm (vertical, on centre line)")
