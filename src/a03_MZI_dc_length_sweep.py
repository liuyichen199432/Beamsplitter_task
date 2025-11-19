import numpy as np
from gdsfactory.generic_tech import get_generic_pdk
import gdsfactory as gf
import os
from src.a02_MZI_with_fiber_array import my_folded_MZI, connect_ports_conditional

generic_pdk = get_generic_pdk()
generic_pdk.activate()
GDS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gds")
os.makedirs(GDS_FOLDER, exist_ok=True)

circuit_width = 0.45
dc_gap = 0.25
dc_yshift = 4.0
short_wg_yshift = 30
arm_length_dif = 200
bend_radius = 5.0
grating_pitch = 30
gc_xshift = 20
wg_xs = gf.cross_section.strip(width=circuit_width)
dc_length_list = np.linspace(2.0, 18.0, 9)
np.random.shuffle(dc_length_list)
each_grating = gf.components.grating_coupler_te()
my_grating_array = gf.components.grating_coupler_array(
    grating_coupler=each_grating,
    pitch=grating_pitch,
    n=2 + len(dc_length_list) * 4,
    rotation=-90,
    with_loopback=True,
    cross_section=wg_xs,
)
doe_top = gf.Component(name="MZI_dc_length_sweep")
grating_ref = doe_top.add_ref(my_grating_array)
grating_ref.rotate(-90)

for index, dc_length in enumerate(dc_length_list):

    mzi = my_folded_MZI(
        this_cross=wg_xs,
        this_dc_length=dc_length,
        this_dc_gap=dc_gap,
        this_dc_yshift=dc_yshift,
        this_short_wg_yshift=short_wg_yshift,
        this_arm_length_dif=arm_length_dif,
        this_bend_radius=bend_radius,
    )

    mzi_ref = doe_top.add_ref(mzi)
    mzi_ref.move((0, -index * grating_pitch * 4))

    if index == 0:
        mzi_o1_pos = mzi.ports["o1"].center
        mzi_o2_pos = mzi.ports["o2"].center
        mzi_o3_pos = mzi.ports["o3"].center
        mzi_o4_pos = mzi.ports["o4"].center

        gc_o1_pos = grating_ref.ports["o1"].center
        gc_o2_pos = grating_ref.ports["o2"].center
        gc_o3_pos = grating_ref.ports["o3"].center
        gc_o4_pos = grating_ref.ports["o4"].center

        gc_y_mid = gc_o2_pos[1] / 2 + gc_o3_pos[1] / 2
        mzi_y_mid = mzi_o2_pos[1] / 2 + mzi_o3_pos[1] / 2

        grating_ref.move((-gc_xshift - gc_o1_pos[0] + mzi_o1_pos[0], mzi_y_mid - gc_y_mid))

    wg1 = connect_ports_conditional(doe_top, mzi_ref.ports["o1"], grating_ref.ports[f"o{4*index+1}"], wg_xs, bend_radius)
    wg2 = connect_ports_conditional(doe_top, mzi_ref.ports["o2"], grating_ref.ports[f"o{4*index+2}"], wg_xs, bend_radius)
    wg3 = connect_ports_conditional(doe_top, mzi_ref.ports["o3"], grating_ref.ports[f"o{4*index+3}"], wg_xs, bend_radius)
    wg4 = connect_ports_conditional(doe_top, mzi_ref.ports["o4"], grating_ref.ports[f"o{4*index+4}"], wg_xs, bend_radius)


current_file = os.path.basename(__file__)[:-3]
gds_path = os.path.join(GDS_FOLDER, current_file+'.gds')
doe_top.write_gds(gds_path)
print(f"GDS written to {gds_path}")
