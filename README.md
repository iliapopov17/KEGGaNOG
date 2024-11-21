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

- `eggNOG-mapper` is a beautiful tool for fast functional annotation of novel sequences. Yet it does not provide any visualization functions.
- `KEGG-Decoder` is a perfect tool for visualizing KEGG Pathways. But it only takes `KEGG-Koala` outputs as an input (including blastKOALA, ghostKOALA, KOFAMSCAN).
- `KEGG-Koala` is a web-tool which can work for more than 24 hours. `eggNOG-mapper` can be installed locally on your PC / server and work faster.
- This tool `KEGGaNOG` makes `eggNOG-mapper` meet `KEGG-Decoder`! It parses `eggNOG-mapper` output, make it fit for the input to `KEGG-Decoder` and then visualize KEGG Pathways as the heatmap!
- **Pro-tip:** `eggNOG-mapper` and `KEGGaNOG` could be wrapped into 🐍 `Snakemake` pipeline making metabolic profiling a "one-click" process!

## Installation

`KEGG-Decoder` is hardwired into `KEGGaNOG`<br>
`KEGG-Decoder` uses `python=3.6`<br>
That's why `KEGGaNOG` uses this version too<br>
There are some compatibility issues, yet they are managed (however, installing `KEGGaNOG` on macOS is a bit not standart)

```bash
# Linux / WSL / Intel Macs
conda create -n kegganog python=3.6
conda activate kegganog
pip install kegganog
```

```bash
# ARM Macs (Apple M1-M4 and so on)
CONDA_SUBDIR=osx-64 conda create -n kegganog python=3.6 python.app
conda activate kegganog
pip install kegganog
alias KEGGaNOG="pythonw $(which KEGGaNOG)"

# In case user needs to unalias KEGGaNOG from pythonw
unalias KEGGaNOG
# To check if KEGGaNOG uses python or pythonw
which KEGGaNOG
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

## Contributing
Contributions are welcome! If you have any ideas, bug fixes, or enhancements, feel free to open an issue or submit a pull request.

## Contact
For any inquiries or support, feel free to contact me via [email](mailto:iljapopov17@gmail.com)

Happy functional annotation! 💻🧬
