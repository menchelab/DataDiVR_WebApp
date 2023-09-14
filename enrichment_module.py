"""
Functions for Enrichment Module
"""
import GlobalData as GD
from PIL import Image
import math
import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils as pu
import scipy.stats as st
from plotly.subplots import make_subplots




ALPHA_VALUES = [0.05, 0.01, 0.005, 0.001]
MAX_AMOUNT_RESULTS = 10


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


def _plot2(data, highlight=None):
    # preprocess
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]))
    data_size = min(MAX_AMOUNT_RESULTS, len([v for k,v in sorted_data.items() if v < 1]))
    names = list(sorted_data.keys())[:data_size]
    values = list(sorted_data.values())[:data_size]
    colors = ["#636efa" if i != highlight else "orange" for i in range(data_size)]

    print(data, "\n",sorted_data,"\n", names,"\n", values)

    # Create the bar trace with names on top of the bars
    bar_trace = go.Bar(
        x=values,
        y=None,  # Names are on top of the bars
        orientation='h',
        text=[f'{name} :: {value}' for name, value in zip(names, values)],
        textposition='outside',
        marker=dict(color=colors)
    )

    # plot
    fig = go.Figure(bar_trace)

    fig.update_layout(
        title=None,
        xaxis=dict(title="P-Value", fixedrange=True, type="log"),
        yaxis=dict(title="Features", categoryorder="total ascending", fixedrange=True),
        bargap=0.1,
        width=400,
        height=400,
        font_color="rgb(200,200,200)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=40, t=30, b=10),
        uniformtext_minsize=12,
        uniformtext_mode='show'
    )

    fig.update_yaxes(showticklabels=False)
    plotly_json = json.dumps(fig, cls=pu.PlotlyJSONEncoder)

    return plotly_json





def _plot(data, highlight=None, feature_type=None):
    # preprocess
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]))
    data_size = min(MAX_AMOUNT_RESULTS, len([v for k, v in sorted_data.items() if v < 1]))
    names = list(sorted_data.keys())[:data_size]
    values = list(sorted_data.values())[:data_size]
    categories = [{"name": names[i], "value": values[i]} for i in range(data_size)]
    if highlight is not None:
        highlight = int(highlight)
    colors = ["#636efa" if i != highlight else "orange" for i in range(data_size)]

    print(colors, highlight)

    data_offset = 1e-10 
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
                x=[category["value"]],
                y=[category["value"]],
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
        width=550,
        font_color="rgb(200,200,200)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        title=None,
        yaxis=dict(categoryorder="total ascending", fixedrange=True, type="log"),
        xaxis=dict(
            fixedrange=True,
            type="log",
            zeroline=True,
            tickvals=np.logspace(np.log10(data_offset), np.log10(max(values)), num=5),
            ticktext=["{:.0e}".format(val) for val in np.logspace(np.log10(data_offset), np.log10(max(values)), num=5)],
        ),
        bargap=0.1,
        height=45 * len(categories),
        uniformtext_minsize=12,
        uniformtext_mode='show',
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
        'l': 0,
        'r': 0,
        't': 20,
        'b': 1,
    }
    for i in range(data_size):
        subplots.update_xaxes(type='log', row=i+1, col=1)

    height_calc = max([45 * len(categories), 350])
    subplots['layout']['height'] = height_calc
    subplots['layout']['width'] = height_calc

    plotly_json = json.dumps(subplots, cls=pu.PlotlyJSONEncoder)

    return plotly_json




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
        if adjusted_pval > sig_level:
            d_term_p[term] = 1.0
        else:
            d_term_p[term] = adjusted_pval

    return d_term_p



def main(highlight):
    # input preprocessing
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

    # build plot
    highlight_bar, highlight_feature = None, None
    if highlight is not None:
        highlight_bar, highlight_feature = highlight
    plot_json = _plot(test_result, highlight=highlight_bar, feature_type=features_type)

    # color highlighted annotation
    if highlight is not None:
        print("TODO: color annotation", features_type, highlight_feature)

    # return results
    return test_result, plot_json



if __name__ == "__main__":
    pass