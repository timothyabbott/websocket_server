#
#
#
# def matches_value(data, pattern, value_to_match):
#     """
#     Check if the value at the end of the path matches value_to_match
#     """
#     if isinstance(pattern, str):
#         # this is our value, no need to go deeper.
#         return isinstance(data, dict) and pattern in data and data[pattern] == value_to_match
#
#     if not isinstance(data, dict) or not isinstance(pattern, dict):
#         return False
#
#     for key, subpattern in pattern.items():
#         if key not in data:
#             return False
#         if not matches_value(data[key], subpattern, value_to_match):
#             return False
#     return True

def matches_subset(sub_set_dict:dict, data_dict:dict):

    if type(sub_set_dict) != type(data_dict):
        return False

    if isinstance(sub_set_dict, dict):
        return all(
            # go through all keys in sub_set_dict and check if they are in data_dict
            key in data_dict and matches_subset(sub_set_dict[key], data_dict[key])
            for key in sub_set_dict
        )
    # do we want/need to handle lists? this code checks the lists are equal.
    if isinstance(sub_set_dict, list):
        return len(sub_set_dict) == len(data_dict) and all(
            matches_subset(sub_set, full_data) for sub_set, full_data in zip(sub_set_dict, data_dict)
        )

    return sub_set_dict == data_dict
# inspiration from https://realpython.com/structural-pattern-matching/#what-is-pattern-matching
