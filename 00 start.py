import os

# 使用当前目录，即脚本所在目录
project = os.path.dirname(os.path.abspath(__file__))

folders = [
    f"{project}/src",
    f"{project}/gds",
    f"{project}/notebooks",
]

files = {
    f"{project}/src/bs_50_50.py": "# Beamsplitter design script\n",
    f"{project}/src/test_circuit.py": "# Test circuit design script\n",
    f"{project}/src/doe.py": "# Design of experiment script\n",
    f"{project}/gds/.keep": "",
    f"{project}/notebooks/simulation.ipynb": "",
    f"{project}/README.md": "# Project README\n",
}

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for filepath, content in files.items():
    with open(filepath, "w") as f:
        f.write(content)

print(f"Project structure created under {project}")
