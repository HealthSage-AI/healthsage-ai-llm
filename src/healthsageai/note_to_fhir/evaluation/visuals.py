import plotly.graph_objects as go
from collections import defaultdict
from healthsageai.note_to_fhir.evaluation.datamodels import FhirDiff
import pprint


def dict_to_html(fhir_dict: dict) -> str:
    """Prettify a FHIR dict for HTML output. Dicts are shortened to 100 characters

    Args:
        fhir_dict (dict): dictionary with FHIR data

    Returns:
        str: HTML string with FHIR data, where newlines and tabs are replaced by <br> and spaces.
    """
    if isinstance(fhir_dict, defaultdict):
        fhir_dict = dict(fhir_dict)
    printer = pprint.PrettyPrinter(depth=1)
    dict_pretty = printer.pformat(fhir_dict)
    dict_pretty = dict_pretty.replace("\t", "  ").replace("\n", "<br>")
    if len(dict_pretty) > 100 and len(dict_pretty.split("<br>")) > 3:
        dict_lines = dict_pretty.split("<br>")
        dict_pretty = (
            dict_lines[0]
            + "<br>"
            + f"<i>...{len(dict_lines)-2} lines...</i>"
            + "<br>"
            + dict_lines[-1]
        )
    return dict_pretty


def preprocess_for_treemap(diff: FhirDiff):
    """Flattens a nested FhirDiff object for plotly treemaps

    Args:
        comparison (FhirDiff): FhirDiff object

    Returns:
        (labels, parents, values):
            - labels define the "name" of the node
            - parents define the parent label
            - values or the content of the treemap
    """

    # Current Node
    labels = [diff.label]
    parents = [diff.parent.label] if diff.parent else [""]
    values = [diff]

    if not diff.children:
        return labels, parents, values

    for child_comparison in diff.children.values():
        if isinstance(child_comparison, list):
            for child_comparison_item in child_comparison:
                new_labels, new_parents, new_values = preprocess_for_treemap(
                    child_comparison_item
                )
                labels = labels + new_labels
                parents = parents + new_parents
                values = values + new_values

        else:
            new_labels, new_parents, new_values = preprocess_for_treemap(
                child_comparison
            )
            labels = labels + new_labels
            parents = parents + new_parents
            values = values + new_values

    return labels, parents, values


def show_diff(diff: FhirDiff) -> None:
    """Produces a treemap visualization of the FhirDiff object in plotly

    Args:
        diff (FhirDiff): Processed FhirDiff object with scores calculated.
    """
    labels, parents, values = preprocess_for_treemap(diff)
    max_level = max([len(x.label.split(".")) for x in values])

    # Shorten text labels for treemap, only use last part of label, or last 2 parts if last part refers to index
    labels_short = [
        label.split(".")[-1]
        if not label.split(".")[-1].isnumeric()
        else label.split(".")[-2:]
        for label in labels
    ]

    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=[max_level + 1 - len(x.label.split(".")) for x in values],
            textinfo="text",
            text=labels_short,
            hovertext=[
                f"{x.score}<br><i>true: </i>{dict_to_html(x.fhir_true)}<br><i>pred: </i>{dict_to_html(x.fhir_pred)}"
                for x in values
            ],
            hoverinfo="text",
            marker_colors=[x.score.accuracy for x in values],
            marker_colorscale="RdBu",
            marker_cmid=0.5,
        )
    )

    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    fig.update_traces(marker=dict(cornerradius=5))
    fig.show()
