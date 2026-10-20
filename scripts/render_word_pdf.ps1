param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$InputDocx = [System.IO.Path]::GetFullPath($InputDocx.Replace('/', '\'))
$OutputPdf = [System.IO.Path]::GetFullPath($OutputPdf.Replace('/', '\'))
[void][System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($OutputPdf))
$wordRenderer = $null
$renderDocument = $null
try {
    $wordRenderer = New-Object -ComObject Word.Application
    $wordRenderer.Visible = $false
    $wordRenderer.DisplayAlerts = 0
    $renderDocument = $wordRenderer.Documents.Open($InputDocx, $false, $true)
    $renderDocument.ExportAsFixedFormat($OutputPdf, 17)
    Write-Output 'WORD_PDF_RENDERED'
} finally {
    if ($null -ne $renderDocument) { $renderDocument.Close(0); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($renderDocument) }
    if ($null -ne $wordRenderer) { $wordRenderer.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordRenderer) }
}
