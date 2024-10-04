from .dvc_git import DvcGit
from .dvc_minio import DvcMinio
from .k8s_stub import K8sStub
from .utils import TempDirectoryManager, ANY_DICT
from . import types
from . import kubectl 

# All the functions in this file correspond one-to-one to the commands in fastapi and click.
# The docstrings of each function serve as their documentation.


def create_experiment(
    params: types.CreateExperimentParams,
    dvcYaml: ANY_DICT,
    hyperparams: str | None
):
    """Create repository to store inputs/outputs"""
    with TempDirectoryManager() as temp_dir:
        git_vcs = DvcGit.create(temp_dir, params)
        DvcMinio(temp_dir, params.bucket).init()
        git_vcs.inital_commit()
        git_vcs.setup_file('dvc.yaml', dvcYaml)
        if hyperparams:
            git_vcs.setup_file('inputs/hyperparams.yaml', hyperparams)
    return types.SimpleResponse(message='created')


def create_k8s_resource(params: types.CreateK8sResourceBody):
    """Create/Apply a configuration to a k8s resource"""
    kubectl.apply_internal(params.kube_deploy_spec)
    return types.SimpleResponse(message='created')


# def create_hyperparams_resource(params: types.CreateHyperparamsResourceParams):
#     """Create/Update hyperparameter file"""
#     with TempDirectoryManager() as temp_dir:
#         git_vcs = DvcGit.clone(temp_dir, params.git)
#         git_vcs.setup_file('inputs/hyperparams.yaml', params.hyperparams)
#     return types.SimpleResponse(message='created')


def run_experiment(params: types.RunExperimentParams):
    """Run an experiment by syncing, updating hyperparameters, and executing in Kubernetes"""
    # K8sStub(params.git)
    kubectl.exec_internal(
        params.resource,
        params.namespace,
        ('/bin/bash', '-c', K8sStub.command(params.dvc_repo)),
    )
    return types.SimpleResponse(message='ran')


# def add_tag(params: types.AddTagParams):
#     """Add a tag to a specific experiment version in the version control system"""
#     with TempDirectoryManager() as temp_dir:
#         git_vcs = DvcGit.clone(temp_dir, params.git)
#         git_vcs.add_tag(params)
#     return types.SimpleResponse(message='added')


# def view_experiment(params: types.ViewExperimentParams):
#     """View details of a specific experiment, including recent commits, branches, and tags"""
#     with TempDirectoryManager() as temp_dir:
#         vcs_git = DvcGit.clone(temp_dir, params.git)
#         return vcs_git.view_repository(params.max_commit)
