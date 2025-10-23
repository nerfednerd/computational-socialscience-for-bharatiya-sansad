import os
import papermill as pm

input_folder = "../preprocessing/agg_outputs"
output_folder = "agg_party"
executed_folder = "executed"
party_lookup_path = "metadata_mapping_16_17_18.csv"
notebook_template = "mapper.ipynb"

os.makedirs(output_folder, exist_ok=True)
os.makedirs(executed_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        base_name = filename.replace(".csv", "")
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"{base_name}_with_partyname.csv")
        executed_notebook = os.path.join(executed_folder, f"{base_name}_executed.ipynb")

        print(f"Processing: {filename}")
        pm.execute_notebook(
            notebook_template,
            executed_notebook,
            parameters={
                "input_csv_path": input_path,
                "output_csv_path": output_path,
                "party_lookup_path": party_lookup_path
            }
        )