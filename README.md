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

🔗 Please also visit [KEGGaNOG wiki](https://github.com/iliapopov17/KEGGaNOG/wiki) page

> Wiki page is in process of rewritting!

**Output examples**

|Single mode|Multi mode|
|-----------|----------|
|![single](https://github.com/user-attachments/assets/5c4d4377-8053-48d7-b7f1-4a4172e1df49)|![multi](https://github.com/user-attachments/assets/d2810d22-52c0-4ac0-9478-9a397c40a026)|

These figures are generated using functional groupping mode (`-g`/`--group`), `Blues` colormap and 300 dpi

## Advantages

1. **Free Access to KEGG Annotations:** Provides KEGG Ortholog (KO) annotations without requiring a KEGG license, making it budget-friendly.
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

In previous versions of `KEGGaNOG` [**`KEGG-Decoder`**](https://github.com/bjtully/BioData/blob/master/KEGGDecoder/README.md) was used as a dependecy. It made me use `Python 3.6`, which is no good by the end of 2024. In `KEGGaNOG` v. 0.7.0 and higher `Python 3.13.1` is used. It became possible after I used not the whole [**`KEGG-Decoder`**](https://github.com/bjtully/BioData/blob/master/KEGGDecoder/README.md), but its one [script](https://github.com/bjtully/BioData/blob/master/KEGGDecoder/KEGG_decoder.py). I greatly thank `KEGG-Decoder`'s developers.
