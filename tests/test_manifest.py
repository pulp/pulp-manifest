import pytest
import os
from textwrap import dedent
from pulp_manifest.build_manifest import main, PROG_DESCRIPTION, get_digest


@pytest.fixture
def create_file(tmp_path):
    def _create_file(filename, content, encoding="utf-8"):
        full_path = tmp_path / filename
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(dedent(content), encoding=encoding)
        return full_path
    return _create_file


@pytest.fixture
def create_file_tree(create_file):
    def _create_file_tree(reponame, files):
        created_files = []
        for filename, content in files:
            full_filename = os.path.join(reponame, filename)
            created_files.append(create_file(full_filename, content))
        repository_path = created_files[0].parent
        directory = str(repository_path)
        return directory, created_files
    return _create_file_tree
    

@pytest.mark.parametrize("args", (["-h"], ["--help"]))
def test_help(capsys, args):
    """Test: pulp-manifest -h|--help"""
    with pytest.raises(SystemExit):
        main(args)
    out = capsys.readouterr().out
    assert PROG_DESCRIPTION in out


def test_build_manifest(create_file_tree, tmp_path):
    """Test: pulp-manifest directory

    Assert the built manifest follows the PULP_MANIFEST spec: <filepath>,<sha256>,<bytesize>
    """
    os.chdir(tmp_path)
    manifest_file = tmp_path / "PULP_MANIFEST"
    reponame = "myrepo"
    files = [
        ("file-a", "file-content-a"),
        ("file-b", "file-content-b"),
        ("subdir/file-c", "file-content-c"),
        ("subdir/subdir2/file-d", "file-content-d"),
    ]
    repo_dir, created_files = create_file_tree(reponame, files)

    main([repo_dir])

    manifest_content = manifest_file.read_text()
    for file in created_files:
        name = str(file.relative_to(repo_dir))
        size = file.stat().st_size
        digest = get_digest(str(file))
        entry = f"{name},{digest},{size}"
        assert entry in manifest_content
        
    



