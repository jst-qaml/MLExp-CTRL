from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from git.exc import GitCommandError
import helper
import yaml
import json

"""
How to use:
$ uvicorn api:app --reload

Generated Document:
- http://127.0.0.1:8000/docs
"""


app = FastAPI()


@app.post("/experiment/create", description=helper.create_experiment.__doc__)
async def create_experiment(
    repo_json: UploadFile = File(...),
    dvc_yaml_file: UploadFile = File(...),
    hyperparams_file: UploadFile = File(...)
) -> helper.SimpleResponse:
    params = helper.CreateExperimentParams(
        **(await read_file(repo_json))
    )
    dvcYaml=await read_file(dvc_yaml_file)
    hyperparams=await read_file(hyperparams_file)
    try:
        return helper.create_experiment(params, dvcYaml, hyperparams)
    except GitCommandError:
        raise HTTPException(status_code=400, detail="git push is failed. It may already be created.")


@app.post("/resource/k8s/create", description=helper.create_k8s_resource.__doc__)
async def create_k8s_resource(
    k8s_manifest_file: UploadFile = File(...)
) -> helper.SimpleResponse:
    params = helper.CreateK8sResourceBody(
        kube_deploy_spec=await read_file(k8s_manifest_file)
    )
    return helper.create_k8s_resource(params)


# @app.post("/resource/dvc/pipeline/create", description=helper.create_dvc_pipeline_resource.__doc__)
# async def create_dvc_pipeline(
#     config_file: UploadFile = File(...),
#     dvc_yaml_file: UploadFile = File(...)
# ) -> helper.SimpleResponse:
#     params = helper.CreateDvcPipelineResourceParams(
#         **(await read_file(config_file)),
#         dvcYaml=await read_file(dvc_yaml_file)
#     )
#     return helper.create_dvc_pipeline_resource(params)


# @app.post("/resource/hyperparams/create", description=helper.create_hyperparams_resource.__doc__)
# async def create_hyperparams_resource(
#     config_file: UploadFile = File(...),
#     hyperparams_file: UploadFile = File(...)
# ) -> helper.SimpleResponse:
#     params = helper.CreateHyperparamsResourceParams(
#         **(await read_file(config_file)),
#         hyperparams=await read_file(hyperparams_file)
#     )
#     return helper.create_hyperparams_resource(params)


@app.post("/experiment/run", description=helper.run_experiment.__doc__)
async def run_experiment(
    repo_json: UploadFile = File(...),
    resource: str = Form(...),
    namespace: str = Form(...)
) -> helper.SimpleResponse:
    params = helper.RunExperimentParams(
        **(await read_file(repo_json)),
        resource=resource,
        namespace=namespace
    )
    return helper.run_experiment(params)


# @app.post("/experiment/tag/add", description=helper.add_tag.__doc__)
# async def add_tag(
#     config_file: UploadFile = File(...),
# ) -> helper.SimpleResponse:
#     params = helper.AddTagParams(
#         **(await read_file(config_file)),
#     )
#     return helper.add_tag(params)


# @app.post("/experiment/view", description=helper.view_experiment.__doc__)
# async def view_experiment(
#     config_file: UploadFile = File(...),
# ) -> helper.ViewExperimentResponse:
#     params = helper.ViewExperimentParams(
#         **(await read_file(config_file)),
#     )
#     return helper.view_experiment(params)


async def read_file(file: UploadFile):
    try:
        print(file)
        content = await file.read()
        data = content.decode('utf-8')
        if file.filename.endswith(('.yml', '.yaml')):
            return yaml.safe_load(data)
        if file.filename.endswith('.json'):
            return json.loads(data)
        raise HTTPException(status_code=400, detail="unknown file extension (json/yaml/yml is valid)")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="failed to decode file content")
