import numpy as np
import trimesh
from typing import Dict, Optional

from .wfc import Direction2D, Direction3D


class Tile:
    """Class to manage the tiles."""
    def __init__(self, name:str, edges=Dict[str, str], dimension:int=2, weight:float=1.0):
        """ Tile definition for the WFC algorithm.
        Args:
            name (str): Name of the tile.
            edges (Dict[str, str]): Dictionary of the edges of the tile. The keys are the directions and the values are the name of the edge.
        Example:
            tile = Tile(name="tile1", edges={"up": "edge1", "right": "edge2", "bottom": "edge3", "left": "edge4"})
        """
        self.name = name
        self.dimension = dimension
        self.edges = edges
        self.weight = weight
        self.directions = Direction2D() if dimension == 2 else Direction3D()

    def get_dict_tile(self):
        return self.name, self.edges, self.weight

    def get_flipped_tile(self, direction):
        if direction not in ["x", "y", "z"]:
            raise ValueError(f"Direction {direction} is not defined.")
        new_name = f"{self.name}_{direction}"
        new_edges = {}
        for key, value in self.edges.items():
            new_key = self.directions.flipped_directions[direction][self.directions.base_directions.index(key)]
            if key in self.directions.is_edge_flipped[direction]:
                new_edges[new_key] = value[::-1]
            else:
                new_edges[new_key] = value
        return Tile(name=new_name, edges=new_edges, dimension=self.dimension)

    def get_rotated_tile(self, deg):
        if deg not in self.directions.directions:
            raise ValueError(f"Rotation degree {deg} is not defined.")
        new_name = f"{self.name}_{deg}"
        basic_directions = self.directions.directions[0]
        new_directions = self.directions.directions[deg]
        new_edges = {new_key: self.edges[key] for new_key, key in zip(new_directions, basic_directions)}
        return Tile(name=new_name, edges=new_edges, dimension=self.dimension)

    def get_all_tiles(self, rotations=(), flips=()):
        tiles = [self]
        for rotation in rotations:
            tiles.append(self.get_rotated_tile(rotation))
        for flip_direction in flips:
            tiles.append(self.get_flipped_tile(flip_direction))
            for rotation in rotations:
                tiles.append(self.get_flipped_tile(flip_direction).get_rotated_tile(rotation))
        return tiles

    def __str__(self):
        return f"Tile {self.name} with edges {self.edges}, weight {self.weight}"


class ArrayTile(Tile):
    """Class to manage the tiles."""

    def __init__(self, name:str, array:np.ndarray, edges:Optional[Dict[str, str]]=None, dimension:int=2, weight:float=1.0):
        self.array = array
        self.directions = Direction2D()
        if edges is None:
            edges = self.create_edges_from_array(array)
        super().__init__(name, edges, dimension, weight)
    def get_array(self, name=None):
        if name is None:
            return self.array
        for deg in (90, 180, 270):
            if name == f"{self.name}_{deg}":
                a = deg // 90
                return np.rot90(self.array, a)

    def get_flipped_tile(self, direction):
        # flip array
        if direction == "x":
            array = np.flip(self.array, 0)
        elif direction == "y":
            array = np.flip(self.array, 1)
        else:
            raise ValueError(f"Direction {direction} is not defined.")
        tile = super().get_flipped_tile(direction)
        return ArrayTile(
            name=tile.name, array=array, edges=tile.edges, dimension=self.dimension
        )

    def get_rotated_tile(self, deg):
        if deg not in self.directions.directions:
            raise ValueError(f"Rotation degree {deg} is not defined.")
        a = deg // 90
        array = np.rot90(self.array, a)
        tile = super().get_rotated_tile(deg)
        return ArrayTile(
            name=tile.name, array=array, edges=tile.edges, dimension=self.dimension
        )

    def get_all_tiles(self, rotations=(), flips=()):
        tiles = [self]
        for rotation in rotations:
            tiles.append(self.get_rotated_tile(rotation))
        for flip_direction in flips:
            tiles.append(self.get_flipped_tile(flip_direction))
            for rotation in rotations:
                tiles.append(self.get_flipped_tile(flip_direction).get_rotated_tile(rotation))
        return tiles

    def create_edges_from_array(self, array):
        """Create a hash for each edge of the tile."""
        edges = {}
        for direction in self.directions.base_directions:
            if direction == "up":
                edges[direction] = tuple(array[0, :])
            elif direction == "down":
                edges[direction] = tuple(array[-1, :][::-1])
            elif direction == "left":
                edges[direction] = tuple(array[:, 0][::-1])
            elif direction == "right":
                edges[direction] = tuple(array[:, -1])
            else:
                raise ValueError(f"Direction {direction} is not defined.")
        return edges

    def __str__(self):
        return super().__str__() + f"\n {self.array}"


class MeshTile(ArrayTile):
    def __init__(self, name:str, array:np.ndarray, mesh:trimesh.Trimesh, edges:Optional[Dict[str, str]]=None, dimension:int=2, weight:float=1.0):
        self.mesh = mesh
        super().__init__(name, array, edges, dimension, weight=weight)

    def get_flipped_tile(self, direction):
        # flip array
        mesh = self.mesh.copy()
        if direction == "x":
            # Create the transformation matrix for inverting the mesh in the x-axis
            transform = trimesh.transformations.scale_matrix(-1, [0, 0, 0], [1, 0, 0])
        elif direction == "y":
            transform = trimesh.transformations.scale_matrix(-1, [0, 0, 0], [0, 1, 0])
        else:
            raise ValueError(f"Direction {direction} is not defined.")
        # Apply the transformation to the mesh
        mesh.apply_transform(transform)
        tile = super().get_flipped_tile(direction)
        return MeshTile(
            name=tile.name, array=tile.array, mesh=mesh, edges=tile.edges, dimension=self.dimension
        )

    def get_rotated_tile(self, deg):
        if deg not in self.directions.directions:
            raise ValueError(f"Rotation degree {deg} is not defined.")
        transform = trimesh.transformations.rotation_matrix(deg * np.pi / 180, [0, 0, 1])
        mesh = self.mesh.copy()
        mesh = mesh.apply_transform(transform)
        tile = super().get_rotated_tile(deg)
        return MeshTile(
            name=tile.name, array=tile.array, mesh=mesh, edges=tile.edges, dimension=self.dimension
        )

    def get_all_tiles(self, rotations=(), flips=()):
        tiles = [self]
        for rotation in rotations:
            tiles.append(self.get_rotated_tile(rotation))
        for flip_direction in flips:
            tiles.append(self.get_flipped_tile(flip_direction))
            for rotation in rotations:
                tiles.append(self.get_flipped_tile(flip_direction).get_rotated_tile(rotation))
        return tiles

    def get_mesh(self):
        return self.mesh

    def __str__(self):
        return super().__str__()
