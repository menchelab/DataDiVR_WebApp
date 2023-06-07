import json
import os
from multiprocessing import Pool

import numpy as np
import pandas as pd
from project import Project, COLOR, NODE, LINK
import swifter
from PIL import Image

SELECTED = (
    255,
    0,
    0,
    255,
)
NOT_SELECTED = (
    255,
    255,
    255,
    10,
)


def selected_color(x):
    if isinstance(x, float):
        return int(0)
    return (SELECTED[:3] + (x[-1],),)
    # return SELECTED


def not_selected_color(x):
    if isinstance(x, float):
        return int(0)
    # return x[:3] + (10,)
    return (NOT_SELECTED[:3] + (x[-1],),)


def handle_node_layout(selected_nodes, project, out, layout, node_color):
    nodes = extract_node_data_from_tex(project, layout)

    selected_nodes = nodes.index.isin(selected_nodes)
    not_selected = nodes[~selected_nodes].copy()
    selected = nodes[selected_nodes].copy()

    if node_color:
        selected["c"] = (
            selected["c"]
            .swifter.progress_bar(False)
            .apply(lambda x: node_color + (x[3],))
        )
    else:
        if selected["c"].unique().size == 1:
            selected["c"] = (
                selected["c"].swifter.progress_bar(False).apply(selected_color)
            )

    not_selected["c"] = (
        not_selected["c"].swifter.progress_bar(False).apply(not_selected_color)
    )
    nodes = pd.concat([selected, not_selected])
    nodes = nodes.sort_index()
    nodes = nodes.reindex(range(len(nodes)))
    nodes["c"] = nodes["c"].apply(lambda x: 0 if isinstance(x, float) else x)

    out = os.path.join(out.layouts_rgb_dir, layout)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img = Image.new("RGBA", (128, 128))
    img.putdata(nodes["c"])

    img.save(out)
    return


def highlight_nodes(selected, layouts, project, out, node_color):
    project.read_nodes()
    project.nodes_df = pd.DataFrame(project.nodes["nodes"])

    args = [(selected, project, out, layout, node_color) for layout in layouts]
    n = len(layouts)
    p = n
    if n > os.cpu_count():
        p = os.cpu_count()
    with Pool(p) as pool:
        pool.starmap(handle_node_layout, args)
    return


def handle_link_layout(
    selected_nodes,
    selected_links,
    project,
    out,
    mode,
    layout,
    link_color,
):
    # log.debug("Handling layout", layout)
    links, img_size = extract_link_data_from_tex(project, layout)
    if selected_links is not None:
        consider = links.index.isin(selected_links)
        consider = links[consider].copy()
    else:
        consider = links.copy()

    if mode == "highlight":
        selected_links = consider["s"].isin(selected_nodes) | consider["e"].isin(
            selected_nodes
        )
    elif mode == "isolate":
        selected_links = consider["s"].isin(selected_nodes) & consider["e"].isin(
            selected_nodes
        )
    elif mode == "bipartite":
        selected_links = consider["s"].isin(selected_nodes) ^ consider["e"].isin(
            selected_nodes
        )

    selected = consider[selected_links].copy()
    not_selected = links.loc[
        [link for link in links.index if link not in selected.index]
    ]
    # print(not_selected)

    not_selected["c"].values[:] = 0
    if link_color:
        selected["c"] = (
            selected["c"]
            .swifter.progress_bar(False)
            .apply(lambda x: link_color + (x[3],))
        )

    links = pd.concat([selected, not_selected])

    links = links.sort_index()
    links = links.reindex(range(len(links)))
    links["c"] = links["c"].apply(lambda x: 0 if isinstance(x, float) else x)

    out = os.path.join(out.links_rgb_dir, layout)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img = Image.new("RGBA", img_size)
    img.putdata(links["c"])
    img.save(out)
    return


def highlight_links(
    selected_nodes,
    selected_links,
    layouts,
    project: Project,
    out,
    mode,
    link_color,
):
    project.read_links()
    project.links_df = pd.DataFrame(project.links["links"])
    project.links_df: pd.DateOffset

    consider = project.links_df
    if selected_links is not None:
        consider = project.links_df[project.links_df.index.isin(selected_links)]
    if selected_nodes is None or len(selected_nodes) == 0:
        selected_nodes = consider["s"].append(consider["e"]).unique()

    args = [
        (
            selected_nodes,
            selected_links,
            project,
            out,
            mode,
            layout,
            link_color,
        )
        for layout in layouts
    ]
    n = len(layouts)
    p = n
    if n > os.cpu_count():
        p = os.cpu_count()
    with Pool(p) as pool:
        pool.starmap(handle_link_layout, args)
    return selected_nodes


def extract_node_data_from_tex(project: Project, layout):
    # layout = os.path.join("static", "projects", project, "layouts",layout+"XYZ.bmp")
    # layout_low = os.path.join("static", "projects", project, "layoutsl",layout+"XYZl.bmp")

    # image = Image.open(layout)
    # nodes["h"] = [
    #     x if x != (0, 0, 0) else pd.NA for x in image.getdata()
    # ]

    # image = Image.open(layout_low)
    # nodes["l"] = [
    #     x if x != (0, 0, 0) else pd.NA for x in image.getdata()
    # ]
    layout_rgb = os.path.join(project.layouts_rgb_dir, layout)
    columns = ["id"]
    nodes = project.nodes_df.copy()

    image = Image.open(layout_rgb)
    nodes["c"] = [
        x
        if x != (0, 0, 0, 0)
        and x != "<NA>"
        and x != np.nan
        and not isinstance(x, float)
        else pd.NA
        for x in image.getdata()
    ][: len(nodes)]
    return nodes


