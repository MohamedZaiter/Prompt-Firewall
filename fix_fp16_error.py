
import json

nb_path = r"c:\Users\igour\Desktop\Prompt-Firewall\notebooks\3-llm-classification-finetuned.ipynb"

try:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Switch FP16 to BF16 (Fixes scaling error on RTX 40 series)
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "TrainingArguments" in source:
                print("Found TrainingArguments.")
                new_source = []
                for line in cell["source"]:
                    if "fp16=True," in line:
                        new_source.append('    fp16=False,                     # Disabled to prevent unscaling errors\n')
                        new_source.append('    bf16=True,                      # Enabled BF16 for stability\n')
                    else:
                        new_source.append(line)
                cell["source"] = new_source

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("Notebook optimized: Switched FP16 -> BF16.")

except Exception as e:
    print(f"Error: {e}")
