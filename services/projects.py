import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional, Union
from uuid import UUID, uuid3

from fastapi import Depends, FastAPI
from fastapi import Path as PathParam
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from libs.application import (
    get_reverse_url_mapper,
    redefine_operation_id_in_router,
    run,
)
from libs.envelope import Envelope
from libs.pagination import Page, init_pagination
from pydantic import BaseModel, Field, PositiveInt, StrictBool, StrictFloat, StrictInt
from pydantic.networks import HttpUrl

APP_NAME = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().stem


InputID = OutputID = str  # constr(regex=PROPERTY_KEY_RE)

# WARNING: oder matters
BuiltinTypes = Union[StrictBool, StrictInt, StrictFloat, str]
DataSchema = Union[
    BuiltinTypes,
]  # any json schema?
DataLink = HttpUrl

DataSchema = Union[DataSchema, DataLink]


class State(BaseModel):
    ...


class Node(BaseModel):
    key: str
    version: str = Field(..., regex=r"\d+\.\d+\.\d+")
    label: str

    inputs: dict[InputID, DataSchema]
    # var inputs?
    outputs: dict[OutputID, DataSchema]
    # var outputs?


# --------------
class Project(BaseModel):
    """Domain model"""

    id: UUID
    pipeline: dict[UUID, Node]


# requests models
class ProjectNew(BaseModel):
    pipeline: dict[UUID, Node]


class ProjectUpdate(BaseModel):
    # same as new but ALL optional??
    # some validators?
    pass


# response models
class ProjectItem(BaseModel):
    # Lightweight and part of an array
    id: UUID

    url: HttpUrl


class ProjectDetail(BaseModel):
    id: UUID
    pipeline: dict[UUID, Node]

    url: HttpUrl

    def update_ids(self, name: str):
        map_ids: dict[UUID, UUID] = {}
        map_ids[self.id] = uuid3(self.id, name)
        map_ids.update({node_id: uuid3(node_id, name) for node_id in self.pipeline})

        # replace ALL references


class WorkbenchView(BaseModel):
    """A view (i.e. read-only and visual) of the project's workbench"""

    workbench: dict[UUID, Node] = {}
    ui: dict[UUID, Any] = {}


# --------------


class Parameter(BaseModel):
    name: str
    value: BuiltinTypes

    node_id: UUID
    output_id: OutputID


# reponse models
class ParameterDetail(Parameter):
    url: HttpUrl
    # url_output: HttpUrl


####################################################################

# project resource --------

_PROJECTS: dict[UUID, Project] = {}


def get_valid_project(
    project_uuid: UUID = PathParam(..., description="Project unique identifier")
) -> UUID:
    if project_uuid not in _PROJECTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project does not exists"
        )
    return project_uuid


project_routes = APIRouter(prefix="/projects", tags=["project"])


@project_routes.get("", response_model=Page[ProjectItem])
def list_projects(page=Depends(init_pagination(ProjectItem))):
    ...


@project_routes.post(
    "", response_model=Envelope[ProjectDetail], status_code=status.HTTP_201_CREATED
)
def create_project(project: ProjectNew):
    ...


@project_routes.get("/{project_uuid}", response_model=Envelope[ProjectDetail])
def get_project(project_uuid: UUID = Depends(get_valid_project)):
    ...


@project_routes.put("/{project_uuid}", response_model=Envelope[ProjectDetail])
def replace_project(
    project: ProjectNew, project_uuid: UUID = Depends(get_valid_project)
):
    ...


@project_routes.patch("/{project_uuid}", response_model=Envelope[ProjectDetail])
def update_project(
    project: ProjectUpdate, project_uuid: UUID = Depends(get_valid_project)
):
    ...


