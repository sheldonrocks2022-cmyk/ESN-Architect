import io
import zipfile

from cogs.botbuilder import make_project, safe_name


def test_safe_name():
    assert safe_name("My Cool Bot!") == "my-cool-bot"
    assert safe_name("!!!") == "discord-bot"


def test_python_project_contains_required_files():
    data = make_project("Test Bot", "python", ["logging", "embeds"])
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = set(archive.namelist())
    assert "test-bot/bot.py" in names
    assert "test-bot/requirements.txt" in names
    assert "test-bot/.env.example" in names
    assert "test-bot/.gitignore" in names
    assert "test-bot/README.md" in names


def test_javascript_project_contains_package():
    data = make_project("JS Bot", "javascript", ["slash commands"])
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = set(archive.namelist())
        package = archive.read("js-bot/package.json").decode()
    assert "js-bot/index.js" in names
    assert '"discord.js"' in package
