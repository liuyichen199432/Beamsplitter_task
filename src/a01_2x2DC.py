from gdsfactory.generic_tech import get_generic_pdk
import gdsfactory as gf
import os

generic_pdk = get_generic_pdk()
generic_pdk.activate()

GDS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gds")
os.makedirs(GDS_FOLDER, exist_ok=True)

# 参数
length = 13.0
gap = 0.25
width = 0.5

# 原始 dc 组件
my_test_dc = gf.components.coupler(
    gap=gap,
    length=length,
    dy=4.0,
    dx=6.5,
    cross_section="strip",
    allow_min_radius_violation=False,
    bend="bend_s",
)

# 创建顶层 component，指定顶层名字
top = gf.Component(name=f"2x2dc_L{length}_G{gap}_w{width}")
top.add_ref(my_test_dc)  # 添加原 dc 作为 reference

# 写入 GDS
current_file = os.path.basename(__file__)[:-3]
gds_path = os.path.join(GDS_FOLDER, current_file+'.gds')
top.write_gds(gds_path)

print(f"GDS written to {gds_path} with top-level name: {top.name}")
