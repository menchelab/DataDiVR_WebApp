import networkx as nx
import copy
import math
import matplotlib.pyplot as plt
import nx2json as nx2j

# ==========================================
# 1. SETUP COLORS & BASE STRUCTURE
# ==========================================
rgba_white = (255, 255, 255, 100)
rgba_black = (0, 0, 0, 100)
rgba_blue = (0, 119, 255, 100)
rgba_red = (255, 50, 50, 100)
rgba_green = (0, 255, 0, 100)
rgba_yellow = (255, 255, 0, 100)  # Start Node Highlight
rgba_transparent = (0, 0, 0, 0)  # Invisible boundary anchors

G_base = nx.Graph()

# -----------------------------------
# SCALE ANCHORS (Invisible Bounding Box)
# -----------------------------------
bnd_nodes = ["BND_TOP", "BND_BOTTOM"]
G_base.add_nodes_from(bnd_nodes)

# -----------------------------------
# LEFT SIDE: Königsberg Landmasses
# -----------------------------------
k_land_nodes = ["A", "B", "C", "D"]
G_base.add_nodes_from(k_land_nodes)

# -----------------------------------
# RIGHT SIDE: House of Nikolaus
# -----------------------------------
n_nodes = ["N1", "N2", "N3", "N4", "N5"]
G_base.add_nodes_from(n_nodes)

n_edges_base = [
    ("N1", "N2"),
    ("N1", "N3"),
    ("N1", "N4"),
    ("N2", "N3"),
    ("N2", "N4"),
    ("N3", "N4"),
    ("N3", "N5"),
    ("N4", "N5"),
]

# ==========================================
# POSITIONS & ADJUSTED CURVES
# ==========================================
pos_2d = {
    # Scaling Boundary Anchors (Adjust Y values here to change viewport scale)
    "BND_TOP": [1.075, 0.60, 0.0],
    "BND_BOTTOM": [1.075, -0.60, 0.0],
    # KÖNIGSBERG
    "C": [-0.25, 0.0, 0.0],  # Island
    "D": [0.55, 0.0, 0.0],  # East
    "A": [-0.25, 0.25, 0.0],  # North
    "B": [-0.25, -0.25, 0.0],  # South
    # NIKOLAUS
    "N1": [1.40, 0.25, 0.0],
    "N2": [2, 0.25, 0.0],
    "N3": [1.40, -0.075, 0.0],
    "N4": [2, -0.075, 0.0],
    "N5": [1.7, -0.25, 0.0],
}


def generate_bezier(p0, p1, p2, num_points):
    points = []
    for i in range(1, num_points + 1):
        t = i / (num_points + 1)
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
        z = (1 - t) ** 2 * p0[2] + 2 * (1 - t) * t * p1[2] + t**2 * p2[2]
        points.append([x, y, z])
    return points


k_bridge_defs = [
    ("A", "C", "Bridge_AC1", [-0.5, 0.125, 0.0]),
    ("A", "C", "Bridge_AC2", [0, 0.125, 0.0]),
    ("B", "C", "Bridge_BC1", [-0.5, -0.125, 0.0]),
    ("B", "C", "Bridge_BC2", [0, -0.125, 0.0]),
    ("A", "D", "Bridge_AD1", [0.25, 0.25, 0.0]),
    ("B", "D", "Bridge_BD1", [0.25, -0.25, 0.0]),
    ("C", "D", "Bridge_CD1", [0.25, 0.0, 0.0]),
]

NUM_DUMMIES = 20

k_bridge_dummies = {}
k_bridge_nodes = []

for u, v, b_name, ctrl in k_bridge_defs:
    p0 = pos_2d[u]
    p2 = pos_2d[v]
    curve_points = generate_bezier(p0, ctrl, p2, NUM_DUMMIES)

    dummies = []
    curr = u
    for i in range(NUM_DUMMIES):
        d_name = f"{b_name}_{i + 1}"
        G_base.add_node(d_name)
        pos_2d[d_name] = curve_points[i]
        dummies.append(d_name)
        k_bridge_nodes.append(d_name)

        G_base.add_edge(curr, d_name)
        curr = d_name

    G_base.add_edge(curr, v)
    k_bridge_dummies[(u, v, b_name)] = dummies
    k_bridge_dummies[(v, u, b_name)] = list(reversed(dummies))

n_edge_dummies = {}
n_dummy_nodes = []

for u, v in n_edges_base:
    p0 = pos_2d[u]
    p3 = pos_2d[v]

    dummies = []
    curr = u
    for i in range(NUM_DUMMIES):
        d_name = f"N_dummy_{u}_{v}_{i + 1}"
        G_base.add_node(d_name)

        t = (i + 1) / (NUM_DUMMIES + 1)
        px = p0[0] + (p3[0] - p0[0]) * t
        py = p0[1] + (p3[1] - p0[1]) * t
        pz = p0[2] + (p3[2] - p0[2]) * t
        pos_2d[d_name] = [px, py, pz]

        dummies.append(d_name)
        n_dummy_nodes.append(d_name)

        G_base.add_edge(curr, d_name)
        curr = d_name

    G_base.add_edge(curr, v)
    n_edge_dummies[(u, v)] = dummies
    n_edge_dummies[(v, u)] = list(reversed(dummies))

