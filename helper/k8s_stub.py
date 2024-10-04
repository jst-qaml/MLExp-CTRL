import subprocess
from pathlib import Path
from typing import List
from . import types, kubectl

class K8sStub:
    def __init__(self, config: types.DvcRepo):
        self._exec(['docker', 'build', '-t', 'example_k8s', '.'])
        self._exec(['docker', 'rm', '-f', 'example_k8s'])
        self._exec(['docker', 'run', '-itd', '--rm', '--name', 'example_k8s', 'example_k8s'])
        self._exec(['docker', 'exec', '-it', 'example_k8s', '/bin/bash', '-c', K8sStub.command(config)])

    def _exec(self, args: List[str]):
        subprocess.run(args, check=True, cwd=Path.cwd())
    
    @staticmethod
    def command(config: types.DvcRepo):
        # TODO: caution the security (only for initial implementation)
        commands = [
            # located directly under the home directory (inside the container)
            f'git clone {config.git_url()}',
            f'cd {config.name}',
            'git config user.name "Pipeline"',
            'git config user.email "pipeline@example.com"',
            'dvc repro',
            'dvc push',
            'git commit -m "execute - dvc repro"',
            'git push',
            'cd ../',
            f'rm -rf {config.name}',
        ]
        return ' && '.join(commands)
