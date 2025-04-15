# KEGGaNOG

<img src="https://github.com/iliapopov17/KEGGaNOG/blob/main/imgs/KaN_logo_light.png#gh-light-mode-only" align="left" width = 25%/>
<img src="https://github.com/iliapopov17/KEGGaNOG/blob/main/imgs/KaN_logo_dark.png#gh-dark-mode-only" align="left" width = 25%/>

<br>
<br>

![Python3](https://img.shields.io/badge/Language-Python3-steelblue)
![Pandas](https://img.shields.io/badge/Dependecy-Pandas-steelblue)
![Seaborn](https://img.shields.io/badge/Dependecy-Seaborn-steelblue)
![Matplotlib](https://img.shields.io/badge/Dependecy-Matplotlib-steelblue)
![Numpy](https://img.shields.io/badge/Dependecy-Numpy-steelblue)
![KEGG-Decoder](https://img.shields.io/badge/Dependecy-KEGG_Decoder-steelblue)
![License](https://img.shields.io/badge/License-MIT-steelblue)
[![Downloads](https://static.pepy.tech/badge/kegganog)](https://pepy.tech/project/kegganog)

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=macos&logoColor=F0F0F0)

<br>
<br>

## Motivation

[**`eggNOG-mapper`**](https://github.com/eggnogdb/eggnog-mapper) 🤝 [**`KEGG-Decoder`**](https://github.com/bjtully/BioData/blob/master/KEGGDecoder/README.md)

- `eggNOG-mapper` is a comprehensive tool for fast functional annotation of novel sequences. Yet it does not provide any visualization functions.
- `KEGG-Decoder` is a perfect tool for visualizing KEGG Pathways. But it only takes `KEGG-Koala` outputs as an input (including blastKOALA, ghostKOALA, KOFAMSCAN).
- `KEGG-Koala` is a web-tool which can work for more than 24 hours. `eggNOG-mapper` can be installed locally on your PC / server and work faster.
- This tool `KEGGaNOG` makes `eggNOG-mapper` meet `KEGG-Decoder`! It parses `eggNOG-mapper` output, make it fit for the input to `KEGG-Decoder` and then visualize KEGG Pathways as the heatmap!
- **Pro-tip:** `eggNOG-mapper` and `KEGGaNOG` could be wrapped into 🐍 `Snakemake` pipeline making metabolic profiling a "one-click" process!

## Installation

```bash
# Linux / WSL / macOS
conda create -n kegganog pip -y
conda activate kegganog
pip install kegganog
```

## Usage Guide

```
usage: KEGGaNOG [-h] [-M] -i INPUT -o OUTPUT [-dpi DPI] [-c COLOR] [-n NAME]
                [-g] [-V]

KEGGaNOG: Link eggNOG-mapper and KEGG-Decoder for pathway visualization.

optional arguments:
  -h, --help            show this help message and exit
  -M, --multi           “Multi” mode allows to run KEGGaNOG on multiple
                        eggNOG-mapper annotation files (a text file with file
                        location paths must be passed to the input)
  -i INPUT, --input INPUT
                        Path to eggNOG-mapper annotation file
  -o OUTPUT, --output OUTPUT
                        Output folder to save results
  -dpi DPI, --dpi DPI   DPI for the output image (default: 300)
  -c COLOR, --color COLOR, --colour COLOR
                        Cmap for seaborn heatmap. Recommended options: Greys,
                        Purples, Blues, Greens, Oranges, Reds (default: Blues)
  -n NAME, --name NAME  Sample name for labeling (default: SAMPLE) (not active
                        in `--multi` mode)
  -g, --group           Group the heatmap based on predefined categories
  -V, --version         show program's version number and exit
```

🔗 Please visit [KEGGaNOG wiki](https://github.com/iliapopov17/KEGGaNOG/wiki) page

## Output examples gallery

**Default visualization**

|Single mode|Multi mode|
|-----------|----------|
|![heatmap_figure](https://github.com/user-attachments/assets/2b50518d-1fff-46d6-8bfc-6a5b8c31356d)|![heatmap_figure](https://github.com/user-attachments/assets/484077b9-8212-4aa2-8a3e-1a831afba26f)|

These figures are generated using functional groupping mode (`-g`/`--group`) and `Greens` colormap

**User APIs visualization**

|[Barplot](https://github.com/iliapopov17/KEGGaNOG/wiki/Barplot-API)|[Boxplot](https://github.com/iliapopov17/KEGGaNOG/wiki/Boxplot-API)|[Radarplot](https://github.com/iliapopov17/KEGGaNOG/wiki/Radarplot-API)|[Correlation Network](https://github.com/iliapopov17/KEGGaNOG/wiki/Correlation-Network-API)|
|-------|-------|---------|-------------------|
|![image](https://github.com/user-attachments/assets/81d69bef-f69c-4960-b2d3-73e348e3853a)|![image](https://github.com/user-attachments/assets/f98fd993-20b7-4b00-b203-83b40fe35f9c)|![image](https://github.com/user-attachments/assets/dd75e5d8-e3c8-4eaa-b009-02c042534a53)|![image](https://github.com/user-attachments/assets/e76057b9-bcfd-4ba9-a4cf-cb7b4269441a)|

## Advantages

1. **Seemless Access to KEGG Annotations:** Provides KEGG Ortholog (KO) annotations without requiring a KEGG license.
2. **High-Throughput Capability:** Optimized for rapid KO assignment in large-scale datasets, ideal for metagenomics and genomics projects.
3. **Broad Functional Coverage:** Leverages the extensive eggNOG database to annotate genes across a wide range of taxa.

## Limitation

1. **Indirect KO Mapping:** `eggNOG-mapper` doesn’t directly use the KEGG database, its KO term assignments are inferred through orthologous groups (eggNOG entries). This can sometimes result in less precise annotations.

## Tool name background

`KEGGaNOG` stands for “KEGG out of NOG”, highlighting its purpose: extracting KEGG Ortholog annotations from eggNOG’s Non-supervised Orthologous Groups.

## Contributing
Contributions are welcome! If you have any ideas, bug fixes, or enhancements, feel free to open an issue or submit a pull request.

## Contact
For any inquiries or support, feel free to contact me via [email](mailto:iljapopov17@gmail.com)

Happy functional annotation! 💻🧬

## Acknowledgements

For now `KEGGaNOG` uses [**`KEGG-Decoder`**](https://github.com/bjtully/BioData/blob/master/KEGGDecoder/KEGG_decoder.py) as a main dependecy. I greatly thank [**`KEGG-Decoder`**](https://github.com/bjtully/BioData/blob/master/KEGGDecoder/KEGG_decoder.py)'s developers.
