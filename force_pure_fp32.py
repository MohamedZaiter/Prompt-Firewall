
import json

nb_path = r"c:\Users\igour\Desktop\Prompt-Firewall\notebooks\3-llm-classification-finetuned.ipynb"

try:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # 1. Remove torch_dtype=torch.float16 from model loading (Reset to FP32)
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "XLMRobertaForSequenceClassification.from_pretrained" in source:
                print("Found model loading cell.")
                # We overwrite the entire source to ensure it's clean
                cell["source"] = [
                    "# Clear VRAM before loading model\n",
                    "import gc\n",
                    "import torch\n",
                    "try:\n",
                    "    gc.collect()\n",
                    "    torch.cuda.empty_cache()\n",
                    "except: pass\n",
                    "\n",
                    "# Load pre-trained Model in Pure FP32 (Stable)\n",
                    "model = XLMRobertaForSequenceClassification.from_pretrained(\n",
                    "    'xlm-roberta-base', \n",
                    "    num_labels=2,\n",
                    "    low_cpu_mem_usage=True\n",
                    ")\n"
                ]

    # 2. Add Gradient Clipping to TrainingArguments
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "TrainingArguments" in source:
                print("Found TrainingArguments.")
                new_source = []
                for line in cell["source"]:
                    if "TrainingArguments(" in line:
                        new_source.append(line)
                        new_source.append('    max_grad_norm=0.5,              # Aggressive clipping to prevent explosion\n')
                    else:
                        new_source.append(line)
                cell["source"] = new_source

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("Notebook optimized: Full Pipeline FP32 + Gradient Clipping.")

except Exception as e:
    print(f"Error: {e}")
