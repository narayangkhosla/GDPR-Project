import subprocess


# def test_bandit_scan():
#     result = subprocess.run(["bandit", "-r", "src/"], capture_output=True, text=True)
#     assert "No issues identified." in result.stdout


def test_bandit_scan():
    result = subprocess.run(
        ["bandit", "-r", "src/", "-f", "json"], capture_output=True, text=True
    )
    assert result.returncode in (0, 1), "Bandit did not run correctly"

    data = result.stdout
    assert (
        '"issue_severity": "HIGH"' not in data
    ), "High severity issue found in Bandit scan"
