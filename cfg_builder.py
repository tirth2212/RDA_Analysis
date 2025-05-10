import ast
from cfg_node import CFGNode, CFG


def build_cfg_from_code(code: str, language: str = "Python") -> CFG:
    if language.lower() != "python":
        raise NotImplementedError("Only Python is supported.")
    tree = ast.parse(code)
    cfg = CFG()
    cfg.build_from_ast(tree)
    return cfg



def finalize_gen_kill(cfg):
    # Collect all variable definitions globally
    all_defs = {}
    for node in cfg.nodes:
        for var in node.defs:
            if var not in all_defs:
                all_defs[var] = set()
            all_defs[var].add((var, node.id))

    for node in cfg.nodes:
        # GEN: assign (var, node_id) for all variables defined in this node
        node.gen = {(var, node.id) for var in node.defs}

        # KILL: all (var, other_node) pairs where var is redefined elsewhere
        kill_set = set()
        for var in node.defs:
            kill_set |= {pair for pair in all_defs.get(var, set()) if pair[1] != node.id}
        node.kill = {var for var, _ in kill_set}

