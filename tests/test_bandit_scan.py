import subprocess


def test_bandit_scan():
    result = subprocess.run(["bandit", "-r", "src/"], capture_output=True, text=True)
    assert "No issues identified." in result.stdout
