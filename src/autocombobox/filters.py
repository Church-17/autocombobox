def default_filter(options: tuple[str], text: str) -> list[int]:
    indices = []
    index = 0
    for opt in options:
        if opt.lower().startswith(text.lower()):
            indices.append(index)
            index += 1
        else:
            indices.append(-1)
    return indices
