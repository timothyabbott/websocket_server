def create_pattern_matcher(*path):
    """
    Creates a pattern where the last item in the path is the value to match against.
    """
    if len(path) < 1:
        raise ValueError("Need at least one key in path")

    *keys, value_key = path
    pattern = value_key  # Last item is the key we'll match value against
    for key in reversed(keys):
        pattern = {key: pattern}
    return pattern


def matches_value(data, pattern, value_to_match):
    """
    Check if the value at the end of the path matches value_to_match
    """
    if isinstance(pattern, str):
        # this is our value, no need to go deeper.
        return isinstance(data, dict) and pattern in data and data[pattern] == value_to_match

    if not isinstance(data, dict) or not isinstance(pattern, dict):
        return False

    for key, subpattern in pattern.items():
        if key not in data:
            return False
        if not matches_value(data[key], subpattern, value_to_match):
            return False
    return True

# inspiration from https://realpython.com/structural-pattern-matching/#what-is-pattern-matching
