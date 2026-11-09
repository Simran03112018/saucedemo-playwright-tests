$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path reports, test-results | Out-Null
$browser = if ($env:PW_BROWSER) { $env:PW_BROWSER } else { "chromium" }

pytest -n auto --browser $browser --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html @args
exit $LASTEXITCODE
