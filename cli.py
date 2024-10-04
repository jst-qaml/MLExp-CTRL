import click
import yaml
from pathlib import Path
from tabulate import tabulate
import helper
import json

@click.group()
def cli():
    """Experiment Management Interface"""
    pass


@cli.command(help=helper.create_experiment.__doc__)
@click.argument('repo_json', type=click.Path(exists=True))
@click.argument('dvc_yaml_file', type=click.Path(exists=True))
@click.argument('hyperparams_file', type=click.Path(exists=True), required=False, default=None)
def create_experiment(repo_json, dvc_yaml_file, hyperparams_file):
    params = helper.CreateExperimentParams(
        **json.loads(Path(repo_json).read_text()),
    )
    dvcYaml=Path(dvc_yaml_file).read_text()
    hyperparams=Path(dvc_yaml_file).read_text() if hyperparams_file else None
    click.echo(helper.create_experiment(params, dvcYaml, hyperparams))


@cli.command(help=helper.create_k8s_resource.__doc__)
@click.argument('kube_deploy_spec_file', type=click.Path(exists=True))
def create_k8s_resource(kube_deploy_spec_file):
    params = helper.CreateK8sResourceBody(
        kube_deploy_spec=yaml.safe_load(Path(kube_deploy_spec_file).open('r'))
    )
    click.echo(helper.create_k8s_resource(params))


# @cli.command(help=helper.create_hyperparams_resource.__doc__)
# @click.argument('config_file', type=click.Path(exists=True))
# def create_hyperparams_resource(config_file, hyperparams_file):
#     params = helper.CreateHyperparamsResourceParams(
#         **yaml.safe_load(Path(config_file).open('r')),
#         hyperparams=Path(hyperparams_file).read_text()
#     )
#     click.echo(helper.create_hyperparams_resource(params))


@cli.command(help=helper.run_experiment.__doc__)
@click.argument('repo_json', type=click.Path(exists=True))
@click.argument('resource')
@click.argument('namespace')
def run_experiment(repo_json, resource, namespace):
    params = helper.RunExperimentParams(
        **json.loads(Path(repo_json).read_text()),
        resource=resource,
        namespace=namespace
    )
    click.echo(helper.run_experiment(params))


# @cli.command(help=helper.add_tag.__doc__)
# @click.argument('config_file', type=click.Path(exists=True))
# def add_tag(config_file):
#     params = helper.AddTagParams(
#         **yaml.safe_load(Path(config_file).open('r'))
#     )
#     click.echo(helper.add_tag(params))


# @cli.command(help=helper.view_experiment.__doc__)
# @click.argument('config_file', type=click.Path(exists=True))
# def view_experiment(config_file):
#     params = helper.ViewExperimentParams(
#         **yaml.safe_load(Path(config_file).open('r'))
#     )
#     response = helper.view_experiment(params)
#     for key, value in response.model_dump().items():
#         table = tabulate(value, headers="keys", tablefmt="grid")
#         click.echo('\n' + '=' * 40)
#         click.echo(key)
#         click.echo(table)


if __name__ == '__main__':
    cli()
