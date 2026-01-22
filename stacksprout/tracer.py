from functools import wraps

def trace(func):
    call_id = 0
    timer = 0
    depth = 0
    stack = []
    parent = {}
    call_info = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal call_id, timer, depth

        if not stack:
            call_id = 0
            timer = 0
            parent.clear()
            call_info.clear()

        call_id += 1
        my_id = call_id

        if stack:
            parent[my_id] = stack[-1]
        else:
            parent[my_id] = None

        timer += 1
        depth += 1
        call_info[my_id] = {
            "name": func.__name__,
            "args": args, 
            "in_time": timer,
            "out_time": None,
            "self_id": my_id,
            "depth": depth,
            "result": None
        }

        stack.append(my_id)
        try:
            res = func(*args, **kwargs)
            call_info[my_id]["result"] = res
            return res
        finally:
            timer += 1
            depth -= 1
            call_info[my_id]["out_time"] = timer
            stack.pop()
            
    wrapper.parent = parent
    wrapper.call_info = call_info
    return wrapper