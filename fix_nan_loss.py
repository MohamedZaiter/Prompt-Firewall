
import json

nb_path = r"c:\Users\igour\Desktop\Prompt-Firewall\notebooks\3-llm-classification-finetuned.ipynb"

try:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Switch to FP32 (Disable both FP16 and BF16) and Lower LR
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "TrainingArguments" in source:
                print("Found TrainingArguments.")
                new_source = []
                for line in cell["source"]:
                    if "fp16=" in line or "bf16=" in line:
                        # Remove existing flags to fallback to default (FP32)
                        pass
                    elif "learning_rate=" in line:
                        new_source.append('    learning_rate=1e-5,             # Lowered to prevent divergence (NaN loss)\n')
                    else:
                        new_source.append(line)
                
                # Re-add flags explicitly to ensure FP32
                # We find the closing brace )
                for i, line in enumerate(new_source):
                    if ")" in line:
                        new_source.insert(i, '    fp16=False,                     # Force FP32 for numeric stability\n')
                        new_source.insert(i+1, '    bf16=False,                     # Force FP32 for numeric stability\n')
                        break
                
                cell["source"] = new_source

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("Notebook optimized: Switched to FP32 and Lowered LR.")

except Exception as e:
    print(f"Error: {e}")
