import os
import json
import click
from kubernetes import client, config, dynamic, stream
from kubernetes.client import api_client
from kubernetes.client.rest import ApiException
import yaml

# Load Cluster Configuration
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '../config/k8s-config.json')

with open(CONFIG_FILE_PATH, 'r') as config_file:
    config_data = json.load(config_file)

KUBECONFIG_PATH = os.path.join(os.path.dirname(__file__), '../', config_data['KUBECONFIG_PATH'])
ALLOWED_NAMESPACES = config_data['ALLOWED_NAMESPACES']
PROHIBITED_NAMESPACES = config_data['PROHIBITED_NAMESPACES']

# Load kubeconfig
config.load_kube_config(KUBECONFIG_PATH)
dyn_client = dynamic.DynamicClient(api_client.ApiClient())

# Resource short names mapping
RESOURCE_SHORT_NAMES = {
    'po': 'pods',
    'svc': 'services',
    'deploy': 'deployments',
    'no': 'nodes',
    'ns': 'namespaces',
    'ing': 'ingresses',
    'cm': 'configmaps',
    'secret': 'secrets',
    'pv': 'persistentvolumes',
    'pvc': 'persistentvolumeclaims',
    'sa': 'serviceaccounts',
    'ds': 'daemonsets',
    'rs': 'replicasets',
    'sts': 'statefulsets',
    'hpa': 'horizontalpodautoscalers',
    'netpol': 'networkpolicies',
    'sc': 'storageclasses',
    'crd': 'customresourcedefinitions',
    'ep': 'endpoints',
    'ev': 'events',
    'hpa': 'horizontalpodautoscalers',
    'job': 'jobs',
    'cj': 'cronjobs',
    'limits': 'limitranges',
    'quota': 'resourcequotas',
    'pdb': 'poddisruptionbudgets',
    'pc': 'priorityclasses',
}

# To Do: Implement resource shortname using propper method
# def get_resource_short_names():
#     """Fetch Kubernetes API resources and their short names."""
#     resource_short_names = {}

#     api_resources = dyn_client.resources.get()
#     for resource in api_resources.resources:
#         if hasattr(resource, 'short_names') and resource.short_names:
#             for short_name in resource.short_names:
#                 resource_short_names[short_name] = resource.kind.lower() + 's'

#     return resource_short_names

# # Fetch and print the resource short names
# RESOURCE_SHORT_NAMES = get_resource_short_names()
# # print("Resource Short Names:", RESOURCE_SHORT_NAMES)


# # API versions for different resource types
# API_VERSIONS = {
#     'pods': 'v1',
#     'services': 'v1',
#     'deployments': 'apps/v1',
#     'namespaces': 'v1',
# }

def namespace_guard(namespace):
    """Check if the namespace is allowed and not prohibited."""
    if namespace in PROHIBITED_NAMESPACES:
        raise click.ClickException(f"Actions in the '{namespace}' namespace are prohibited.")
    if ALLOWED_NAMESPACES and namespace not in ALLOWED_NAMESPACES:
        raise click.ClickException(f"The namespace '{namespace}' is not in the allowed list.")

# K8S API Helper Function

def get_resource_type(resource_type):
    """Resolve short names to full resource names."""
    return RESOURCE_SHORT_NAMES.get(resource_type, resource_type)

def get_api_resource(resource_type):
    """Get the API resource for a given resource type."""
    try:
        camel_case_resources = {
        "networkpolicies": "NetworkPolicies",
        "statefulsets": "StatefulSets",
        "daemonsets": "DaemonSets",
        "deployments": "Deployments",
        "replicasets": "ReplicaSets",
        "cronjobs": "CronJobs",
        "ingresses": "Ingresses",
        "services": "Services",
        "configmaps": "ConfigMaps",
        "persistentvolumeclaims": "PersistentVolumeClaims",
        "persistentvolumes": "PersistentVolumes",
        "poddisruptionbudgets": "PodDisruptionBudgets",
        "horizontalpodautoscalers": "HorizontalPodAutoscalers",
        }

        # Resolving resource name
        if resource_type in camel_case_resources:
            kind = singularize(camel_case_resources[resource_type])
        else:
            kind = singularize(resource_type).capitalize()
        
        # Search for the resource by kind
        resources = dyn_client.resources.search(kind=kind) 
        if not resources:
            raise dynamic.exceptions.ResourceNotFoundError(f"No resources found for kind: {kind}")

        # Use the first found resource
        api_resource = resources[0]
        # print(f"Debug resource_type: {resource_type}, kind: {kind}, api_version: {api_resource.group_version}")
        return api_resource

    except dynamic.exceptions.ResourceNotFoundError as e:
        raise click.ClickException(f"Resource type '{resource_type}' not found. Error: {str(e)}")


# def get_pod_name(resource):
#     """Get a running pod name from the resource"""
#     if resource['kind'].lower() == 'pod':
#         return resource['metadata']['name']
    
