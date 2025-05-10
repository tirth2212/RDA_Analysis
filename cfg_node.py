from typing import List
import ast

class CFGNode:
    def __init__(self, id: int, code: str):
        self.id = id
        self.code = code
        self.defs = set()
        self.uses = set()
        self.outgoing: List[int] = []

        # For dataflow analysis
        self.gen = set()
        self.kill = set()
        self.in_set = set()
        self.out_set = set()

        # For graph traversal
        self.predecessors: List['CFGNode'] = []
        self.successors: List['CFGNode'] = []

        # For break/continue resolution
        self.break_stmt = False
        self.continue_stmt = False

        # For return resolution
        self.return_stmt = False

        # For function call/return flow
        self.call_target = None
        self.return_to: 'CFGNode' = None


class CFG:
    def __init__(self):
        self.nodes: List[CFGNode] = []
        self.node_counter = 0
        self.function_entries = {}  # Map function name to entry node
        self.function_returns = {}  # Map function name to list of return nodes

    def add_node(self, code: str) -> CFGNode:
        node = CFGNode(self.node_counter, code)
        self.nodes.append(node)
        self.node_counter += 1
        return node

    def add_edge(self, from_node: CFGNode, to_node: CFGNode):
        from_node.successors.append(to_node)
        to_node.predecessors.append(from_node)

    def build_from_ast(self, tree: ast.AST):
        loop_stack = []

        def handle_stmt(stmt, prev_nodes):
            if isinstance(stmt, ast.FunctionDef):
                entry_node = self.add_node(f"def {stmt.name}():")
                self.function_entries[stmt.name] = entry_node
                self.function_returns[stmt.name] = []
                for p in prev_nodes:
                    self.add_edge(p, entry_node)
                func_exits = []
                for s in stmt.body:
                    func_exits = handle_stmt(s, [entry_node])
                return prev_nodes

            elif isinstance(stmt, ast.Return):
                return_node = self.add_node(f"return {ast.unparse(stmt.value).strip()}")
                return_node.return_stmt = True
                for p in prev_nodes:
                    self.add_edge(p, return_node)
                for fname, entry in self.function_entries.items():
                    if entry in return_node.predecessors:
                        self.function_returns[fname].append(return_node)
                        break
                return []

            elif isinstance(stmt, ast.If):
                cond_code = ast.unparse(stmt.test).strip()
                cond_node = self.add_node(f"if {cond_code}:")
                for p in prev_nodes:
                    self.add_edge(p, cond_node)

                then_exits = []
                for s in stmt.body:
                    then_exits = handle_stmt(s, [cond_node])

                else_exits = []
                if stmt.orelse:
                    else_node = self.add_node("else:")
                    self.add_edge(cond_node, else_node)
                    for s in stmt.orelse:
                        else_exits = handle_stmt(s, [else_node])
                else:
                    else_exits = [cond_node]

                return then_exits + else_exits

            elif isinstance(stmt, ast.While):
                cond_code = ast.unparse(stmt.test).strip()
                cond_node = self.add_node(f"while {cond_code}")
                for p in prev_nodes:
                    self.add_edge(p, cond_node)

                body_exits = []
                for s in stmt.body:
                    body_exits = handle_stmt(s, [cond_node])
                for b in body_exits:
                    self.add_edge(b, cond_node)
                return [cond_node]

            elif isinstance(stmt, ast.For):
                target_code = ast.unparse(stmt.target).strip()
                iter_code = ast.unparse(stmt.iter).strip()
                loop_header = self.add_node(f"for {target_code} in {iter_code}")
                for p in prev_nodes:
                    self.add_edge(p, loop_header)

                body_exits = []
                for s in stmt.body:
                    body_exits = handle_stmt(s, [loop_header])
                for b in body_exits:
                    self.add_edge(b, loop_header)
                return [loop_header]

            elif isinstance(stmt, ast.Break):
                node = self.add_node("break")
                node.break_stmt = True
                for p in prev_nodes:
                    self.add_edge(p, node)
                return []

            elif isinstance(stmt, ast.Continue):
                node = self.add_node("continue")
                node.continue_stmt = True
                for p in prev_nodes:
                    self.add_edge(p, node)
                if loop_stack:
                    self.add_edge(node, loop_stack[-1])
                return []

            elif isinstance(stmt, ast.Pass):
                node = self.add_node("pass")
                for p in prev_nodes:
                    self.add_edge(p, node)
                return [node]

            elif isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                func_name = stmt.value.func.id
                call_node = self.add_node(ast.unparse(stmt).strip())
                call_node.call_target = func_name
                for p in prev_nodes:
                    self.add_edge(p, call_node)

                # NEW: Add defs and uses for assignment
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        call_node.defs.add(target.id)
                for n in ast.walk(stmt.value):
                    if isinstance(n, ast.Name):
                        call_node.uses.add(n.id)

                if func_name in self.function_entries:
                    self.add_edge(call_node, self.function_entries[func_name])
                    for ret_node in self.function_returns[func_name]:
                        self.add_edge(ret_node, call_node)
                        ret_node.return_to = call_node
                return [call_node]


            else:
                code_str = ast.unparse(stmt).strip()
                node = self.add_node(code_str)
                for p in prev_nodes:
                    self.add_edge(p, node)

                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            node.defs.add(target.id)
                    for n in ast.walk(stmt.value):
                        if isinstance(n, ast.Name):
                            node.uses.add(n.id)
                elif isinstance(stmt, ast.AugAssign):
                    if isinstance(stmt.target, ast.Name):
                        node.defs.add(stmt.target.id)
                        node.uses.add(stmt.target.id)
                    for n in ast.walk(stmt.value):
                        if isinstance(n, ast.Name):
                            node.uses.add(n.id)
                elif isinstance(stmt, ast.Expr):
                    for n in ast.walk(stmt):
                        if isinstance(n, ast.Name):
                            node.uses.add(n.id)
                return [node]

        entry_nodes = []
        for stmt in tree.body:
            entry_nodes = handle_stmt(stmt, entry_nodes)
