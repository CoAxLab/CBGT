# bgNetwork

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
conda create -n py36 python=3.6 anaconda

# activate 'py36' environment
source activate py36

# use conda (not pip) to install pymc
conda install pymc=2.3.6 --no-deps

# install hddm and kabuki
pip install --upgrade kabuki hddm

# Alternative Install: (not recommended) 
# conda install -c pymc hddm

# finally install numpy version 1.11.3
# (avoids hddm incompatibility with later numpy)
pip install numpy==1.11.3
```

* After installing everything, run the line below to open up Jupyter in your browser, then drag/drop the demo notebook (`CBGT_PLOSCompBio2019_Demo.ipynb`) into the Jupyter browser window (see [**this tutorial**](https://medium.com/codingthesmartway-com-blog/getting-started-with-jupyter-notebook-for-python-4e7082bd5d46) if you're new to Jupyter)

```sh
# make sure you've activated the py36 env first
jupyter notebook
```



#### HDDM Resources:

- For those interested in working more with HDDM, see the [**methods paper here**](https://www.frontiersin.org/articles/10.3389/fninf.2013.00014/full) as well as the introductory [**demo**](http://ski.clps.brown.edu/hddm_docs/tutorial_python.html) and [**how-to**](http://ski.clps.brown.edu/hddm_docs/howto.html) sections

