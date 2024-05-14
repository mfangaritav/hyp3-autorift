
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10871107.svg)](https://doi.org/10.5281/zenodo.10871107) ![Coverage](images/coverage.svg)

# HyP3 autoRIFT Plugin

The HyP3-autoRIFT plugin provides a set of workflows to get dense feature tracking between two images with the [autonomous Repeat Image Feature Tracking](https://github.com/nasa-jpl/autoRIFT) (autoRIFT) software package. This plugin is part of the [Alaska Satellite Facility's](https://asf.alaska.edu) larger HyP3 (Hybrid Plugin Processing Pipeline) system, which is a batch processing pipeline designed for on-demand processing of optical and SAR data.

## Usage
The HyP3-autoRIFT plugin provides a set of workflows (accessible directly in Python or via a CLI) that can be used to process SAR or optical data using autoRIFT. The workflows currently included in this plugin are:

- `hyp3_autorift`: A workflow to get dense feature tracking between two images using autoRIFT
- `s1_correction`: A workflow for geogriding Sentinel-1 images using ISCE2's processing workflow 
---

To run a workflow, simply run `python -m hyp3_autorift ++process [WORKFLOW_NAME] [WORKFLOW_ARGS]`. For example, to run the `s1_correction` workflow:

```
python -m hyp3_autorift ++process s1_correction \
  "S1A_IW_SLC__1SSH_20170221T204710_20170221T204737_015387_0193F6_AB07" \
```

This command will geogrid a Sentinel-1 image in Greenland. 

### Options
To learn about the arguments for each workflow, look at the help documentation 
(`python -m hyp3_autorift ++process [WORKFLOW_NAME] --help`).

### Earthdata Login and ESA Credentials

For all workflows, the user must provide their Earthdata Login credentials and ESA Copernicus Data Space Ecosystem (CDSE) credentials in order to download input data.
If you do not already have an Earthdata account, you can sign up [here](https://urs.earthdata.nasa.gov/home). 
If you do not already have a CDSE account, you can sign up [here](https://dataspace.copernicus.eu). 
Your credentials can be passed to the workflows via command-line options (`--esa-username` and  `--esa-password`), environment variables 
(`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`, `ESA_USERNAME`, and `ESA_PASSWORD`), or via your `.netrc` file. If you haven't set up a `.netrc` file 
before, check out this [guide](https://harmony.earthdata.nasa.gov/docs#getting-started) to get started.

### Docker Container
The ultimate goal of this project is to create a docker container that can run autoRIFT workflows within a HyP3 
deployment. To run the current version of the project's container, use this command:
```
docker run -it --rm \
    -e EARTHDATA_USERNAME=[YOUR_USERNAME_HERE] \
    -e EARTHDATA_PASSWORD=[YOUR_PASSWORD_HERE] \
    -e ESA_USERNAME=[YOUR_USERNAME_HERE] \
    -e ESA_PASSWORD=[YOUR_PASSWORD_HERE] \
    ghcr.io/asfhyp3/hyp3-autorift:latest \
    ++process [WORKFLOW_NAME] \
    [WORKFLOW_ARGS]
```

**NOTE** Each workflow can also be accessed via an alternative CLI with the format (`[WORKFLOW_NAME] [WORKFLOW_ARGS]`)

#### Docker Outputs

To retain hyp3_autorift output files running via Docker there are two recommended approaches:

1. Use a volume mount

Add the `-w /tmp -v [localdir]:/tmp` flags after docker run. `-w` changes the working directory of the container to `/tmp` and `-v` will mount whichever local directory you choose so that such that hyp3_autorift outputs are preserved locally.

1. Copy outputs to remote object storage

Append the `--bucket` and `--bucket-prefix` to [WORKFLOW_ARGS]. *Only the final output files and zipped archive of those files is uploaded.* This also requires that AWS credentials to write to the bucket are available to the running container. For example, to write outputs to a hypothetical bucket `s3://hypothetical-bucket/test-run/`:

```
docker run -it --rm \
    -e AWS_ACCESS_KEY_ID=[YOUR_KEY] \
    -e AWS_SECRET_ACCESS_KEY=[YOUR_SECRET] \ 
    -e AWS_SESSION_TOKEN=[YOUR_TOKEN] \ 
    -e EARTHDATA_USERNAME=[YOUR_USERNAME_HERE] \
    -e EARTHDATA_PASSWORD=[YOUR_PASSWORD_HERE] \
    -e ESA_USERNAME=[YOUR_USERNAME_HERE] \
    -e ESA_PASSWORD=[YOUR_PASSWORD_HERE] \
    ghcr.io/asfhyp3/hyp3-isce2:latest \
      ++process [WORKFLOW_NAME] \
      [WORKFLOW_ARGS] \
      --bucket "hypothetical-bucket" \
      --bucket-prefix "test-run"
```

Tip: you can use [`docker run --env-file`](https://docs.docker.com/reference/cli/docker/container/run/#env) to capture all the necessary environment variables in a single file.


## Developer Setup
1. Ensure that conda is installed on your system (we recommend using [mambaforge](https://github.com/conda-forge/miniforge#mambaforge) to reduce setup times).
2. Download a local version of the `hyp3-autorift` repository (`git clone https://github.com/ASFHyP3/hyp3-autorift.git`)
3. In the base directory for this project call `mamba env create -f environment.yml` to create your Python environment, then activate it (`mamba activate hyp3-autorift`)
4. Finally, install a development version of the package (`python -m pip install -e .`)

To run all commands in sequence use:
```bash
git clone https://github.com/ASFHyP3/hyp3-autorift.git
cd hyp3-autorift
mamba env create -f environment.yml
mamba activate hyp3-autorift
python -m pip install -e .
```

## Background
HyP3 is broken into two components: the cloud architecture/API that manage processing of HyP3 workflows, and Docker container plugins that contain scientific workflows which produce new science products from a variety of data sources (see figure below for the full HyP3 architecture).

![Cloud Architecture](images/arch_here.jpg)

The cloud infratstructure-as-code for HyP3 can be found in the main [HyP3 repository](https://github.com/asfhyp3/hyp3). This repository contains a plugin that can be used to process ISCE2-based processing of SAR data.

This project was heavily influenced by the [DockerizedTopsApp](https://github.com/ACCESS-Cloud-Based-InSAR/DockerizedTopsApp) project, which contains a similar workflow that is designed to produce ARIA Sentinel-1 Geocoded Unwrapped Interferogram standard products via HyP3.

## License
The HyP3-autoRIFT plugin is licensed under the Apache License, Version 2 license. See the LICENSE file for more details.

## Code of conduct
We strive to create a welcoming and inclusive community for all contributors to HyP3-ISCE2. As such, all contributors to this project are expected to adhere to our code of conduct.

Please see `CODE_OF_CONDUCT.md` for the full code of conduct text.

## Contributing
Contributions to the HyP3-autoRIFT plugin are welcome! If you would like to contribute, please submit a pull request on the GitHub repository.

## Contact Us
Want to talk about HyP3-autoRIFT? We would love to hear from you!

Found a bug? Want to request a feature?
[open an issue](https://github.com/ASFHyP3/asf_tools/issues/new)

General questions? Suggestions? Or just want to talk to the team?
[chat with us on gitter](https://gitter.im/ASFHyP3/community)
