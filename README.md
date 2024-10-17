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

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=macos&logoColor=F0F0F0)

<br>
<br>
<br>

## Motivation

[`eggNOG-mapper`](https://github.com/eggnogdb/eggnog-mapper) 🤝 [`KEGG-Decoder`](https://github.com/bjtully/BioData/blob/master/KEGGDecoder/README.md)

- `eggNOG-mapper` is a beautiful tool for fast functional annotation of novel sequences. Yet it does not provide any visualization functions.
- `KEGG-Decoder` is a perfect tool for visualizing KEGG Pathways. But it takes only KEGG-Koala outputs (including blastKOALA, ghostKOALA, KOFAMSCAN).
- `KEGG-Koala` is a web-tool which can work for more than 24 hours. `eggNOG-mapper` can be installed locally on your PC / server and work faster.
- This tool `KEGGaNOG` makes `eggNOG-mapper` meet `KEGG-Decoder`! It will parse `eggNOG-mapper` output, make it fit for the input to `KEGG-Decoder` and then visualize KEGG Pathways as the heatmap!
- **Pro-tip:** `eggNOG-mapper` and `KEGGaNOG` could be wrapped into 🐍 `Snakemake` pipeline to make metabolic profiling a "one-click" process!

## Installation

`KEGG-Decoder` is hardwired into `KEGGaNOG`<br>
`KEGG-Decoder` uses `python=3.6`<br>
That's `KEGGaNOG` uses this version too

```bash
conda create -n kegganog python=3.6
conda activate kegganog
pip install kegganog
```

## Usage Guide

🔗 Visit [KEGGaNOG wiki](https://github.com/iliapopov17/KEGGaNOG/wiki) page

## Contributing
Contributions are welcome! If you have any ideas, bug fixes, or enhancements, feel free to open an issue or submit a pull request.

## Contact
For any inquiries or support, feel free to contact me via [email](mailto:iljapopov17@gmail.com)

Happy functional annotation! 💻🧬
