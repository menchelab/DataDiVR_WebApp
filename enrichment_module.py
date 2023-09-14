"""
Functions for Enrichment Module
"""
import GlobalData as GD
from PIL import Image
import math
import json
import plotly.graph_objs as go
import plotly.utils as pu
import numpy as np
import util
import scipy.stats as st



ALPHA_VALUES = [0.05, 0.01, 0.005, 0.001]


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

def _plot():...

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

        oddsratio, pval = st.fisher_exact([[ab, amb], [bma, backg]],alternative='greater')
        adjusted_pval = pval * number_of_tests

        # Adjust the p-value based on the number of tests performed (Bonferroni)
        if adjusted_pval > sig_level:
            d_term_p[term] = 1.0
        else:
            d_term_p[term] = adjusted_pval

    return d_term_p
    


def main():
    # input preprocessing
    query_set = [int(node["id"]) for node in GD.pdata["enrichment_query"]]
    alpha = ALPHA_VALUES[int(GD.pdata["enrichment-cutoff"])]
    features_type = GD.annotation_types[int(GD.pdata["enrichment-features"])]
    dict_features_to_samples = GD.annotations[features_type]
    dict_samples_to_features = {
        node: GD.nodes["nodes"][node]["attrlist"].get(features_type, []) for node in query_set  # case of type annotations
    } if GD.pfile.get("annotationTypes", False) else {
        node: GD.nodes["nodes"][node]["attrlist"][1:] for node in query_set  # case of list annotations
    }
    background_count = int(GD.pfile["nodecount"])
    
    print("uhm==???")

    # run tests
    result = _fisher_test(
        sig_level = alpha, 
        sampleset = query_set, 
        d_sample_attributes = dict_samples_to_features, 
        d_attributes_sample = dict_features_to_samples, 
        background = background_count
    )

    print(result)

    # build plot
    # return results
    return


if __name__ == "__main__":
    pass