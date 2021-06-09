from typing import Any, Dict, List, Optional

from ...consts import ActorSourceType
from ..base import ResourceClient


class ActorVersionClient(ResourceClient):
    """Sub-client for manipulating a single actor version."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorVersionClient."""
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about the actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Returns:
            dict, optional: The retrieved actor version data
        """
        return self._get()

    def update(
        self,
        *,
        build_tag: Optional[str] = None,
        env_vars: Optional[List[Dict]] = None,
        apply_env_vars_to_build: Optional[bool] = None,
        source_type: Optional[ActorSourceType] = None,
        source_code: Optional[str] = None,
        base_docker_image: Optional[str] = None,
        source_files: Optional[List[Dict]] = None,
        git_repo_url: Optional[str] = None,
        tarball_url: Optional[str] = None,
        github_gist_url: Optional[str] = None,
    ) -> Dict:
        """Update the actor version with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/version-object/update-version

        Args:
            build_tag (str, optional): Tag that is automatically set to the latest successful build of the current version.
            env_vars (list of dict, optional): Environment variables that will be available to the actor run process,
                and optionally also to the build process. See the API docs for their exact structure.
            apply_env_vars_to_build (bool, optional): Whether the environment variables specified for the actor run
                will also be set to the actor build process.
            source_type (ActorSourceType, optional): What source type is the actor version using.
            source_code (str, optional): Source code as a single JavaScript/Node.js file,
                using the base Docker image specified in ``baseDockerImage``.
                Required when ``source_type`` is ``ActorSourceType.SOURCE_CODE``.
            base_docker_image (str, optional): The base Docker image to use for single-file actors.
                Required when ``source_type`` is ``ActorSourceType.SOURCE_CODE``.
            source_files (list of dict, optional): Source code comprised of multiple files, each an item of the array.
                Required when ``source_type`` is ``ActorSourceType.SOURCE_FILES``. See the API docs for the exact structure.
            git_repo_url (str, optional): The URL of a Git repository from which the source code will be cloned.
                Required when ``source_type`` is ``ActorSourceType.GIT_REPO``.
            tarball_url (str, optional): The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when ``source_type`` is ``ActorSourceType.TARBALL``.
            github_gist_url (str, optional): The URL of a GitHub Gist from which the source will be downloaded.
                Required when ``source_type`` is ``ActorSourceType.GITHUB_GIST``.

        Returns:
            dict: The updated actor version
        """
        version_fields: Dict[str, Any] = {}
        if build_tag is not None:
            version_fields['buildTag'] = build_tag
        if env_vars is not None:
            version_fields['envVars'] = env_vars
        if apply_env_vars_to_build is not None:
            version_fields['applyEnvVarsToBuild'] = apply_env_vars_to_build
        if source_type is not None:
            version_fields['sourceType'] = source_type.value
        if source_code is not None:
            version_fields['sourceCode'] = source_code
        if base_docker_image is not None:
            version_fields['baseDockerImage'] = base_docker_image
        if source_files is not None:
            version_fields['sourceFiles'] = source_files
        if git_repo_url is not None:
            version_fields['gitRepoUrl'] = git_repo_url
        if tarball_url is not None:
            version_fields['tarballUrl'] = tarball_url
        if github_gist_url is not None:
            version_fields['gitHubGistUrl'] = github_gist_url

        return self._update(version_fields)

    def delete(self) -> None:
        """Delete the actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version
        """
        return self._delete()
