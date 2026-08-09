# seed.ps1 — Run once to populate answers.json with all historical Wordle answers.
# Run from the wordle-data directory:  .\seed.ps1

$Start     = [datetime]"2021-06-19"
$Today     = [datetime]::Today
$Yesterday = $Today.AddDays(-1)
$Headers = @{ "User-Agent" = "Mozilla/5.0" }
$Answers = New-Object System.Collections.ArrayList
$Skipped = 0
$Total   = ($Yesterday - $Start).Days + 1

Write-Host "Fetching $Total dates ($($Start.ToString('yyyy-MM-dd')) to $($Yesterday.ToString('yyyy-MM-dd')))..."
Write-Host ""

$d = $Start
while ($d -le $Yesterday) {
    $dateStr = $d.ToString("yyyy-MM-dd")

    try {
        $r = Invoke-RestMethod -Uri "https://www.nytimes.com/svc/wordle/v2/$dateStr.json" `
                               -Headers $Headers -TimeoutSec 10
        [void]$Answers.Add([PSCustomObject]@{
            word = $r.solution.ToLower()
            date = $r.print_date
        })
        Write-Host "  $dateStr  $($r.solution.ToLower())"
    }
    catch [System.Net.WebException] {
        $code = [int]$_.Exception.Response.StatusCode
        if ($code -eq 404) {
            Write-Host "  $dateStr  (not found, skipped)"
        } else {
            Write-Warning "$dateStr  HTTP $code"
        }
        $Skipped++
    }
    catch {
        Write-Warning "$dateStr  $_"
        $Skipped++
    }

    $d = $d.AddDays(1)
    Start-Sleep -Milliseconds 200
}

$json    = @($Answers | Sort-Object date) | ConvertTo-Json -Compress
$utf8    = New-Object System.Text.UTF8Encoding $false   # no BOM
[System.IO.File]::WriteAllText("$PWD\answers.json", $json, $utf8)

Write-Host ""
Write-Host "Done. $($Answers.Count) answers written to answers.json ($Skipped skipped)."
