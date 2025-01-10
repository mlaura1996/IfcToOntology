import ifcopenshell
import OCC.Core.TopoDS 
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge


def get_topods_shape(element):
    """
    Gets the TopoDS_Shape of an IFC element using ifcopenshell.geom.

    Parameters:
    - element: The IFC element.

    Returns:
    - TopoDS_Shape object or None if shape extraction fails.
    """
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True) #generalinfo
    product = ifcopenshell.geom.create_shape(settings, element)
    shape = OCC.Core.TopoDS.TopoDS_Iterator(product.geometry).Value()
    return shape 

def are_shapes_touching(shape1, shape2):
    """
    Check if two TopoDS_Shapes are touching.
    :param shape1: First shape
    :param shape2: Second shape
    :return: True if the shapes are touching, False otherwise
    """
    extrema = BRepExtrema_DistShapeShape(shape1, shape2)
    extrema.Perform()
    if not extrema.IsDone():
        raise RuntimeError("Distance computation failed.")
    min_distance = extrema.Value()
    return min_distance == 0.0

def group_touching_shapes(shapes):
    """
    Group touching TopoDS_Shapes into clusters.
    :param shapes: List of TopoDS_Shapes
    :return: List of clusters, where each cluster is a list of touching shapes
    """
    visited = set()
    groups = []

    def dfs(shape, group):
        """Depth-first search to find all connected shapes."""
        for i, other_shape in enumerate(shapes):
            if i not in visited and are_shapes_touching(shape, other_shape):
                visited.add(i)
                group.append(other_shape)
                dfs(other_shape, group)

    for i, shape in enumerate(shapes):
        if i not in visited:
            visited.add(i)
            group = [shape]
            dfs(shape, group)
            groups.append(group)

    return groups