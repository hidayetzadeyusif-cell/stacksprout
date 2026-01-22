class LayoutEngine:
    def __init__(self, tree_grid, diameter, cell_offset):
        self.tree_grid = tree_grid
        self.diameter = diameter
        self.cell_offset = cell_offset

        self.offset_x = 0
        self.offset_y = 0

    def compute_centering(self, canvas_width, canvas_height):
        grid_width = (
            (len(self.tree_grid[0]) - 1) * (self.diameter + self.cell_offset)
            + self.diameter
        )
        grid_height = (
            (len(self.tree_grid) - 1) * (self.diameter + self.cell_offset)
            + self.diameter
        )

        self.offset_x = (canvas_width - grid_width) / 2
        self.offset_y = (canvas_height - grid_height) / 2

    def node_center(self, row, col):
        x = (
            col * (self.diameter + self.cell_offset)
            + self.diameter / 2
            + self.offset_x
        )
        y = (
            row * (self.diameter + self.cell_offset)
            + self.diameter / 2
            + self.offset_y
        )
        return x, y
    
    def edge_endpoints(self, row1, col1, row2, col2):
        x1, y1 = self.node_center(row1, col1)
        x2, y2 = self.node_center(row2, col2)
        return x1, y1, x2, y2