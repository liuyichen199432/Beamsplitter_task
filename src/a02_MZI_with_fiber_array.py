from gdsfactory.generic_tech import get_generic_pdk
import gdsfactory as gf
import os

generic_pdk = get_generic_pdk()
generic_pdk.activate()
GDS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gds")
os.makedirs(GDS_FOLDER, exist_ok=True)


def my_folded_MZI(
        this_cross,
        this_dc_length=13.0,
        this_dc_gap=0.25,
        this_dc_yshift=4.0,
        this_short_wg_yshift=30,
        this_arm_length_dif=100,
        this_bend_radius=5.0,
):
    top = gf.Component(name="folded_mzi_dc_length_" + str(this_dc_length))

    my_test_dc1 = gf.components.coupler(
        gap=this_dc_gap,
        length=this_dc_length,
        dy=this_dc_yshift,
        dx=6.5,
        cross_section=this_cross,
        allow_min_radius_violation=False,
        bend="bend_s",
    )
    combiner_ref = top.add_ref(my_test_dc1)

    points = [
        (0, 0),
        (8, 0),
        (8, -this_short_wg_yshift),
        (0, -this_short_wg_yshift),
    ]
    p_short = gf.path.smooth(points, radius=this_bend_radius, bend=gf.path.euler)
    wg_short = p_short.extrude(cross_section=wg_xs)
    wg_short_start_port = wg_short.ports["o1"]
    combiner_o4_port = combiner_ref.ports["o4"]
    dx = combiner_o4_port.center[0] - wg_short_start_port.center[0]
    dy = combiner_o4_port.center[1] - wg_short_start_port.center[1]
    wg_short.move((dx, dy))
    wg_short_ref = top.add_ref(wg_short)
    wg_short_length = p_short.length()
    wg_long_length_true = this_arm_length_dif + wg_short_length

    my_test_dc2 = gf.components.coupler(
        gap=this_dc_gap,
        length=this_dc_length,
        dy=this_dc_yshift,
        dx=6.5,
        cross_section=this_cross,
        allow_min_radius_violation=False,
        bend="bend_s",
    )
    splitter_ref = top.add_ref(my_test_dc2)
    dc_o3 = splitter_ref.ports["o3"]
    wg_end_port = wg_short_ref.ports["o2"]
    dx = wg_end_port.center[0] - dc_o3.center[0]
    dy = wg_end_port.center[1] - dc_o3.center[1]
    splitter_ref.move((dx, dy))

    points = [
        (0, this_dc_yshift),
        (20, this_dc_yshift),
        (20, -this_short_wg_yshift - this_dc_yshift),
        (0, -this_short_wg_yshift - this_dc_yshift),
    ]
    p_long_temp = gf.path.smooth(points, radius=this_bend_radius, bend=gf.path.euler)
    wg_long_length_temp = p_long_temp.length()
    wg_long_length_rest = wg_long_length_true - wg_long_length_temp
    points = [
        (0, this_dc_yshift),
        (20 + wg_long_length_rest / 2, this_dc_yshift),
        (20 + wg_long_length_rest / 2, -this_short_wg_yshift - this_dc_yshift),
        (0, -this_short_wg_yshift - this_dc_yshift),
    ]
    p_long = gf.path.smooth(points, radius=this_bend_radius, bend=gf.path.euler)
    wg_long = p_long.extrude(cross_section=wg_xs)
    wg_long_start_port = wg_long.ports["o1"]
    combiner_o3_port = combiner_ref.ports["o3"]
    dx = combiner_o3_port.center[0] - wg_long_start_port.center[0]
    dy = combiner_o3_port.center[1] - wg_long_start_port.center[1]
    wg_long.move((dx, dy))
    wg_long_ref = top.add_ref(wg_long)

    top.add_port("o1", port=combiner_ref.ports["o2"])
    top.add_port("o2", port=combiner_ref.ports["o1"])
    top.add_port("o3", port=splitter_ref.ports["o2"])
    top.add_port("o4", port=splitter_ref.ports["o1"])

    return top


def connect_ports_conditional(top, port1, port2, cross_section, bend_radius=5.0):
    x1, y1 = port1.center
    x2, y2 = port2.center

    if abs(y2 - y1) < 1e-6:  # y 坐标相同，直接直线
        points = [(x1, y1), (x2, y2)]
    else:  # y 不同，生成平滑 Euler 弯曲
        points = [
            (x1, y1),
            ((x1 + x2) / 2, y1),
            ((x1 + x2) / 2, y2),
            (x2, y2),
        ]
    path = gf.path.smooth(points, radius=bend_radius, bend=gf.path.euler)
    wg = path.extrude(cross_section=cross_section)
    return top.add_ref(wg)


circuit_width = 0.45
dc_length = 13
dc_gap = 0.25
dc_yshift = 4.0
short_wg_yshift = 30
arm_length_dif = 200
bend_radius = 5.0
gc_xshift = 20
wg_xs = gf.cross_section.strip(width=circuit_width)

if __name__ == "__main__":
    mzi = my_folded_MZI(
        this_cross=wg_xs,
        this_dc_length=dc_length,
        this_dc_gap=dc_gap,
        this_dc_yshift=dc_yshift,
        this_short_wg_yshift=short_wg_yshift,
        this_arm_length_dif=arm_length_dif,
        this_bend_radius=bend_radius,
    )

    each_grating = gf.components.grating_coupler_te()
    my_grating_array = gf.components.grating_coupler_array(
        grating_coupler=each_grating,
        pitch=30.0,
        n=6,
        port_name="o1",
        rotation=-90,
        with_loopback=True,
        cross_section=wg_xs,
    )

    top = gf.Component(name="mzi_with_grating")

    mzi_ref = top.add_ref(mzi)
    mzi_ref.move((0, 0))

    grating_ref = top.add_ref(my_grating_array)
    grating_ref.rotate(-90)

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

    wg1 = connect_ports_conditional(top, mzi_ref.ports["o1"], grating_ref.ports["o1"], wg_xs, bend_radius)
    wg2 = connect_ports_conditional(top, mzi_ref.ports["o2"], grating_ref.ports["o2"], wg_xs, bend_radius)
    wg3 = connect_ports_conditional(top, mzi_ref.ports["o3"], grating_ref.ports["o3"], wg_xs, bend_radius)
    wg4 = connect_ports_conditional(top, mzi_ref.ports["o4"], grating_ref.ports["o4"], wg_xs, bend_radius)

    current_file = os.path.basename(__file__)[:-3]
    gds_path = os.path.join(GDS_FOLDER, current_file + '.gds')
    top.write_gds(gds_path)
    print(f"GDS written to {gds_path}")
