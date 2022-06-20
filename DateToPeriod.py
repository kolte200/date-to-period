import json


class Period:
    def __init__(self, name, begin, end, children = None) -> None:
        self.name = name
        self.begin = begin
        self.end = end
        self.parent = None
        self.children = list() if children is None else children


def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)


# Test if a child bring to a node directly or indirectly
def has_indirect_child(node, child):
    for c in node.children:
        if c == child or has_indirect_child(c, child):
            return True
    return False


# Test if a child is a direct child (so, check if a child doesn't have as parent another child)
def is_direct_child(node, child):
    for c in node.children:
        if c != child and has_indirect_child(c, child):
            return False
    return True


def find_indirect_child(node, condition):
    if condition(node): return node
    for child in node.children:
        r = find_indirect_child(child, condition)
        if r is not None: return r
    return None


def load_data(infos_filename, intervals_filename):
    periods_infos_data = read_json_file(infos_filename)
    periods_intervals_data = read_json_file(intervals_filename)

    periods_tree = []
    periods_dict = dict()
    periods_list = []

    for period_info in periods_infos_data:
        id = period_info['id']
        name = period_info['name']
        interval = periods_intervals_data[id]
        begin = -interval['hasBeginning']
        end = -interval['hasEnd']
        period = Period(name, begin, end)
        periods_list.append(period)
        periods_dict[id] = period

    for period_info in periods_infos_data:
        period = periods_dict[period_info['id']]
        for child_id in period_info['narrow']:
            child = periods_dict[child_id]
            if child.parent is not None:
                if is_direct_child(period, child):
                    child.parent.children.remove(child)
                    period.children.append(child)
                    child.parent = period
            else:
                period.children.append(child)
                child.parent = period

    for period in periods_list:
        if period.parent is None:
            periods_tree.append(period)

    return periods_tree


def date_to_periods(periods_tree, date):
    periods = []

    while len(periods_tree) > 0:
        for child in periods_tree:
            if child.begin <= date <= child.end:
                periods.append(child)
                periods_tree = child.children
                break
        else:
            print("Can't find period for date %.2f" % date)
            return periods

    return periods


periods_tree = load_data("data/periods_infos.json", "data/periods_intervals.json")
print(list(map(lambda x: x.name, date_to_periods(periods_tree, -140))))