nx.set_node_attributes(G_base, pos_2d, name="pos")

node_colors = {}
node_labels = {}
for n in G_base.nodes():
    if n in bnd_nodes:
        node_colors[n] = rgba_transparent
        node_labels[n] = ""
    elif n in k_bridge_nodes or n in n_dummy_nodes:
        node_colors[n] = rgba_black
        node_labels[n] = ""
    else:
        node_colors[n] = rgba_white
        node_labels[n] = n

nx.set_node_attributes(G_base, node_colors, name="nodecolor")
nx.set_node_attributes(G_base, node_labels, name="label")


# ==========================================
# 2. SCENE GENERATOR
# ==========================================
def create_scene(
    layout_name,
    k_nodes,
    k_edges,
    k_failed,
    k_start,
    n_nodes_list,
    n_edges_list,
    n_success,
    n_start,
):
    G = copy.deepcopy(G_base)
    G.graph["layoutname"] = layout_name

    edge_colors = {e: rgba_white for e in G.edges()}
    n_colors = nx.get_node_attributes(G, "nodecolor")

    k_color = rgba_red if k_failed else rgba_blue
    n_color = rgba_green if n_success else rgba_blue

    for n in k_nodes:
        n_colors[n] = k_color
    for n in n_nodes_list:
        n_colors[n] = n_color

    for u, v in k_edges:
        if (u, v) in edge_colors:
            edge_colors[(u, v)] = k_color
        elif (v, u) in edge_colors:
            edge_colors[(v, u)] = k_color

    for u, v in n_edges_list:
        if (u, v) in edge_colors:
            edge_colors[(u, v)] = n_color
        elif (v, u) in edge_colors:
            edge_colors[(v, u)] = n_color

    if k_start:
        n_colors[k_start] = rgba_yellow
    if n_start:
        n_colors[n_start] = rgba_yellow

    nx.set_node_attributes(G, n_colors, name="nodecolor")
    nx.set_edge_attributes(G, edge_colors, name="linkcolor")
    return G


def get_micro_chunks(u, v, dummies):
    all_nodes = dummies + [v]
    all_edges = []
    curr = u
    for nxt in all_nodes:
        all_edges.append((curr, nxt))
        curr = nxt

    chunk_size = len(all_nodes) // 3
    chunks = []
    idx = 0
    for i in range(3):
        if i == 2:
            chunks.append((all_nodes[idx:], all_edges[idx:]))
        else:
            chunks.append(
                (all_nodes[idx : idx + chunk_size], all_edges[idx : idx + chunk_size])
            )
            idx += chunk_size
    return chunks


# ==========================================
# 3. GENERATE THE SEQUENCES
# ==========================================
k_walks = [
    (
        "C",
        [
            ("Bridge_AC1", "A"),
            ("Bridge_AD1", "D"),
            ("Bridge_BD1", "B"),
            ("Bridge_BC1", "C"),
            ("Bridge_AC2", "A"),
        ],
    ),
    (
        "A",
        [
            ("Bridge_AD1", "D"),
            ("Bridge_CD1", "C"),
            ("Bridge_BC1", "B"),
            ("Bridge_BD1", "D"),
        ],
    ),
    (
        "B",
        [
            ("Bridge_BC1", "C"),
            ("Bridge_AC1", "A"),
            ("Bridge_AD1", "D"),
            ("Bridge_CD1", "C"),
            ("Bridge_BC2", "B"),
            ("Bridge_BD1", "D"),
        ],
    ),
    (
        "D",
        [
            ("Bridge_AD1", "A"),
            ("Bridge_AC1", "C"),
            ("Bridge_BC1", "B"),
            ("Bridge_BD1", "D"),
            ("Bridge_CD1", "C"),
            ("Bridge_AC2", "A"),
        ],
    ),
    (
        "C",
        [
            ("Bridge_CD1", "D"),
            ("Bridge_BD1", "B"),
            ("Bridge_BC1", "C"),
            ("Bridge_AC1", "A"),
            ("Bridge_AC2", "C"),
            ("Bridge_BC2", "B"),
        ],
    ),
]

n_walks = [
    ("N1", ["N2", "N4", "N3", "N1", "N4", "N5", "N3", "N2"]),
    ("N2", ["N1", "N3", "N4", "N2", "N3", "N5", "N4", "N1"]),
    ("N1", ["N4", "N2", "N1", "N3", "N4", "N5", "N3", "N2"]),
    ("N2", ["N3", "N1", "N2", "N4", "N3", "N5", "N4", "N1"]),
    ("N1", ["N3", "N5", "N4", "N3", "N2", "N4", "N1", "N2"]),
]

scenes = []
scene_counter = 1

