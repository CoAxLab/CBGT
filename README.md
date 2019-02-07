# CBGT

This repository contains code for implementing the spiking cortico-basal ganglia-thalamus (CBGT) network and drift-diffusion model (DDM) fits described in the manuscript [**Reward-driven changes in striatal pathway competition shape evidence evaluation in decision-making**](https://www.biorxiv.org/content/10.1101/418756v2.abstract). 

The code requires several dependencies to be installed (see below for instructions). After completing the installation procedure below, the demo notebook can be downloaded and opened inside Jupyter.



#### Requirements

- OSX or Linux
- Anaconda with Python 3.* (for [**OSX**](https://www.anaconda.com/download/#macos), [**Linux**](https://www.anaconda.com/download/#linux))

- `gcc` (if Linux) or `gcc-8` (if OSX, see [**here**](https://solarianprogrammer.com/2017/05/21/compiling-gcc-macos/))



#### Installation Instructions

```sh
# create a new conda environment with python 3.6
# and hit 'y' to verify the install 
conda create -n cbgt_env python=3.6 anaconda ipykernel

# activate 'cbgt_env' environment
source activate cbgt_env

# use conda (not pip) to install pymc
conda install pymc=2.3.6 --no-deps

# install hddm and kabuki
pip install --upgrade kabuki hddm

# finally install numpy version 1.11.3
# (avoids hddm incompatibility with later numpy)
pip install numpy==1.11.3

# install cbgt package
pip install -U cbgt --no-cache-dir
```

* After installing everything, run `jupyter notebook` in your terminal to start Jupyter in your browser 
* Drag/drop the demo notebook (`CBGT_PLOSCompBio2019_Demo.ipynb`) into the Jupyter browser window



#### Miscellaneous:

* HDDM resources: ([**methods paper**](https://www.frontiersin.org/articles/10.3389/fninf.2013.00014/full), [**demo**](http://ski.clps.brown.edu/hddm_docs/tutorial_python.html), [**how-to**](http://ski.clps.brown.edu/hddm_docs/howto.html))
* Jupyter Notebook [**tutorial**](https://medium.com/codingthesmartway-com-blog/getting-started-with-jupyter-notebook-for-python-4e7082bd5d46) 

