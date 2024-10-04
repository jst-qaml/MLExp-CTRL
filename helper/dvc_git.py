"""
all helper about create/pull/clone/commit to the git
"""

from git import Repo
from typing import List, Optional
from pathlib import Path
from .utils import dict2yaml, ANY_DICT
from . import types

class DvcGit:
    @staticmethod
    def create(temp_dir: Path, config: types.CreateExperimentParams):
        Repo.init(temp_dir)
        Repo(temp_dir).create_remote('origin', config.dvc_repo.git_url())
        (temp_dir / 'config').mkdir(exist_ok=True)
        (temp_dir / 'config' / 'repo.json').write_text(config.model_dump_json(indent=2))
        return DvcGit(temp_dir)
    
    @staticmethod
    def clone(temp_dir: Path, config: types.DvcRepo):
        Repo.clone_from(config.git_url(), temp_dir)
        return DvcGit(temp_dir)
    
    def __init__(self, temp_dir: Path, shorten_commit_hash = True):
        self.repo = Repo(temp_dir)
        self._shorten_commit_hash = shorten_commit_hash

    def inital_commit(self):
        self.push('initial commit', ['config/repo.json', '.dvc/config'])
    
    # def setup_dvc_resource(self, params: types.SetupDvcResourceBody):
    #     repo_dir = Path(self.repo.working_dir)
    #     (repo_dir / 'dvc.yaml').write_text(dict2yaml(params.dvcYaml))
    #     self.push('setup dvc', ['dvc.yaml'])

    # def setup_hyperparams_resource(self, params: types.SetupHyperparamsResourceBody):
    #     repo_dir = Path(self.repo.working_dir)
    #     (repo_dir / 'inputs').mkdir(exist_ok=True)
    #     (repo_dir / 'inputs' / 'hyperparams.yaml').write_text(dict2yaml(params.hyperparams))
    #     self.push('setup hyperparams', ['inputs/hyperparams.yaml'])
    
    def setup_file(self, filepath: str, contents: ANY_DICT):
        repo_dir = Path(self.repo.working_dir)
        target_dir = repo_dir / filepath
        assert str(target_dir.resolve()).startswith(str(repo_dir.resolve()))
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        target_dir.write_text(dict2yaml(contents))
        self.push(f'setup {filepath}', [filepath])

    def push(self, commit_name: str, filenames: List[str] = []):
        self.repo.index.add(filenames)
        self.repo.index.commit(commit_name)
        self.repo.remote().push(self.current_branch_name()).raise_if_error()
    
    # def view_repository(self, max_commit: int):
    #     commits = [
    #         types.CommitMetadata(
    #             commit_hash=self.shorten_hash(commit.hexsha),
    #             commit_time=str(commit.committed_datetime),
    #             author_name=commit.author.name,
    #             message=commit.message
    #         )
    #         for commit in self.repo.iter_commits(self.current_branch_name(), max_count=max_commit)
    #     ]
    #     branches = [
    #         types.BranchMetadata(
    #             branch_name=branch.name,
    #             commit_hash=self.shorten_hash(branch.commit.hexsha),
    #             commit_time=str(branch.commit.committed_datetime)
    #         )
    #         for branch in self.repo.branches
    #     ]
    #     tags = [
    #         types.TagMetadata(
    #             tag_name=tag.name,
    #             commit_hash=self.shorten_hash(tag.commit.hexsha),
    #             commit_time=str(tag.commit.committed_datetime),
    #             tag_message=tag.tag.message if tag.tag else ''
    #         )
    #         for tag in self.repo.tags
    #     ]
    #     return types.ViewExperimentResponse(
    #         recent_commits=commits,
    #         branches=branches,
    #         tags=tags
    #     )

    # def add_tag(self, body: types.AddTagParams):
    #     self.repo.remote().fetch()
    #     tag = self.repo.create_tag(body.tag_name, body.commit_hash, body.message)
    #     self.repo.remote().push(tag)

    # def create_branch(self, body: types.CreateBranchBody):
    #     commit = None
    #     if body.branch_name:
    #         for branch in self.repo.branches:
    #             if branch.name == body.branch_name:
    #                 commit = branch.commit
    #     if body.tag_name:
    #         for tag in self.repo.tags:
    #             if tag.name == body.tag_name:
    #                 commit = tag.name
    #     if body.commit_hash:
    #         commit = self.repo.commit(body.commit_hash)
    #     assert commit
    #     self.repo.create_head(body.new_branch_name, commit)
    #     self.repo.remote().push(body.new_branch_name)
       
    def shorten_hash(self, commit_hash: str):
        return commit_hash[:7] if self._shorten_commit_hash else commit_hash

    def current_branch_name(self) -> Optional[str]:
        head = self.repo.head.commit
        branches = [branch.name for branch in self.repo.branches if branch.commit == head]
        assert len(branches) <= 1
        return branches[0]
