# Rolling Process Variation Estimation Using a Monte-Carlo Method

[![DOI](https://zenodo.org/badge/624275351.svg)](https://doi.org/10.5281/zenodo.13960836)

This repository contains the LaTeX sources for the research article *Rolling Process Variation Estimation Using a Monte-Carlo Method* submitted to *steel research international* as well as the supplemental material for this paper.
All data and routines used in the study are included, the data analysis and simulation results can be reproduced using the content of this repository.
To run the procedures here, you need a working installation of Python 3.12 and the project management tool [`hatch`](https://hatch.pypa.io) installed.

First, create a virtual environment using hatch with

```shell
hatch env create
```

Hatch will download all necessary packages and install them locally. Then, you may run all tasks to reproduce the study data and document by

```shell
hatch run pytask
```