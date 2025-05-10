# This module will implement core dataflow logic (reaching definitions).

def compute_reaching_definitions(cfg):
    worklist = list(cfg.nodes)

    # Initialize GEN and KILL if not already
    for node in cfg.nodes:
        if not node.gen:
            for var in node.defs:
                node.gen.add((var, node.id))
            for var in node.defs:
                node.kill.add(var)

    changed = True
    while changed:
        changed = False
        for node in worklist:
            in_set = set()
            for pred in node.predecessors:
                in_set |= pred.out_set

            old_out = node.out_set.copy()
            node.in_set = in_set
            node.out_set = node.gen | {d for d in in_set if d[0] not in node.kill}

            # 🔁 Propagate return edges back to call site
            if node.return_stmt and node.return_to:
                node.return_to.out_set |= node.out_set

            if old_out != node.out_set:
                changed = True
