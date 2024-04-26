"""
Functions for Enrichment Module
"""
import GlobalData as GD
from PIL import Image
import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils as pu
import scipy.stats as st
from plotly.subplots import make_subplots
import math




ALPHA_VALUES = [0.05, 0.01, 0.005, 0.001]
MAX_AMOUNT_RESULTS = 20
COLOR_FEATURE_QUERY = (255, 166, 0, 150)
COLOR_FEATURE_BACKGROUND = (99, 110, 250, 100)
COLOR_NOTFEATURE_QUERY = (3, 218, 198, 100)
COLOR_BACKGROUND = (55, 55, 55, 30)


def validate():
    # check for set alpha
    if "enrichment-cutoff" not in GD.pdata.keys():
        GD.pdata["enrichment-cutoff"] = 0
        print("ENRICHMENT: WARNING: Significance level not selected. 0.05 significance niveau assumed.")
        return True

    # check for query
    if "enrichment_query" not in GD.pdata.keys():
        GD.pdata["enrichment_query"] = []
    if GD.pdata["enrichment_query"] == []:
        print("ENRICHMENT: ERROR: Query not selected.")
        return False

    # check for target
    if "enrichment-features" not in GD.pdata.keys():
        GD.pdata["enrichment-features"] = 0
    if GD.pdata["enrichment-features"] == []:
        print("ENRICHMENT: WARNING: Features not selected. Default features assumed.")
        return True
    
    return True


def query_from_clipboard():
    # function to move clipboard to query field
    GD.pdata["enrichment_query"] = []
    if "cbnode" not in GD.pdata.keys():
        print("ENRICHMENT: Clipboard empty")
        GD.savePD()
        return
    for node in GD.pdata["cbnode"]:
        GD.pdata["enrichment_query"].append(node)
    GD.savePD()


def query_clear():
    # function to clear query field
    GD.pdata["enrichment_query"] = []
    GD.savePD()



def _plot(data, highlight_bar=None):
    # preprocess
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]))
    data_size = len(sorted_data.items())
    display_note = None
    if len(sorted_data.items()) > MAX_AMOUNT_RESULTS:
        display_note = f"Warning: {MAX_AMOUNT_RESULTS} of {data_size} hits shown."
        data_size = MAX_AMOUNT_RESULTS

    if data_size == 0:
        display_note = "Warning: No significant feature hits."
        return

    names = list(sorted_data.keys())[:data_size]
    values = list(sorted_data.values())[:data_size]
    categories = [{"name": names[i], "value": values[i]} for i in range(data_size)]
    colors = ["#636efa" if i != highlight_bar else "orange" for i in range(data_size)]

    # Create subplots for each category
    subplots = make_subplots(
        rows=data_size,
        cols=1,
        subplot_titles=[f'{categories[i]["name"]} :: {categories[i]["value"]:.2e}' for i in range(len(categories))],
        shared_xaxes=True,
        print_grid=False,
        vertical_spacing=(0.45 / len(categories)),
    )

    # Add bars for each category
    for k, category in enumerate(categories):
        subplots.add_trace(
            go.Bar(
                x=[-math.log(category["value"])],
                y=[1],
                orientation='h',
                hoverinfo='text',
                text=f'{category["name"]} :: {category["value"]:.2e}',
                marker=dict(color=colors[k]),
                customdata=[[k, category["name"]]]   # retrievable for ui and responsive feedback
            ),
            row=k + 1, col=1
        )

    # Update the layout
    subplots.update_layout(
        font_color="rgb(200,200,200)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        title=None,
        yaxis=dict(categoryorder="total ascending", fixedrange=True),
        # https://plotly.com/python-api-reference/generated/plotly.graph_objects.layout.html#plotly.graph_objects.layout.XAxis
        xaxis=dict(
            fixedrange=True,
            type="log",
            zeroline=True,
            showticklabels=False
        ),
        bargap=0.1,
        height=45 * len(categories),
        margin=dict(l=20, r=20, t=40, b=20),
        dragmode=False
    )

    for annotation in subplots["layout"]['annotations']:
        annotation['x'] = 0
        annotation['xanchor'] = 'left'
        annotation['align'] = 'left'
        annotation['font'] = dict(
            size=12,
        )

    # Hide the axes
    for axis in subplots['layout']:
        if axis.startswith('yaxis'):
            subplots['layout'][axis]['visible'] = False

    # Update the margins and size
    subplots['layout']['margin'] = {
        'l': 5,
        'r': 0,
        't': 20,
        'b': 1,
    }
    for i in range(data_size):
        subplots.update_xaxes(type='log', row=i+1, col=1, showticklabels=False)

    height_calc = max([45 * len(categories), 350])
    subplots['layout']['height'] = height_calc
    subplots['layout']['width'] = 400

    plotly_json = json.dumps(subplots, cls=pu.PlotlyJSONEncoder)

    return plotly_json, display_note



