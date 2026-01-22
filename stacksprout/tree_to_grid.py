from collections import defaultdict
from sortedcontainers import SortedList

def generate_basic_tree_grid(parent, call_info):
    class Node:
        def __init__(self, row, col):
            self.edges = []
            self.id = None # free
            self.row = row
            self.col = col
        def free(self):
            return self.id == None
        def set_id(self, id):
            self.id = id
        def add_edge(self, to):
            self.edges.append(to)
        def __str__(self):
            return str(self.id)
        def __repr__(self):
            return str(self.id)

    max_depth = 0
    for value in call_info.values():
        max_depth = max(value['depth'], max_depth)
    freq = [0 for _ in range(max_depth+1)]
    for value in call_info.values():
        freq[value['depth']] += 1

    grid = [[Node(r, c) for c in range(max(freq)+1)]
            for r in range(max_depth+1)]
    width = max(freq) + 1
    free_cols = [
        SortedList(range(width))
        for _ in range(max_depth + 1)
    ]
    
    adj = defaultdict(list)
    for node, p in parent.items():
        if p is not None:
            adj[node].append(p)
            adj[p].append(node)

    postorder = []

    visited = [False for _ in range(len(parent)+1)]
    pos = {}
    def place_node(u, parent):
        depth = call_info[u]['depth']
        preferred = 0 if parent is None else pos[parent][1]

        cols = free_cols[depth]

        i = cols.bisect_left(preferred)

        if i == 0:
            c = cols[0]
        elif i == len(cols):
            c = cols[-1]
        else:
            left = cols[i - 1]
            right = cols[i]
            c = left if abs(left - preferred) <= abs(right - preferred) else right

        cols.remove(c)

        grid[depth][c].set_id(u)
        pos[u] = (depth, c)

        if parent is not None:
            grid[depth][c].add_edge(parent)

    def DFS_iterative(root):
        stack = [(root, None, False)]  # (node, parent, processed)

        while stack:
            u, p, processed = stack.pop()

            if not processed:
                visited[u] = True
                place_node(u, p)

                # Postorder marker
                stack.append((u, p, True))

                for v in adj[u]:
                    if not visited[v]:
                        stack.append((v, u, False))
            else:
                postorder.append(u)

    DFS_iterative(1)

    return grid, pos, postorder, adj

def center_tree_grid(grid, parent, pos, postorder):
    children = defaultdict(list)
    for child, p in parent.items():
        if p is not None:
            children[p].append(child)

    max_depth = len(grid) - 1
    width = len(grid[0])

    for row in grid:
        for cell in row:
            cell.id = None
            cell.edges = []

    free_cols = [
        SortedList(range(width))
        for _ in range(max_depth + 1)
    ]

    for u in postorder:
        r, old_c = pos[u]

        cols = [pos[v][1] for v in children.get(u, []) if v in pos]
        target = old_c if not cols else sum(cols) // len(cols)

        cols_free = free_cols[r]
        i = cols_free.bisect_left(target)

        if i == 0:
            c = cols_free[0]
        elif i == len(cols_free):
            c = cols_free[-1]
        else:
            left = cols_free[i - 1]
            right = cols_free[i]
            c = left if abs(left - target) <= abs(right - target) else right

        cols_free.remove(c)
        pos[u] = (r, c)
        grid[r][c].set_id(u)

    for u, (r_u, c_u) in pos.items():
        p = parent.get(u)
        if p is not None:
            grid[r_u][c_u].add_edge(p)
        for ch in children.get(u, []):
            grid[r_u][c_u].add_edge(ch)

    return grid, pos


def generate_tree_grid(parent, call_info, center=True):
    grid, pos, postorder, adj = generate_basic_tree_grid(parent, call_info)
    if center:
        grid, pos = center_tree_grid(grid, parent, pos, postorder)
    return grid, adj, pos

def test_debug(grid):
    for r, row in enumerate(grid):
        print(f"depth {r}:", end=" ")
        for cell in row:
            s = str(cell.id) if cell.id else '.'
            print( s, end=" "*(4-len(s)) )
        print()