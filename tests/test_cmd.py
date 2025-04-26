import pytest
from yoctales.cmd import extract_git_repo_name_from_uri


# Tests for extract_git_repo_name_from_call
@pytest.mark.parametrize(
    "uri, expected_name",
    [
        ("git://git.openembedded.org/meta-openembedded", "meta-openembedded"),
        ("git://git.yoctoproject.org/poky", "poky"),
        ("git@github.com:marifante/super_repo.git", "super_repo"),
        ("https://github.com/example/repo.git", "repo"),
        ("ssh://git@github.com/example/repo", "repo"),
        ("invalid-uri", ""),
        ("not-a-valid git url", ""),
        ("", ""),
    ],
)
def test_extract_git_repo_name_from_uri(uri, expected_name):
    """Test extract_git_repo_name_from_call with various URIs."""
    assert extract_git_repo_name_from_uri(uri) == expected_name
