#  Copyright (c) 2023. HealthSage AI.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from measures import ResourceBundleDistance, ResourceDistance
import matplotlib.pyplot as plt
from datasets import load_dataset
from measures import validate_resource, resource_mapping

import json
import pandas as pd

dataset = load_dataset("healthsage/example_fhir_output")

def clear_empty(bundle):
    cleared_resources = []
    for entry in bundle['entry']:
        clean_resource = {}
        keyvals = [(k, v) for k, v in entry['resource'].items()]
        for k, v in keyvals:
            if v != None:
                clean_resource[k] = v
        cleared_resources.append({"resource": clean_resource})
    bundle['entry'] = cleared_resources
    return bundle


notes = load_dataset('healthsage/fhir-to-note-v2')

notes = notes['test']['note']

fhirsage_lst = [x for x in dataset['train']['fhirsage'] if len(x)>30]

dataset["train"] = dataset['train'].filter(lambda row: (len(row['fhirsage']) > 10) & (len(row['gpt4']) > 10))

gpt4_compare = pd.DataFrame({"fhir_true": dataset["train"]["fhir_true"], "gpt4": dataset["train"]["gpt4"]})
gpt4_compare['gpt4'] = gpt4_compare['gpt4'].apply(json.loads)
gpt4_compare['gpt4'] = gpt4_compare['gpt4'].apply(clear_empty)
gpt4_compare['fhir_true'] = gpt4_compare['fhir_true'].apply(json.loads)
gpt4_compare['fhir_true'] = gpt4_compare['fhir_true'].apply(clear_empty)

fhirsage_compare = pd.DataFrame({"fhir_true": dataset["train"]["fhir_true"], "fhirsage": dataset["train"]["fhirsage"]})
fhirsage_compare['fhirsage'] = fhirsage_compare['fhirsage'].apply(json.loads)
fhirsage_compare['fhirsage'] = fhirsage_compare['fhirsage'].apply(clear_empty)
fhirsage_compare['fhir_true'] = fhirsage_compare['fhir_true'].apply(json.loads)
fhirsage_compare['fhir_true'] = fhirsage_compare['fhir_true'].apply(clear_empty)



def correct_gpt(bundle):
    resources = bundle['entry']['resource']
    entry = [{"resource": item} for item in resources]
    bundle['entry'] = entry
    return bundle

#gpt4_compare['gpt4'] = gpt4_compare['gpt4'].apply(correct_gpt)

gpt4_compare['gpt4'].loc[3]

def compare(fhir_true_lst, fhir_pred_lst):
    accuracies = []
    distances = []
    for fhir_true, fhir_pred in zip(fhir_true_lst, fhir_pred_lst):
        if len(fhir_true['entry']) == 0:
            continue
        fhir_true_entry = [x['resource'] for x in fhir_true['entry']]
        fhir_pred_entry = [x['resource'] for x in fhir_pred['entry']]
        distance = ResourceBundleDistance(fhir_true_entry,fhir_pred_entry)
        accuracies.append(distance.bundle_accuracy)
        distances.append(distance)
        
        
    return accuracies, distances

def report_distances(dists):
    all_entry_scores = [x.entry_scores for x in dists]
    all_entry_scores = pd.DataFrame(pd.concat(all_entry_scores,axis=0))
    all_entry_scores = all_entry_scores.groupby(['resource_type']).mean()
    all_entry_scores.reset_index(inplace=True)
    all_entry_scores.columns = ['resource_type', 'accuracy']
    all_entry_scores = all_entry_scores.sort_values(by='accuracy', ascending=False)
    all_entry_scores.set_index('resource_type', inplace=True)
    return all_entry_scores

def report_syntax_score(bundles):
    syntax_scores = []
    for bundle in bundles:
        for resource in bundle['entry']:
            valid = validate_resource(resource['resource'])
            try:
                syntax_scores.append([resource['resource']['resourceType'], valid])
            except:
                syntax_scores.append(["unknown", False])
    return syntax_scores

    
accs, dists = compare(gpt4_compare['fhir_true'].tolist(), gpt4_compare['gpt4'].tolist())
_, dists_sage = compare(fhirsage_compare['fhir_true'].tolist(), fhirsage_compare['fhirsage'].tolist())

final_comparison = pd.concat([report_distances(dists), report_distances(dists_sage)], axis=1)
final_comparison.columns = ['gpt4', 'fhirsage']
final_comparison = final_comparison.sort_values(by='fhirsage', ascending=False)
final_comparison.plot(kind='bar')

syntax_scores_sage = report_syntax_score(fhirsage_compare['fhirsage'].tolist())
syntax_scores_gpt4 = report_syntax_score(gpt4_compare['gpt4'].tolist())
syntax_scores_synth = report_syntax_score(gpt4_compare['fhir_true'].tolist())

syntax_scores_sage = pd.DataFrame(syntax_scores_sage, columns=['resource_type', 'syntax_validity'])
syntax_scores_sage['source'] = 'fhirsage'
syntax_scores_gpt4 = pd.DataFrame(syntax_scores_gpt4, columns=['resource_type', 'syntax_validity'])
syntax_scores_gpt4['source'] = 'gpt4'
syntax_scores_synth = pd.DataFrame(syntax_scores_synth, columns=['resource_type', 'syntax_validity'])
syntax_scores_synth['source'] = 'synthea'

syntax_scores_both = pd.concat([syntax_scores_sage, syntax_scores_gpt4,syntax_scores_synth], axis=0)

score_per_source = syntax_scores_both[["source","syntax_validity"]].groupby("source").mean()
plt.figure()
score_per_source.plot(kind='bar', title="Syntax Validity per LLM")
plt.show()

score_per_resource_source = syntax_scores_both.pivot_table(index="resource_type", columns="source",aggfunc="mean")
score_per_resource_source = score_per_resource_source[score_per_resource_source.index.isin(resource_mapping.keys())]

plt.figure()
score_per_resource_source.plot(kind='bar', title="Syntax Validity per Resource Type")
plt.show()




