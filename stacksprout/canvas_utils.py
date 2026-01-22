def create_circle(canvas, cx, cy, r, **kwargs):
    return canvas.create_oval(
        cx - r, cy - r,
        cx + r, cy + r,
        **kwargs
    )
def label_vertical_offset(font):
    """
    Distance from node center to second label,
    derived from the current medium font size.
    """
    return font.metrics("linespace") // 2
def trim_text_to_width(text, font, max_width):
    ellipsis = "..."

    if font.measure(ellipsis) > max_width:
        return ""

    if font.measure(text) <= max_width:
        return text

    left, right = 0, len(text)

    while left < right:
        mid = (left + right) // 2
        candidate = text[:mid] + ellipsis

        if font.measure(candidate) <= max_width:
            left = mid + 1
        else:
            right = mid

    return text[:max(0, left - 1)] + ellipsis
def get_node_circle(canvas, node_tag):
    for item in canvas.find_withtag(node_tag):
        if canvas.type(item) == "oval":
            return item
    return None