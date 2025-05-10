import matplotlib.pyplot as plt
import networkx as nx

def plot_cfg(cfg, filename="cfg.png"):
    G = nx.DiGraph()

    # Add nodes with labels
    for node in cfg.nodes:
        label = f"{node.id}: {node.code.strip()}"
        G.add_node(node.id, label=label)

    # Add edges based on successors
    for node in cfg.nodes:
        for succ in node.successors:
            G.add_edge(node.id, succ.id)

    pos = nx.spring_layout(G, seed=42)
    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=2500,
            node_color="lightblue", font_size=10, font_weight='bold', arrows=True)
    plt.title("Control Flow Graph")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
