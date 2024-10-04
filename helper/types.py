from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, List, Optional

class DvcRepo(BaseModel):
    name: str
    url: str
    username: str
    passkey: str

    def git_url(self):
        return f"http://{self.username}:{self.passkey}@{self.url}/{self.name}.git"

class Bucket(BaseModel):
    name: str
    url: str
    endpointurl: str
    access_key_id: str
    secret_access_key: str
    remote_name: str = Field(default="minio")

class GitRepo(BaseModel):
    name: str
    url: str
    username: str
    passkey: str

class CtRegistry(BaseModel):
    server: str
    username: str
    password: str
    email: str

class CreateExperimentParams(BaseModel):
    dvc_repo: DvcRepo
    bucket: Bucket
    git_repo: GitRepo
    ct_registry: CtRegistry

class CreateK8sResourceBody(BaseModel):
    kube_deploy_spec: Dict[str, Any]

class RunExperimentParams(CreateExperimentParams):
    resource: str
    namespace: str

# class AddTagParams(BaseModel):
#     git: GitConfig
#     commit_hash: str
#     tag_name: str
#     message: Optional[str] = Field(default=None)

# class CreateBranchBody(SyncExperimentBody):
#     new_branch_name: str
#     commit_hash: Optional[str] = Field(default=None)
#     tag_name: Optional[str] = Field(default=None)

#     def pointer(self):
#         pointer = []
#         if self.branch_name:
#             pointer.append(self.branch_name)
#         if self.commit_hash:
#             pointer.append(self.commit_hash)
#         if self.tag_name:
#             pointer.append(self.tag_name)
#         assert len(pointer) == 1, 'only one of branch_name, commit_hash, tag_name can be specified'
#         return pointer[0]

# class ViewExperimentParams(BaseModel):
#     git: GitConfig
#     max_commit: int = Field(default=10, description="Number of commits to display details for")

# class CommitMetadata(BaseModel):
#     commit_hash: str
#     commit_time: str
#     author_name: str
#     message: str

# class BranchMetadata(BaseModel):
#     branch_name: str
#     commit_hash: str
#     commit_time: str

# class TagMetadata(BaseModel):
#     tag_name: str
#     commit_hash: str
#     commit_time: str
#     tag_message: str

# class ViewExperimentResponse(BaseModel):
#     recent_commits: List[CommitMetadata]
#     branches: List[BranchMetadata]
#     tags: List[TagMetadata]

class SimpleResponse(BaseModel):
    message: Literal['created', 'added', 'modified', 'synced', 'ran']