#     # For deployments, statefulsets, etc.
#     if 'spec' in resource and 'selector' in resource['spec']:
#         label_selector = ','.join([f"{k}={v}" for k, v in resource['spec']['selector']['matchLabels'].items()])
#         api = client.CoreV1Api()
#         pods = api.list_namespaced_pod(namespace=resource['metadata']['namespace'], label_selector=label_selector)
#         running_pods = [pod for pod in pods.items if pod.status.phase == 'Running']
#         if running_pods:
#             return random.choice(running_pods).metadata.name
    
#     return None

# Trivial Helper Function 
def singularize(resource_type):
    """Convert resource type to singular form."""
    if resource_type.endswith('ies'):
        return resource_type[:-3] + 'y'
    elif resource_type.endswith('ses'):
        return resource_type[:-2]
    elif resource_type.endswith('s'):
        return resource_type[:-1]
    return resource_type

def format_output(resource, output_format):
    if output_format == 'json':
        return json.dumps(client.ApiClient().sanitize_for_serialization(resource), indent=2)
    elif output_format == 'yaml':
        return yaml.dump(client.ApiClient().sanitize_for_serialization(resource))
    else:
        return f"{resource['kind']}: {resource['metadata']['name']}"

# Interface
@click.group()
def cli():
    """Kubernetes CLI Tool for Kubernetes Operations"""
    pass

# Main Kubectl modules
@cli.command()
@click.argument('resource_type')
@click.option('--namespace', '-n', default='default', help='Namespace of resource')
# @click.option('--name', '-r', help='Name of the resource')
@click.option('--output', '-o', help='Output format')
def get(resource_type, namespace, output):
    """Get Kubernetes resources"""
    namespace_guard(namespace)
    resource_type = get_resource_type(resource_type)
    api_resource = get_api_resource(resource_type)
    try:    
        resources = api_resource.get(namespace=namespace)
        for resource in resources.items:
            click.echo(format_output(resource, output))
    except ApiException as e:
        click.echo(f"Error: {e.reason}")

@cli.command()
@click.option('--filename', '-f', required=True, help='YAML file path relative to project root or just filename')
def apply(filename):
    """Apply a configuration to a resource by filename"""
    # Path management
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.sep not in filename:
        full_path = os.path.join(project_root, filename)
    else:
        full_path = os.path.join(project_root, filename)
    
    if not os.path.exists(full_path): # Check config file existence
        click.echo(f"Error: File not found: {full_path}")
        return

    with open(full_path, 'r') as f:
        resource_def = yaml.safe_load(f)

    apply_internal(resource_def)

def apply_internal(resource_def):
    api_resource = get_api_resource(resource_def['kind'].lower() + 's')
    namespace = resource_def['metadata'].get('namespace', 'default')
    namespace_guard(namespace)

    try:
        existing_resource = api_resource.get(name=resource_def['metadata']['name'], namespace=namespace)
        api_resource.patch(body=resource_def, name=resource_def['metadata']['name'], namespace=namespace)
        click.echo(f"Resource {resource_def['kind']} '{resource_def['metadata']['name']}' updated.")
    except ApiException as e:
        if e.status == 404:
            api_resource.create(body=resource_def, namespace=namespace)
            click.echo(f"Resource {resource_def['kind']} '{resource_def['metadata']['name']}' created.")
        else:
            click.echo(f"Error: {e.reason}")

def get_pod_name(resource):
    """Get a running pod name from the resource"""
    if resource.kind.lower() == 'pod':
        return resource.metadata.name
    
    # For deployments, statefulsets, etc.
    if hasattr(resource.spec, 'selector') and hasattr(resource.spec.selector, 'match_labels'):
        # print(f"selector is {resource.spec.selector.matchLabels}")
        label_selector = ','.join([f"{k}={v}" for k, v in resource.spec.selector.matchLabels.items()])
        api = client.CoreV1Api()
        try:
            pods = api.list_namespaced_pod(namespace=resource.metadata.namespace, label_selector=label_selector)
            if pods.items:
                for pod in pods.items:
                    if pod.status.phase == 'Running':
                        return pod.metadata.name
        except ApiException as e:
            click.echo(f"Error listing pods: {e.reason}")
    
    return None

@cli.command()
@click.argument('resource')
@click.option('--namespace', '-n', default='default', help='Namespace of the resource')
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def exec(resource, namespace, command):
    """Execute a command in a running pod of the specified resource"""
    try:
        cmd_index = command.index('--')
        command = command[cmd_index + 1:]
    except ValueError:
        pass  # No '--' found, use the entire command
    exec_internal(resource, namespace, command)


def exec_internal(resource, namespace, command):
    namespace_guard(namespace)

    if '/' in resource: # check resource type
        resource_type, resource_name = resource.split('/')
        resource_type = get_resource_type(resource_type)
    else:
        resource_type = 'pods'
        resource_name = resource

    try:
        api_resource = get_api_resource(resource_type)
        resource_obj = api_resource.get(name=resource_name, namespace=namespace)
        
        pod_name = get_pod_name(resource_obj)
        if not pod_name:
            click.echo(f"No running pods found for {resource_type} '{resource_name}'")
            return

        api = client.CoreV1Api()
        resp = stream.stream(
            api.connect_get_namespaced_pod_exec,
            pod_name,
            namespace,
            command=list(command),
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False
        )
        click.echo(resp)
    except ApiException as e:
        click.echo(f"Error: {e.reason}")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    cli()