for walk_idx in range(5):
    k_start, k_steps = k_walks[walk_idx]
    n_start, n_steps = n_walks[walk_idx]

    # 1. Generate 2 White Overview Frames
    for _ in range(2):
        scenes.append(
            create_scene(
                f"{scene_counter:03d}-OVERVIEW",
                [],
                [],
                False,
                None,
                [],
                [],
                False,
                None,
            )
        )
        scene_counter += 1

    k_colored_nodes = []
    k_colored_edges = []
    n_colored_nodes = []
    n_colored_edges = []

    # 2. Generate 1 Yellow Start Frame
    scenes.append(
        create_scene(
            f"{scene_counter:03d}-WALK{walk_idx + 1}-START",
            k_colored_nodes,
            k_colored_edges,
            False,
            k_start,
            n_colored_nodes,
            n_colored_edges,
            False,
            n_start,
        )
    )
    scene_counter += 1

    # 3. Micro-Step Walking
    curr_k = k_start
    curr_n = n_start
    max_steps = max(len(k_steps), len(n_steps))

    for step_idx in range(max_steps):
        k_chunks = []
        if step_idx < len(k_steps):
            b_name, next_k = k_steps[step_idx]
            dummies = k_bridge_dummies[(curr_k, next_k, b_name)]
            k_chunks = get_micro_chunks(curr_k, next_k, dummies)
            curr_k = next_k

        n_chunks = []
        if step_idx < len(n_steps):
            next_n = n_steps[step_idx]
            dummies = n_edge_dummies[(curr_n, next_n)]
            n_chunks = get_micro_chunks(curr_n, next_n, dummies)
            curr_n = next_n

        for m in range(3):
            if k_chunks:
                k_colored_nodes.extend(k_chunks[m][0])
                k_colored_edges.extend(k_chunks[m][1])
            if n_chunks:
                n_colored_nodes.extend(n_chunks[m][0])
                n_colored_edges.extend(n_chunks[m][1])

            k_failed = step_idx >= len(k_steps)
            n_success = (step_idx >= len(n_steps)) or (
                step_idx == len(n_steps) - 1 and m == 2
            )

            scenes.append(
                create_scene(
                    f"{scene_counter:03d}-WALK{walk_idx + 1}-STEP{step_idx + 1}-{m + 1}",
                    k_colored_nodes,
                    k_colored_edges,
                    k_failed,
                    k_start,
                    n_colored_nodes,
                    n_colored_edges,
                    n_success,
                    n_start,
                )
            )
            scene_counter += 1

    # 4. Generate 2 Final Red/Green Outcome Frames
    for _ in range(2):
        scenes.append(
            create_scene(
                f"{scene_counter:03d}-WALK{walk_idx + 1}-END",
                k_colored_nodes,
                k_colored_edges,
                True,
                k_start,
                n_colored_nodes,
                n_colored_edges,
                True,
                n_start,
            )
        )
        scene_counter += 1

for g in scenes:
    g.graph["projectname"] = "Koenigsberg_vs_Nikolaus_Walking"
    g.graph["info"] = "Comparing paths with micro-step walking."

try:
    nx2j.create_project(scenes)
except Exception as e:
    print(f"Skipping JSON export: {e}")

# ==========================================
# 4. MATPLOTLIB PREVIEW
# ==========================================
print(f"Generating Matplotlib preview for {len(scenes)} scenes...")
cols = 6
rows = math.ceil(len(scenes) / cols)

fig = plt.figure(figsize=(4 * cols, 4 * rows))
fig.patch.set_facecolor("black")

for i, g in enumerate(scenes):
    ax = plt.subplot(rows, cols, i + 1)
    ax.set_facecolor("black")

    pos_3d = nx.get_node_attributes(g, "pos")
    pos_2d_plot = {node: (coords[0], coords[1]) for node, coords in pos_3d.items()}

    raw_n_colors = nx.get_node_attributes(g, "nodecolor")
    plot_n_colors = []
    plot_n_sizes = []

    for node in g.nodes():
        r, g_val, b, a = raw_n_colors[node]
        # Fixed: Now accurately passes dynamic alpha mapping (a / 100) to keep boundaries invisible
        plot_n_colors.append((r / 255, g_val / 255, b / 255, a / 100))

        if str(node) in bnd_nodes:
            plot_n_sizes.append(0)  # Boundary nodes have 0 visible volume
        elif "Bridge" in str(node) or "N_dummy" in str(node):
            plot_n_sizes.append(15)
        else:
            plot_n_sizes.append(150)

    raw_e_colors = nx.get_edge_attributes(g, "linkcolor")
    plot_e_colors = []
    for u, v in g.edges():
        color = raw_e_colors.get((u, v), raw_e_colors.get((v, u), rgba_white))
        plot_e_colors.append((color[0] / 255, color[1] / 255, color[2] / 255, 1.0))

    labels = nx.get_node_attributes(g, "label")

    nx.draw(
        g,
        pos=pos_2d_plot,
        node_color=plot_n_colors,
        edge_color=plot_e_colors,
        labels=labels,
        with_labels=True,
        node_size=plot_n_sizes,
        font_size=6,
        font_color="white",
        edgecolors="grey",
        width=2.5,
        ax=ax,
    )

    ax.set_title(g.graph["layoutname"], color="white", fontsize=6)

plt.tight_layout()
plt.savefig("koenigsberg_vs_nikolaus_walking_preview.pdf")