def extract_link_data_from_tex(project: Project, layout):
    # layout_xyz = os.path.join(project.links_dir, layout.replace("RGB.png", "XYZ.bmp"))
    layout_rgb = os.path.join(project.links_rgb_dir, layout)
    columns = ["s", "e"]
    links = project.links_df[[c for c in columns]].copy()

    # Colors
    image = Image.open(layout_rgb)
    links["c"] = [x if x != (0, 0, 0, 0) or pd.isna(x) else 0 for x in image.getdata()][
        : len(links.index)
    ]
    return links, image.size


def mask_links(project: Project, selected_links, selected_nodes, mode="highlight"):
    LINK_BITMAP_SIZE = 512
    # MASK WHICH HIGHLIGHTS NODES THAT ARE SELECTED
    links = pd.DataFrame(project.get_links()["links"])
    mask = np.zeros((LINK_BITMAP_SIZE, LINK_BITMAP_SIZE, 4))
    if selected_links is not None:
        consider = links.index.isin(selected_links)
        consider = links[consider].copy()
    else:
        consider = links.copy()
    if selected_nodes is None or len(selected_nodes) == 0:
        selected_nodes = links["s"].append(links["e"]).unique()

    if mode == "highlight":
        selected_links = consider["s"].isin(selected_nodes) | consider["e"].isin(
            selected_nodes
        )
    elif mode == "isolate":
        selected_links = consider["s"].isin(selected_nodes) & consider["e"].isin(
            selected_nodes
        )
    elif mode == "bipartite":
        selected_links = consider["s"].isin(selected_nodes) ^ consider["e"].isin(
            selected_nodes
        )
    selected_links = consider[selected_links].copy()
    if not selected_links.empty:
        x, y = (
            selected_links["id"] // LINK_BITMAP_SIZE,
            selected_links["id"] % LINK_BITMAP_SIZE,
        )
        x, y = x.astype(int), y.astype(int)
        mask[x, y, :] = 1
    mask = Image.fromarray(np.uint8(mask)).convert("RGBA")
    project.write_bitmap(
        mask,
        "mask",
        LINK,
        COLOR,
    )
    return selected_nodes


def mask_nodes(project: Project, selected_nodes):
    # MASK WHICH HIGHLIGHTS NODES THAT ARE SELECTED
    NODE_BITMAP_SIZE = 128
    nodes = pd.DataFrame(project.get_nodes()["nodes"])
    mask = np.zeros((NODE_BITMAP_SIZE, NODE_BITMAP_SIZE, 4))
    nodes = nodes[nodes["id"].isin(selected_nodes)].copy()
    x, y = nodes["id"] // NODE_BITMAP_SIZE, nodes["id"] % NODE_BITMAP_SIZE
    x, y = x.astype(int), y.astype(int)
    mask[x, y, :] = 1
    mask = Image.fromarray(np.uint8(mask)).convert("RGBA")
    project.write_bitmap(
        mask,
        "mask",
        NODE,
        COLOR,
    )


def apply_mask(project, layout, data_type=NODE, bitmap_type=COLOR):
    project = Project(project, False)
    mask = project.load_bitmap("mask", data_type, bitmap_type, True)
    layout_bmp = project.load_bitmap(layout, data_type, bitmap_type, True)
    if data_type == NODE:

        selected = np.zeros_like(layout_bmp)
        selected[layout_bmp > 0] = mask[layout_bmp > 0]
        # Multiply the two images element-wise
        if len(np.unique(layout_bmp)) >= 1:
            result = layout_bmp * selected
        else:
            # MAKE SELECTED NODES RED
            result[:, :, :3] = [255, 0, 0]

        non_zero = np.nonzero(selected)
        max_row = np.max(non_zero[0])
        non_zero = np.nonzero(selected[max_row])
        max_col = np.max(non_zero[0])
        not_selected = ~selected
        not_selected[:max_row, :, :] = NOT_SELECTED
        not_selected[max_row, :max_col, :] = NOT_SELECTED
        not_selected[max_row, max_col:, :] = NOT_SELECTED
        not_selected[max_row + 1 :, :, :] = NOT_SELECTED

        result = result + not_selected
        bmp = Image.fromarray(np.uint8(result))

    elif data_type == LINK:
        selected = np.zeros_like(layout_bmp)
        selected[layout_bmp > 0] = mask[layout_bmp > 0]
        result = layout_bmp * selected
        bmp = Image.fromarray(np.uint8(result))

    project.write_bitmap(bmp, layout, data_type, bitmap_type)


if __name__ == "__main__":
    # nodes = extract_node_data_from_tex("alz_100_ppi","cy")
    selected = [20, 50, 30]
    highlight_nodes(selected, "alz_100_ppi", "cy")
    # print("Nodes extracted")
    # extract_link_data_from_tex("alz_100_ppi", "any")
    # print("Links extracted")
