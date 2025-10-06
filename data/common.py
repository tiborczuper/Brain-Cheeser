"""Közös konstansok és utility függvények mindkét játékmódhoz."""

# ================== KÖZÖS EDGE INDEX MAP ==================

EDGE_INDEX_MAP = {
    1: ((1,1),(1,2)), 2: ((1,2),(1,3)), 3: ((1,3),(1,4)),
    4: ((1,1),(2,1)), 5: ((1,2),(2,2)), 6: ((1,3),(2,3)), 7: ((1,4),(2,4)),
    8: ((2,1),(2,2)), 9: ((2,2),(2,3)), 10: ((2,3),(2,4)),
    11: ((2,1),(3,1)), 12: ((2,2),(3,2)), 13: ((2,3),(3,3)), 14: ((2,4),(3,4)),
    15: ((3,1),(3,2)), 16: ((3,2),(3,3)), 17: ((3,3),(3,4)),
    18: ((3,1),(4,1)), 19: ((3,2),(4,2)), 20: ((3,3),(4,3)), 21: ((3,4),(4,4)),
    22: ((4,1),(4,2)), 23: ((4,2),(4,3)), 24: ((4,3),(4,4)),
}

def edge_index_to_cells(idx: int):
    """Edge index-ből cella koordinátákat ad vissza."""
    return EDGE_INDEX_MAP.get(idx, None)

def create_mice_from_edges(edge_indices):
    """Edge index lista alapján létrehozza az egerek pozícióit."""
    mice = []
    for edge in edge_indices:
        try:
            cells = edge_index_to_cells(edge)
            if cells:
                mice.append(cells)
        except Exception as err:
            print(f'[MOUSE EDGE ERROR] {err}')
    return mice