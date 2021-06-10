from enum import Enum


class ActorJobStatus(Enum):
    """Available statuses for actor jobs (runs or builds)."""

    #: Actor job initialized but not started yet
    READY = 'READY'
    #: Actor job in progress
    RUNNING = 'RUNNING'
    #: Actor job finished successfully
    SUCCEEDED = 'SUCCEEDED'
    #: Actor job or build failed
    FAILED = 'FAILED'
    #: Actor job currently timing out
    TIMING_OUT = 'TIMING_OUT'
    #: Actor job timed out
    TIMED_OUT = 'TIMED_OUT'
    #: Actor job currently being aborted by user
    ABORTING = 'ABORTING'
    #: Actor job aborted by user
    ABORTED = 'ABORTED'

    @property
    def _is_terminal(self) -> bool:
        """Whether this actor job status is terminal."""
        return self in (ActorJobStatus.SUCCEEDED, ActorJobStatus.FAILED, ActorJobStatus.TIMED_OUT, ActorJobStatus.ABORTED)


class ActorSourceType(Enum):
    """Available source types for actors."""

    #: Actor source code is a single JavaScript/Node.js file
    SOURCE_CODE = 'SOURCE_CODE'
    #: Actor source code is comprised of multiple files
    SOURCE_FILES = 'SOURCE_FILES'
    #: Actor source code is cloned from a Git repository
    GIT_REPO = 'GIT_REPO'
    #: Actor source code is downloaded using a tarball or Zip file
    TARBALL = 'TARBALL'
    #: Actor source code is taken from a GitHub Gist
    GITHUB_GIST = 'GITHUB_GIST'


class WebhookEventType(Enum):
    """Events that can trigger a webhook."""

    #: The actor run was created
    ACTOR_RUN_CREATED = 'ACTOR.RUN.CREATED'
    #: The actor run has succeeded
    ACTOR_RUN_SUCCEEDED = 'ACTOR.RUN.SUCCEEDED'
    #: The actor run has failed
    ACTOR_RUN_FAILED = 'ACTOR.RUN.FAILED'
    #: The actor run has timed out
    ACTOR_RUN_TIMED_OUT = 'ACTOR.RUN.TIMED_OUT'
    #: The actor run was aborted
    ACTOR_RUN_ABORTED = 'ACTOR.RUN.ABORTED'
    #: The actor run was resurrected
    ACTOR_RUN_RESURRECTED = 'ACTOR.RUN.RESURRECTED'