@project_routes.delete(
    "/{project_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(project_uuid: UUID = Depends(get_valid_project)):
    ...


@project_routes.post("/{project_uuid}:open")
def open_project(project_uuid: UUID = Depends(get_valid_project)):
    ...


@project_routes.post("/{project_uuid}:start")
def start_project(
    use_cache: bool = True, project_uuid: UUID = Depends(get_valid_project)
):
    ...


@project_routes.post("/{project_uuid}:stop")
def stop_project(project_uuid: UUID = Depends(get_valid_project)):
    ...


@project_routes.post("/{project_uuid}:close")
def close_project(project_uuid: UUID = Depends(get_valid_project)):
    ...


@project_routes.post("/{project_uuid}:restore", response_model=Envelope[ProjectDetail])
def restore_project(project_uuid: UUID = Depends(get_valid_project)):
    ...


redefine_operation_id_in_router(
    project_routes,
    operation_id_prefix="simcore_service_webserver.projects.projects_handlers",
)

# project states sub-resource --------

pr_state_routes = APIRouter(prefix="/projects/{project_uuid}", tags=["project"])


@pr_state_routes.get("/state", response_model=Envelope[State])
def get_project_state(project_uuid: UUID = Depends(get_valid_project)):
    ...


redefine_operation_id_in_router(
    pr_state_routes,
    operation_id_prefix="simcore_service_webserver.projects.projects_handlers",
)

# project nodes sub-resource --------

project_nodes_routes = APIRouter(prefix="/projects/{project_uuid}", tags=["project"])


@project_nodes_routes.get("/nodes", response_model=Envelope[Node])
def get_project_node(project_uuid: UUID = Depends(get_valid_project)):
    ...


redefine_operation_id_in_router(
    pr_state_routes,
    operation_id_prefix="simcore_service_webserver.projects.projects_node_handlers",
)


# project tags sub-resource --------
# here we use a different approach just to check
class Tags:
    routes = APIRouter(prefix="/projects/{project_uuid}", tags=["project"])

    @staticmethod
    @routes.put("/tags/{tag_id}")
    def replace(tag_id: int, project_uuid: UUID = Depends(get_valid_project)):
        """Assigns a tag to a project"""
        ...

    @staticmethod
    @routes.delete(
        "/tags/{tag_id}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete(tag_id: int, project_uuid: UUID = Depends(get_valid_project)):
        """Un-assigns tag to a project"""
        ...


# repositories
#
#  -  versions workbench subresource
#  - Like a git system but with a "single file": the project's workbench
#
# cd new-project
# git init
# git add new-project/workbench
#
# git commit -m "Some changes"
#
# git add new-project.workbench
#
#
# SEE

#  - https://gandalf.readthedocs.io/en/latest/api.html
#  - https://github.com/hulu/restfulgit#readme
#  - https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
#       - https://www.talentica.com/blogs/explanation-git-design-principles-git-internals/
#


RepoRef = Union[UUID, str]  # :ref is the repository ref (commit, tag or branch)

# response models
class Repo(BaseModel):
    project_uuid: UUID
    url: HttpUrl


_PROJECTS_WITH_REPO = {}


def get_valid_repo(project_uuid: UUID = Depends(get_valid_project)):
    if project_uuid not in _PROJECTS_WITH_REPO:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project does not has a repository",
        )
    return project_uuid


repo_routes = APIRouter(prefix="/repos/projects", tags=["repository"])
repo_routes_hidden = APIRouter(prefix="/repos/projects", tags=["repository"])


@repo_routes.get(
    "",
    response_model=Page[Repo],
)
def list_repos(page=Depends(init_pagination(Repo))):
    """List info about versioned projects"""
    ...


# Should be automatic after first commit
#
@repo_routes_hidden.post(
    "/{project_uuid}",
    response_model=Envelope[Repo],
    status_code=status.HTTP_201_CREATED,
)
def create_repo(
    project_uuid: UUID = Depends(get_valid_project),
):
    """Creates a repo to version a project

    cd project_uuid
    git init
    git add new-project/workbench
    """
    ...


class CommitRef(BaseModel):
    sha: str  #
    url: HttpUrl


class Commit(CommitRef):
    # author: Author
    created_at: datetime
    message: str
    parents: list[CommitRef]


class CommitMessage(BaseModel):
    message: str


@repo_routes_hidden.post(
    "/{project_uuid}/commits",
    response_model=Envelope[Commit],
    status_code=status.HTTP_201_CREATED,
)
def create_commit(
    message: CommitMessage,
    project_uuid: UUID = Depends(get_valid_repo),
):
    """Commit current state of the workbench's project

    git commit -m "Some changes"
    """


@repo_routes_hidden.get(
    "/{project_uuid}/commits",
    response_model=Page[Commit],
)
def get_logs(
    ref: str,
    page=Depends(init_pagination(Commit)),
    project_uuid: UUID = Depends(get_valid_repo),
):
    """Lists commits tree of the project"""


@repo_routes_hidden.get(
    "/{project_uuid}/commits/{ref_id}", response_model=Envelope[Commit]
)
def get_commit(
    ref_id: RepoRef = PathParam(
        ..., description="A repository ref (commit, tag or branch)"
    ),
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


@repo_routes_hidden.patch(
    "/{project_uuid}/commits/{ref_id}", response_model=Envelope[Commit]
)
def update_commit_message(
    message: CommitMessage,
    ref_id: RepoRef = PathParam(
        ..., description="A repository ref (commit, tag or branch)"
    ),
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


class Tag(BaseModel):
    name: str = Field(..., description="Unique tag name")
    commit_ref: CommitRef

    url: HttpUrl


@repo_routes_hidden.get("/{project_uuid}/tags", response_model=Page[Tag])
def list_tags(
    page=Depends(init_pagination(Tag)),
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


class NewTag(BaseModel):
    commit_ref: CommitRef = Field(..., description="Commit to tag")
    name: str = Field(..., description="Unique tag name")
    message: Optional[str] = None


@repo_routes_hidden.post("/{project_uuid}/tags", response_model=Envelope[Tag])
def create_tag(
    tag: NewTag,
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


@repo_routes_hidden.get("/{project_uuid}/tags/{ref_id}", response_model=Envelope[Tag])
def get_tag(
    ref_id: RepoRef = PathParam(..., description="A commit sha or a tag name"),
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


class TagAnnotations(BaseModel):
    name: Optional[str]
    message: Optional[str]


@repo_routes_hidden.patch("/{project_uuid}/tags/{ref_id}", response_model=Envelope[Tag])
def update_tag_annotations(
    annotations: TagAnnotations,
    ref_id: RepoRef = PathParam(..., description="A commit sha or a tag name"),
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


@repo_routes_hidden.delete(
    "/{project_uuid}/tags/{tag_name}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tag(
    tag_name: str,
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


#
# a checkpoint is a combination of tags and commits in one
# Used to simplify in the front-end
#
class Checkpoint(BaseModel):
    id: PositiveInt
    checksum: str

    tag: str
    message: str

    parent: PositiveInt
    created_at: datetime

    url: HttpUrl


class CheckpointNew(BaseModel):
    tag: str
    message: Optional[str] = None


class CheckpointAnnotations(BaseModel):
    tag: Optional[str] = None
    message: Optional[str] = None


@repo_routes.get(
    "/{project_uuid}/checkpoints",
    response_model=Page[Checkpoint],
)
def list_checkpoints(
    page=Depends(init_pagination(Checkpoint)),
    project_uuid: UUID = Depends(get_valid_repo),
):
    """Lists commits&tags tree of the project"""


@repo_routes.post(
    "/{project_uuid}/checkpoints",
    response_model=Envelope[Checkpoint],
    status_code=status.HTTP_201_CREATED,
)
def create_checkpoint(
    new: CheckpointNew,
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


@repo_routes.get(
    "/{project_uuid}/checkpoints/{ref_id}", response_model=Envelope[Checkpoint]
)
def get_checkpoint(
    ref_id: RepoRef = PathParam(
        ..., description="A repository ref (commit, tag or branch)"
    ),
    project_uuid: UUID = Depends(get_valid_repo),
):
    """Set ref_id=HEAD to return current commit"""
    ...


@repo_routes.patch(
    "/{project_uuid}/checkpoints/{ref_id}", response_model=Envelope[Checkpoint]
)
def update_checkpoint_annotations(
    annotations: CheckpointAnnotations,
    ref_id: RepoRef = PathParam(
        ..., description="A repository ref (commit, tag or branch)"
    ),
    project_uuid: UUID = Depends(get_valid_repo),
):
    ...


@repo_routes.post(
    "/{project_uuid}/checkpoints/{ref_id}:checkout",
    response_model=Envelope[Checkpoint],
)
def checkout(
    ref_id: RepoRef = PathParam(
        ..., description="A repository ref (commit, tag or branch)"
    ),
    project_uuid: UUID = Depends(get_valid_repo),
):
    """
    Affect current working copy of the project, i.e. get_project will now return
    the check out
    """
    ...


@repo_routes.get(
    "/{project_uuid}/checkpoints/{ref_id}/workbench/view",
    response_model=Envelope[WorkbenchView],
)
def view_project_workbench(
    ref_id: RepoRef = PathParam(
        ..., description="A repository ref (commit, tag or branch)"
    ),
    project_uuid: UUID = Depends(get_valid_project),
    url_for: Callable = Depends(get_reverse_url_mapper),
):
    """Returns a view of the workbench for a given project's version"""
    ...


redefine_operation_id_in_router(
    repo_routes,
    operation_id_prefix="simcore_service_webserver.version_control_handlers",
)


the_app = FastAPI(title=APP_NAME)

for r in [
    project_routes,
    # project_nodes_routes,
    # pr_state_routes,
    # snapshot_routes,
    # parameter_routes,
    repo_routes,
    # repo_routes_hidden,
]:
    the_app.include_router(r)


if __name__ == "__main__":
    run(APP_NAME)