def _fisher_test(sig_level, sampleset, d_sample_attributes, d_attributes_sample, background):
    """
    Implementation by Felix Mueller


    Perform a hypergeometric or Fisher's exact test for each feature in a set of samples, 
    using the corresponding attributes in d_sample_attributes and d_attributes_sample.

    Parameters:
    sig_level (float): the significance level of the test.
    sampleset (set): the set of samples to be tested.
    d_sample_attributes (dict): a dictionary with samples as keys and lists of attributes as values.
    d_attributes_sample (dict): a dictionary with attributes as keys and sets of samples as values.
    background (int): the total number of samples in the population.

    Returns:
    d_term_p (dict): a dictionary with attributes as keys and adjusted p-values as values.
    """
    # Make sure that all samples in the sampleset are present in the d_sample_attributes dictionary
    sample_overlap = set(sampleset) & set(d_sample_attributes.keys())

    # Extract all attributes associated with the samples in the sampleset
    l_terms = []
    for gene in sample_overlap:
        l_terms.extend(d_sample_attributes[gene])

    # Find the unique set of attributes and the number of tests to be performed
    set_terms = set(l_terms)
    number_of_tests = len(set_terms)


    # Perform the test for each attribute and calculate adjusted p-values
    d_term_p = {}
    for term in set_terms:
        attributeset = set(d_attributes_sample[term])

        ab = len(sample_overlap.intersection(attributeset))
        amb = len(sample_overlap.difference(attributeset))
        bma = len(attributeset.difference(sample_overlap))
        backg = background - ab - amb - bma

        oddsratio, pval = st.fisher_exact([[ab, amb], [bma, backg]], alternative='greater')
        adjusted_pval = pval * number_of_tests


        # Adjust the p-value based on the number of tests performed (Bonferroni)
        if adjusted_pval <= sig_level:
            d_term_p[term] = adjusted_pval

    return d_term_p


def _gen_highlight_textures(query_ids, feature_type, feature):
    
    print(1)
    path_nodes = "static/projects/"+ GD.data["actPro"] + "/layoutsRGB/temp_enrichment.png"
    path_links = "static/projects/"+ GD.data["actPro"] + "/linksRGB/temp_enrichment.png"
    nodes = GD.nodes["nodes"]
    links = GD.links["links"]
    query_id_set = set(query_ids)
    annotation_set = set(GD.annotations[feature_type][feature])

    node_colors = []
    for node in nodes:
        node_color = COLOR_BACKGROUND
        # is query but not has not feature
        if node["id"] in annotation_set and node["id"] not in query_id_set:
            node_color = COLOR_FEATURE_BACKGROUND
        # is not query but has feature
        if node["id"] not in annotation_set and node["id"] in query_id_set:
            node_color = COLOR_NOTFEATURE_QUERY
        # is query and has feature
        if node["id"] in annotation_set and node["id"] in query_id_set:
            node_color = COLOR_FEATURE_QUERY
        node_colors.append(node_color)
    
    texture_nodes_active = Image.open("static/projects/"+ GD.data["actPro"]  + "/layoutsRGB/"+ GD.pfile["layoutsRGB"][int(GD.pdata["layoutsRGBDD"])]+".png","r")
    texture_nodes = texture_nodes_active.copy()
    texture_nodes.putdata(node_colors)
    texture_nodes.save(path_nodes, "PNG")

    # generate link texture
    link_colors = []
    for link in links:
        link_color = COLOR_BACKGROUND
        start, end = int(link["s"]), int(link["e"])
        # both no feature and query
        if start in annotation_set and start not in query_id_set and end in annotation_set and end not in query_id_set:
            link_color = COLOR_FEATURE_BACKGROUND
        # both feature and no query
        if start not in annotation_set and start in query_id_set and end not in annotation_set and end in query_id_set:
            link_color = COLOR_NOTFEATURE_QUERY
        # both feature and query
        if start in annotation_set and start in query_id_set and end in annotation_set and end in query_id_set:
            link_color = COLOR_FEATURE_QUERY
        link_colors.append(link_color)
    
    texture_links_active = Image.open("static/projects/"+ GD.data["actPro"]  + "/linksRGB/"+ GD.pfile["linksRGB"][int(GD.pdata["linksRGBDD"])]+".png","r")
    texture_links = texture_links_active.copy()
    texture_links.putdata(link_colors)
    texture_links.save(path_links, "PNG")

    texture_links_active.close()
    texture_nodes_active.close()
    texture_links.close()
    texture_nodes.close()

    return {"path_nodes" : path_nodes, "path_links": path_links, "textures_created": True}


def main(highlight=None):
    
    
    print(highlight)
    
    # main process
    query_set = []
    test_result = {}
    features_type = None
    if highlight is None:
        query_set = [int(node["id"]) for node in GD.pdata["enrichment_query"]]
        alpha = ALPHA_VALUES[int(GD.pdata["enrichment-cutoff"])]
        features_type = GD.annotation_types[int(GD.pdata["enrichment-features"])]
        dict_features_to_samples = GD.annotations[features_type]
        dict_samples_to_features = {
            node: GD.nodes["nodes"][node]["attrlist"].get(features_type, []) for node in query_set  # case of type annotations
        } if GD.pfile.get("annotationTypes", False) else {
            node: GD.nodes["nodes"][node]["attrlist"][1:] for node in query_set  # case of list annotations, split off name from attrlist
        }
        background_count = int(GD.pfile["nodecount"])
        # run tests
        test_result = _fisher_test(
            sig_level = alpha, 
            sampleset = query_set, 
            d_sample_attributes = dict_samples_to_features, 
            d_attributes_sample = dict_features_to_samples, 
            background = background_count
        )

        if not test_result:
            return None, None, None, "Warning: No significant feature hits."

    # build plot and insert responsive payload
    highlight_bar, highlight_feature, highlight_feature_type, highlight_results, highlight_query_ids = None, None, features_type, test_result, query_set
    if highlight is not None:
        highlight_bar, highlight_feature, highlight_feature_type, highlight_results, highlight_query_ids = highlight


    plot_json, display_note = _plot(
        data = highlight_results, 
        highlight_bar=highlight_bar
    )

    # color highlighted annotation
    texture_obj = None
    if highlight is not None:
        try:
            texture_obj = _gen_highlight_textures(
                query_ids = highlight_query_ids, 
                feature_type = highlight_feature_type, 
                feature = highlight_feature
            )
        except:
            texture_obj = {"textures_created": False}

    # return results
    payload = [highlight_feature_type, highlight_results, highlight_query_ids]

    return plot_json, payload, texture_obj, display_note



if __name__ == "__main__":
    pass