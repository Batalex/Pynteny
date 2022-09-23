![logo](assets/logo.png)
<br>

# Synteny-aware hmm searches made easy

![GitHub release (latest by date)](https://img.shields.io/github/v/release/Robaina/pynteny)
![license](https://img.shields.io/github/license/Robaina/Pynteny)
![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4)
[![DOI](https://zenodo.org/badge/500470783.svg)](https://zenodo.org/badge/latestdoi/500470783)

## What is Pynteny?

Pynteny is a command-line tool to search for [synteny](https://en.wikipedia.org/wiki/Synteny) blocks in (assembled) sequence data through [HMMs](https://www.bioinformatics.org/wiki/Hidden_Markov_Model) of the ORFs of interest and [HMMER](http://hmmer.janelia.org/).

## Installation

Download (or fork) repo to local directory:

```bash
git clone https://github.com/Robaina/Pynteny.git
```

cd to downloaded repo and install conda enviroment:

```bash
cd Pynteny
conda env create -f environment.yml
```

Install pynteny in conda enviroment:

```bash
conda activate pynteny
python setup.py install
```

Check that installation worked fine:

```bash
pynteny tests
```

## Usage

Pynteny currently contains these subcommands:

* `pynteny search`: searches for synteny blocks in a set of ORFs using HMMER and outputs the results in a tabular format. Synteny blocks are specified by strings of ordered HMM names or gene IDs with the following format:
$$\lt HMM_a \space n_{ab} \space \lt HMM_b \space n_{bc} \space \lt(HMM_{c1}|HMM_{c2}|HMM_{c3}),$$ 

    where $n_{ab}$ corrresponds to the maximum number of genes between $HMM_a$ and $HMM_b$. Results can be strand-specific, in that case $>$ preceding a HMM name indicates that the corresponding ORF must be located in the positive (or sense) strand. Likewise, a $<$ symbol indicates that the ORF must be located in the negative (antisense) strand. Searches can be made strand-insensitive by omitting the $>$ or $<$ symbol. 

    Several HMMs can be assigned to the same ORF, in which case the search is performed for all of them. In this case, HMM names must be separated by "|" and grouped within parentheses, as shown above.

    If the PGAP database is employed (see `pynteny download` below), synteny blocks can also be specified by gene symbols, such as $$\lt leuD \space 0 \space \lt leuC \space 1 \space \lt leuA.$$ In that case, the program will try to match gene symbols to HMM names in the PGAP database previous to running the search.

* `pynteny build`: predict ORFs with [prodigal]()and add positional information to each ORF &mdash; i.e., loci and gene number within assembled contig. Alternatively, the user can provide their own ORF annotations in GenBank format.
* `pynteny download`: downloads the latest version of the [NCBI Prokaryotic Genome Annotation Pipeline](https://github.com/ncbi/pgap) (PGAP) HMM database. However, the user may provide their own HMM database.

## Graphical interface

Pynteny may be run from within a graphical interface made with [Streamlit](https://streamlit.io). The app is run on a local server in your machine, thus all files are kept locally and the app can run without an internet connection. 

To run the app, execute the following command once pyteny has been successfully installed:

```bash
conda activate pynteny
pynteny app
```

![pynyeny-gif](assets/pynteny_1.gif)

## Citation

If you use this software, please cite it as below:

Semidán Robaina Estévez. (2022). Pynteny: synteny-aware hmm searches made easy (Version 0.0.1). Zenodo. https://doi.org/10.5281/zenodo.7048685
