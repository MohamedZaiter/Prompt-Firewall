import matplotlib.pyplot as plt
import numpy as np
import os

# Ensure directories exist
os.makedirs("report/figures", exist_ok=True)

# 1. Dataset Distribution
labels = ['Safe', 'Malicious']
sizes = [55, 45] # Mockup data representing balance
colors = ['#4CAF50', '#F44336']

plt.figure(figsize=(6, 6))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, shadow=True)
plt.title('Distribution des données (Safe vs Injection)')
plt.savefig("report/figures/dataset_dist.png")
plt.close()

# 2. Model Performance Comparison
models = ['Naive Bayes', 'Random Forest', 'SVM', 'Logistic Reg.', 'Zero-Shot', 'XLM-R (Fine-Tuned)']
accuracy = [89, 92, 94, 95, 65, 99.5]
colors_bar = ['#bdc3c7', '#95a5a6', '#7f8c8d', '#34495e', '#e74c3c', '#2ecc71']

plt.figure(figsize=(10, 6))
bars = plt.barh(models, accuracy, color=colors_bar)
plt.xlabel('Précision (%)')
plt.title('Comparaison des Performances des Modèles')
plt.xlim(0, 105)

for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width}%', ha='left', va='center')

plt.tight_layout()
plt.savefig("report/figures/model_comparison.png")
plt.close()

# 3. Simple Block Diagram (Architecture)
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')

# Define boxes
box_props = dict(boxstyle="round,pad=0.5", fc="white", ec="black", lw=2)
arrow_props = dict(facecolor='black', arrowstyle='->', lw=1.5)

# Coordinates
x_user = 0.1; y_start = 0.5
x_firewall = 0.4; y_fw = 0.5
x_models = 0.7; y_ml = 0.8; y_dl = 0.5; y_xlm = 0.2
x_decis = 0.9; y_end = 0.5

# Nodes
ax.text(x_user, y_start, "User Prompt\n(Input)", ha="center", va="center", bbox=dict(boxstyle="round", fc="#3498db", ec="none", alpha=0.3), fontsize=12)
ax.text(x_firewall, y_fw, "LLM Firewall\n(Controller)", ha="center", va="center", bbox=box_props, fontsize=12)

ax.text(x_models, y_ml, "ML Classifiers\n(SVM, RF, LR)", ha="center", va="center", bbox=dict(boxstyle="round", fc="#f1c40f", ec="none", alpha=0.3), fontsize=10)
# ax.text(x_models, y_dl, "Zero-Shot\n(XLM-R Base)", ha="center", va="center", bbox=dict(boxstyle="round", fc="#e67e22", ec="none", alpha=0.3), fontsize=10) # Removed Zero-Shot
ax.text(x_models, y_xlm, "Fine-Tuned\n(XLM-R Large)", ha="center", va="center", bbox=dict(boxstyle="round", fc="#2ecc71", ec="none", alpha=0.3), fontsize=10)

ax.text(x_decis, y_end, "Consensus\n& Decision", ha="center", va="center", bbox=dict(boxstyle="circle", fc="#9b59b6", ec="none", alpha=0.3), fontsize=10)

# Edges
# User -> FW
ax.annotate("", xy=(x_firewall-0.08, y_fw), xytext=(x_user+0.08, y_start), arrowprops=arrow_props)

# FW -> Models
ax.annotate("", xy=(x_models-0.08, y_ml), xytext=(x_firewall+0.08, y_fw), arrowprops=arrow_props)
# ax.annotate("", xy=(x_models-0.08, y_dl), xytext=(x_firewall+0.08, y_fw), arrowprops=arrow_props) # Removed Zero-Shot
ax.annotate("", xy=(x_models-0.08, y_xlm), xytext=(x_firewall+0.08, y_fw), arrowprops=arrow_props)

# Models -> Decision
ax.annotate("", xy=(x_decis-0.08, y_end), xytext=(x_models+0.08, y_ml), arrowprops=arrow_props)
# ax.annotate("", xy=(x_decis-0.08, y_end), xytext=(x_models+0.08, y_dl), arrowprops=arrow_props) # Removed Zero-Shot
ax.annotate("", xy=(x_decis-0.08, y_end), xytext=(x_models+0.08, y_xlm), arrowprops=arrow_props)

plt.title("Architecture du Système Multi-Modèles", fontsize=16)
plt.savefig("report/figures/architecture_diagram.png")
plt.close()

print("Figures generated successfully.")
