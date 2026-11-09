# Sauce Demo UI tests

A small Playwright + Python + pytest UI suite for [Sauce Demo](https://www.saucedemo.com), with page objects, shared authenticated browser state, parallel execution, failure artifacts, and Azure Pipelines CI configuration.

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux
- Network access to Sauce Demo and the Playwright browser downloads

## Setup

Create and activate a virtual environment, then install pinned packages and the Chromium browser:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

On Linux/macOS, activate with `source .venv/bin/activate`; install the browser with `python -m playwright install chromium` (or `python -m playwright install --with-deps chromium` on a Linux CI agent).

The default base URL and browser settings are in `pytest.ini` and the test runner. Override the URL with `--base-url`, the browser with `PW_BROWSER`, and credentials with environment variables or pytest options:

- `SAUCE_USERNAME` / `--username` (default: `standard_user`)
- `SAUCE_PASSWORD` / `--password` (default: `secret_sauce`)
- `SAUCE_LOCKED_OUT_USERNAME` / `--locked-out-username` (default: `locked_out_user`)

Do not commit real credentials. The defaults are the public Sauce Demo practice-site credentials.

## Run the suite

One command runs the complete suite in parallel and creates JUnit XML and a self-contained HTML report in `reports/`:

```powershell
.\run_tests.ps1
```

On Linux/macOS, run `python -m pytest -n auto --browser chromium --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html`. Set `--browser firefox` or `--browser webkit` to choose another browser; install it first with `python -m playwright install firefox` or `python -m playwright install webkit`. Add pytest options such as `-k checkout` to run a subset.

Useful focused commands:

```powershell
pytest tests/test_login.py::test_valid_user_lands_on_inventory
pytest -m smoke
pytest -m regression
pytest tests/test_login.py --browser chromium -n 0
```

The Azure pipeline runs a Chromium/Firefox/WebKit matrix. It uses Ubuntu-hosted agents by default; set `useMicrosoftHosted` to `false` and supply `selfHostedPool` to select a self-hosted pool. Self-hosted agents should be Linux with the Python version and dependencies available for Playwright's `install --with-deps` step.

## Design decisions

- Each page object owns locators and user-level actions; page objects are provided as pytest fixtures in `conftest.py`.
- A session-scoped fixture signs in once per pytest worker, saves browser storage under `test-results/.auth/`, and reuses it for tests that do not exercise login. Login scenarios opt out with `no_auth` and get a clean context.
- Base URL is configured through pytest's base-url option/config; browser selection comes from `PW_BROWSER` in the runner or `--browser`; account values come from environment variables or CLI options.
- Selectors prefer Sauce Demo's stable `data-test` attributes and accessible role/name locators. Assertions use Playwright's web-first `expect`; there are no fixed sleeps.
- `smoke` covers the valid login and checkout journey; `regression` covers validation, sorting, and cart behavior.
- Traces and videos are retained on test failure; screenshots are captured only on failure. Generated output is under `test-results/` and is ignored by Git.

## Azure Pipelines steps

`azure-pipelines.yml` runs for pushes and pull requests, selects Python 3.11, installs pinned dependencies, installs each matrix browser and its system dependencies, executes pytest with xdist, publishes JUnit results using `PublishTestResults@2`, and uploads HTML reports plus failure artifacts as pipeline artifacts. Pool selection is parameterized so the YAML can target Microsoft-hosted Ubuntu or a named self-hosted pool. Configure the Sauce Demo credentials as pipeline variables if overriding the public defaults.

## Sample reports

`sample-reports/` contains the committed JUnit XML and self-contained HTML report from a local run. New local reports are generated in `reports/`; copy the desired run output into `sample-reports/` when refreshing the checked-in sample.

## Assumptions and next steps

- Tests target the public Sauce Demo practice application and its current labels and `data-test` attributes; a redesign may require locator updates.
- The default suite uses Chromium locally. The CI matrix adds Firefox and WebKit coverage.
- With more time, I would add a scheduled run, richer failure metadata (browser/version and commit), retry policy informed by observed flakiness, and an Allure report only if stakeholders need its history and dashboards.
