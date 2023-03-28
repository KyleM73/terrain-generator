import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass

from numpy.random import f

from trimesh_tiles.mesh_parts.mesh_parts_cfg import (
    MeshPattern,
    MeshPartsCfg,
    WallPartsCfg,
    StairMeshPartsCfg,
    PlatformMeshPartsCfg,
    HeightMapMeshPartsCfg,
)
from trimesh_tiles.mesh_parts.rough_parts import generate_perlin_tile_configs

from trimesh_tiles.patterns.pattern_generator import (
    generate_random_box_platform,
    generate_walls,
    generate_floating_boxes,
    generate_narrow,
    generate_platforms,
    generate_ramp_parts,
    generate_stair_parts,
    generate_stepping_stones,
    generate_floating_capsules,
    generate_random_boxes,
    generate_overhanging_platforms,
    add_capsules,
)
from trimesh_tiles.mesh_parts.create_tiles import create_mesh_tile
from trimesh_tiles.mesh_parts.basic_parts import create_from_height_map


@dataclass
class OverhangingPattern(MeshPattern):
    dim: Tuple[float, float, float] = (2.0, 2.0, 2.0)  # x, y, z
    seed: int = 1234

    # random box platform
    random_boxes_cfg = []
    n_random_boxes: int = 10
    random_box_weight: float = 0.1
    for i in range(n_random_boxes):
        random_boxes_cfg += generate_random_box_platform(
            name=f"box_platform_flat_{i}",
            offset=0.0,
            height_diff=0.0,
            height_std=0.2,
            n=6,
            dim=dim,
            weight=random_box_weight / n_random_boxes,
        )
        random_boxes_cfg += generate_random_box_platform(
            name=f"box_platform_flat_8_{i}",
            offset=0.0,
            height_diff=0.0,
            height_std=0.2,
            n=8,
            dim=dim,
            weight=random_box_weight / n_random_boxes,
        )
        random_boxes_cfg += generate_random_box_platform(
            name=f"box_platform_0.0{i}",
            offset=0.0,
            height_diff=0.5,
            height_std=0.1,
            n=6,
            dim=dim,
            weight=random_box_weight / n_random_boxes,
        )
        random_boxes_cfg += generate_random_box_platform(
            name=f"box_platform_0.5{i}",
            offset=0.5,
            height_diff=0.5,
            height_std=0.1,
            n=6,
            dim=dim,
            weight=random_box_weight / n_random_boxes,
        )
        random_boxes_cfg += generate_random_box_platform(
            name=f"box_platform_1.0_{i}",
            offset=1.0,
            height_diff=0.5,
            height_std=0.1,
            n=6,
            dim=dim,
            weight=random_box_weight / n_random_boxes,
        )
        random_boxes_cfg += generate_random_box_platform(
            name=f"box_platform_1.5_{i}",
            offset=1.5,
            height_diff=0.5,
            height_std=0.1,
            n=6,
            dim=dim,
            weight=random_box_weight / n_random_boxes,
        )
        random_boxes_cfg += generate_random_box_platform(
            name=f"box_platform_diff_1.0_{i}",
            offset=0.0,
            height_diff=1.0,
            height_std=0.1,
            n=6,
            dim=dim,
            weight=random_box_weight / n_random_boxes,
        )
    mesh_parts: Tuple[MeshPartsCfg, ...] = (
        (WallPartsCfg(name=f"floor", dim=dim, wall_edges=(), weight=0.01),)
        + tuple(generate_platforms(name="platform_1", dim=dim, max_h=1.0, min_h=0.0, weight=0.5))
        + tuple(generate_platforms(name="platform_2", dim=dim, max_h=2.0, min_h=0.0, weight=0.5))
        + tuple(generate_platforms(name="platform_2_1", dim=dim, max_h=2.0, min_h=1.0, weight=0.5))
        + tuple(generate_platforms(name="platform_0.5", dim=dim, max_h=0.5, min_h=0.0, weight=0.5))
        + tuple(generate_platforms(name="platform_1_0.5", dim=dim, max_h=1.0, min_h=0.5, weight=0.5))
        + tuple(random_boxes_cfg)
        + tuple(generate_stair_parts(name="stair", dim=dim, seed=seed, array_shape=[15, 15], weight=0.5, depth_num=2))
        + tuple(
            generate_stair_parts(
                name="stair_offset", dim=dim, seed=seed, array_shape=[15, 15], weight=2.0, depth_num=2, offset=1.0
            )
        )
        + tuple(
            generate_stair_parts(
                name="stair_low", dim=dim, total_height=0.5, seed=seed, array_shape=[15, 15], weight=0.5, depth_num=2
            )
        )
        + tuple(
            generate_stair_parts(
                name="stair_low_offset",
                dim=dim,
                total_height=0.5,
                offset=0.5,
                seed=seed,
                array_shape=[15, 15],
                weight=0.5,
                depth_num=2,
            )
        )
        + tuple(
            generate_stair_parts(
                name="stair_low_offset_1",
                dim=dim,
                total_height=0.5,
                offset=1.0,
                seed=seed,
                array_shape=[15, 15],
                weight=0.5,
                depth_num=2,
            )
        )
        + tuple(
            generate_stair_parts(
                name="stair_low_offset_2",
                dim=dim,
                total_height=0.5,
                offset=1.5,
                seed=seed,
                array_shape=[15, 15],
                weight=0.5,
                depth_num=2,
            )
        )
        # + tuple(
        #     generate_ramp_parts(
        #         name="ramp",
        #         dim=dim,
        #         seed=seed,
        #         array_shape=[30, 30],
        #         total_height=1.0,
        #         offset=0.00,
        #         weight=1.0,
        #         depth_num=1,
        #     )
        # )
        + tuple(
            generate_ramp_parts(
                name="ramp_low",
                dim=dim,
                seed=seed,
                array_shape=[30, 30],
                total_height=0.5,
                offset=0.00,
                weight=0.2,
                depth_num=1,
            )
        )
    )


if __name__ == "__main__":
    from utils import get_height_array_of_mesh

    cfg = OverhangingPattern()
    # print(cfg)
    keywords = ["mesh"]
    for mesh_part in cfg.mesh_parts:
        print("name ", mesh_part.name)
        if any([keyword in mesh_part.name for keyword in keywords]):
            print(mesh_part)
            tile = create_mesh_tile(mesh_part)
            print("tile ", tile)
            mesh = tile.get_mesh()
            print("mesh ", mesh)
            mesh.show()
            print(get_height_array_of_mesh(mesh, mesh_part.dim, 5))
