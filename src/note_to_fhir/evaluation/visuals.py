import plotly.graph_objects as go
from collections import defaultdict
from src.note_to_fhir.evaluation.datamodels import FhirDiff
import pprint

def dict_to_html(fhir_dict):
    if type(fhir_dict) == defaultdict:
        fhir_dict = dict(fhir_dict)
    printer = pprint.PrettyPrinter(depth=1)
    dict_pretty = printer.pformat(fhir_dict)
    dict_pretty = dict_pretty.replace("\t", "  ").replace("\n", "<br>")
    return dict_pretty

def preprocess_for_treemap(comparison: FhirDiff):
    """Flattens a nested comparison object for plotly treemaps

    Args:
        comparison (FhirComparison): FhirComparison object

    Returns:
        (labels, parents, values):
            - labels define the "name" of the node
            - parents define the parent label
            - values or the content of the treemap 
    """

    # Current Node
    labels = [comparison.label]
    parents = [comparison.parent.label] if comparison.parent else [""]
    values = [comparison]

    if not comparison.children:
        return labels, parents, values
    
    for child_comparison in comparison.children.values():
        if type(child_comparison) == list:
            for child_comparison_item in child_comparison:
                new_labels, new_parents, new_values = preprocess_for_treemap(child_comparison_item)
                labels = labels + new_labels
                parents = parents + new_parents
                values = values + new_values

        else:
            new_labels, new_parents, new_values = preprocess_for_treemap(child_comparison)
            labels = labels + new_labels
            parents = parents + new_parents
            values = values + new_values

    return labels, parents, values

def show_diff(diff: FhirDiff):
    labels, parents, values = preprocess_for_treemap(diff)
    max_level = max([len(x.label.split(".")) for x in values])
    labels_short = [label.split(".")[-1] for label in labels]


    fig = go.Figure(go.Treemap(
        labels = labels,
        parents = parents,
        values = [max_level + 1 - len(x.label.split(".")) for x in values],
        textinfo= "text",
        text=labels_short,
        hovertext=[f"{x.score}<br>true: {dict_to_html(x.fhir_true)}<br>pred: {dict_to_html(x.fhir_pred)}" for x in values],
        hoverinfo="text",
        marker_colors=[x.score.score for x in values],
        marker_colorscale='RdBu',
        marker_cmid=0.5
    ))

    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    fig.update_traces(marker=dict(cornerradius=5))
    fig.show()