from orchestration.tools.file_system import FileSystemTool


def test_empty_content(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    fs.write_file("empty.txt", "")
    assert fs.read_file("empty.txt") == ""

def test_special_characters(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    content = "hello\nworld\t!@#$%^&*()"
    fs.write_file("special.txt", content)
    assert fs.read_file("special.txt") == content

def test_deeply_nested_path(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    fs.write_file("a/b/c/d/e/f/file.txt", "deep")
    assert fs.file_exists("a/b/c/d/e/f/file.txt")

def test_append_to_new_file(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    result = fs.append_file("new.txt", "content")
    assert "Created" in result
    assert fs.read_file("new.txt") == "content"

def test_glob_pattern(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    fs.write_file("foo.txt", "1")
    fs.write_file("bar.txt", "2")
    fs.write_file("data.json", "{}")
    jsons = fs.list_files_by_extension(".json")
    assert "data.json" in jsons
    assert "foo.txt" not in jsons
