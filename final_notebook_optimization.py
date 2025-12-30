
import json

nb_path = r"c:\Users\igour\Desktop\Prompt-Firewall\notebooks\3-llm-classification-finetuned.ipynb"

try:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # 1. Enable Gradient Checkpointing (Saves 60%+ VRAM)
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "TrainingArguments" in source:
                print("Found TrainingArguments.")
                new_source = []
                for line in cell["source"]:
                    if "TrainingArguments(" in line:
                        new_source.append(line)
                        # Inject gradient checkpointing right after instantiation
                        new_source.append('    gradient_checkpointing=True,  # Crucial for low VRAM\n')
                    elif "per_device_train_batch_size" in line:
                        new_source.append('    per_device_train_batch_size=1,  # Keep at 1\n')
                    else:
                        new_source.append(line)
                cell["source"] = new_source

    # 2. Robust VRAM Cleanup (Try/Except)
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "torch.cuda.empty_cache()" in source:
                print("Found CUDA cleanup cell.")
                # Wrap in try/except to avoid crashing the notebook on zombie processes
                cell["source"] = [
                    "# Robust VRAM cleanup\n",
                    "import gc\n",
                    "import torch\n",
                    "try:\n",
                    "    gc.collect()\n",
                    "    torch.cuda.empty_cache()\n",
                    "except RuntimeError as e:\n",
                    "    print(f'Warning: VRAM cleanup failed: {e}')\n",
                    "\n"
                ] + [line for line in cell["source"] if "gc.collect" not in line and "empty_cache" not in line]

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("Notebook optimized with Gradient Checkpointing and Safe Cleanup.")

except Exception as e:
    print(f"Error: {e}")
