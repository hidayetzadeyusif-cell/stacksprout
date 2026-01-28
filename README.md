# StackSprout

![StackSprout demo](https://raw.githubusercontent.com/hidayetzadeyusif-cell/stacksprout/main/assets/stacksprout-example.gif)

**StackSprout** is a Python library for visualizing the execution of recursive functions as interactive call trees, with optional timeline-based animation.

It helps you *see* how recursion grows, branches, and unwinds — making it useful for learning, debugging, and exploration.

Unlike debuggers or profilers, StackSprout records execution first and visualizes it afterward, enabling deterministic playback and timeline control.

Perfect for students, educators, and developers who want to understand why recursive code behaves the way it does.

---

## Why Use StackSprout?

StackSprout makes recursion *visible*. Unlike debuggers that show the state at a single point in time, or profilers that focus on performance metrics, StackSprout lets you step through the entire call lifecycle of recursive functions. This makes it an invaluable tool for learning, teaching, and debugging recursive algorithms.

---

## Features

- Visualize recursive calls as an interactive, clean tree layout
- Static and animated execution modes
- Timeline scrubbing, stepping, and playback controls
- Interactive canvas with pan, zoom, and click-to-inspect nodes
- Synchronized tree and hierarchy views
- Works with any recursive Python function

---

## Installation
Install from PyPI:
```bash
pip install stacksprout
```

Or install from source:
```bash
pip install .
```

## Quick Example
```python
from stacksprout import trace, visualize_tree

@trace
def fib(n):
    if n <= 1:
        return 1
    return fib(n - 1) + fib(n - 2)

fib(6)
visualize_tree(fib)
```

This opens an interactive window where you can scrub, step through, and replay the recursive call tree for `fib(6)`.

---

## Design Overview

StackSprout operates in two phases:

1. **Tracing phase**  
   A decorator (`@trace`) records function entry, exit, and timing information during execution.
2. **Visualization phase**  
   After execution, the recorded data is turned into a visual call tree, which can be explored statically or animated over time.

This design ensures deterministic, debuggable visualizations without interfering with runtime behavior.

---

## Usage Notes
- The decorated function **must** be executed before calling `visualize_tree()`.
- If no trace data exists, StackSprout displays a helpful message and exits cleanly.
- Mutual recursion and multi-root call trees are not supported in v1.

---

## Examples

Additional examples can be found in the `examples/` directory:
- Fibonacci
- Factorial
- Custom recursive functions

---

## Requirements

- Python 3.10 or newer
- `tkinter` (included with most Python installations; Linux users may need `python3-tk`)

---

## License

This project is licensed under the **MIT License**. See the license on [GitHub](https://github.com/hidayetzadeyusif-cell/stacksprout/blob/main/LICENSE).

---

## About

Built as an educational and exploratory tool for understanding recursion and call stacks. Feedback is welcome.
