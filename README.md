# MLExp CTRL Framework

This project provides a framework for setting up, managing, and running machine learning experiments. Below you'll find detailed instructions on how to set up the framework, operate it, and perform sample runs.

## Framework Prerequisites

Before setting up `mlexp-ctrl`, ensure you have the following installed on your system:

- Git: Version control system
- Conda: Package, dependency, and environment management
- Python: Version compatible with your environment

Additionally, ensure you have access to the following systems:

- Version Control Systems: Access to GitHub, GitLab, or similar platforms
- Object Storage System: A solution such as Amazon S3 or an APi-compatible platform like MinIO can be used.
- Kubernetes: Any distribution is supported, this framework is primarily tested with the RKE2 variant.

## Setup Guide

Follow these steps to set up the `mlexp-ctrl` framework:

1. Clone this Repository

```bash
git clone /url/to/mlexp-ctrl
```

2. Copy Configuration Templates

```bash
cd mlexp-ctrl
cp -r config.templ/ config
```

3. Configure YAML Files
Ensure the following configuration files are properly set up:
- `config/kubeconfig.yaml`: Import config from your K8S cluster, and ensure proper access permission has been configured.
- `config/k8s-config.yaml`: Annotate path of kubeconfig (can be changed to switching between K8S cluster), listed up prohibited and allowed namespace for this FW to interact with.

4. Create & Activate Conda Environment

```bash
conda env create -f ./sys-env/mlexp-ctrl-env.yaml
conda activate mlx
```

5. Run the API Server

```bash
uvicorn api:app --reload
```

## Operational Guide
There are three endpoints to interact with this Framework, via CLI, for testing purposes and API for deployment purposes.
API documentation can be found in the [Swagger UI](http://127.0.0.1:8000/docs#/)

### 1. Creating an Experiment

Execute `/experiment/create` Endpoint
Provide the following file inputs:
- `repo_json`: Configuration and credentials for resources repository such as Git, DVC Repository, Bucket Storage, and Container Registry.
- `dvc_yaml_file`: DVC pipeline configuration file, annotated with various stages of automatically executing the workload.
- `hyperparams_file`: Hyperparameters for the experiment.

> Sample Files: Located in the `client_ref.templ` or `workload_example` folder.

### 2. Scheduling Kubernetes Resources

Run the `/resource/k8s/create` endpoint to schedule Kubernetes resource specifications.
- The sample environment of the workload can be found in `workload_example/Dockerfile`.
    - The DVC package is pre-installed.
    - Scripts corresponding to `dvc.yaml` are provided for smooth operation.

### 3. Running an Experiment

To run an existing experiment:
Execute `/experiment/run` Endpoint
Provide the following parameters:
- `repo_json`: Please refer to section 1:`/experiment/create`.
- `resource`: K8S-resource that ML workload should be run e.g. `sts/<statefulset-name>`, `deploy/<deployment-name>`
- `namespace`: Kubernetes namespace for the K8S-resource.

### 4. Retrieving Experiment results and artifacts

After the experiment workflow is completed, artifacts should be pushed to the designated experiment repository.
To retrieve the results and artifacts of the experiment to the client side can be done by:

```bash
git clone <exp-repo-url>
cd <exp-repo>
dvc pull
```