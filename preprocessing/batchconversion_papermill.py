from pathlib import Path
import papermill as pm

input_folder = Path("misc")
output_folder = Path("agg_outputs")
output_folder.mkdir(exist_ok=True)

for file in input_folder.glob("*.csv"):
    print(f"🚀 Processing {file.name} ...")

    output_notebook = output_folder / f"run_{file.stem}.ipynb"

    pm.execute_notebook(
        "prepro.ipynb",           # input notebook
        str(output_notebook),     # output notebook for each file
        parameters=dict(
            input_file=str(file),
            output_dir=str(output_folder)
        )
    )

print("✅ All files processed successfully.")
