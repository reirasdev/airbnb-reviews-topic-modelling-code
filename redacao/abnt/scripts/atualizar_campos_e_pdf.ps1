# Atualiza sumario, lista de tabelas e numeracao no Word (campos) e salva o DOCX. Registra cada etapa em saida\word.log.
$saida = Join-Path (Split-Path $PSScriptRoot -Parent) "saida"
$docx = Join-Path $saida "Raphael_Eiras-Decomposicao_por_aspecto_do_sentimento_em_avaliacoes_do_airbnb_rj-ucp_2026-ABNT.docx"
$pdf = Join-Path $saida "Raphael_Eiras-Decomposicao_por_aspecto_do_sentimento_em_avaliacoes_do_airbnb_rj-ucp_2026-ABNT.pdf"
$log = Join-Path $saida "word.log"
function L($m) { (Get-Date -Format "HH:mm:ss") + " " + $m | Out-File -FilePath $log -Append -Encoding utf8 }
Remove-Item $log -ErrorAction SilentlyContinue
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    L "abrindo"
    $d = $w.Documents.Open($docx, $false, $false)
    L ("aberto; paginas=" + $d.ComputeStatistics(2))
    foreach ($t in $d.TablesOfContents) { L "atualizando sumario"; $t.Update() | Out-Null; L "sumario ok" }
    foreach ($t in $d.TablesOfFigures) { L "atualizando lista de tabelas"; $t.Update() | Out-Null; L "lista ok" }
    $d.Repaginate()
    foreach ($t in $d.TablesOfContents) { $t.UpdatePageNumbers() }
    foreach ($t in $d.TablesOfFigures) { $t.UpdatePageNumbers() }
    L "salvando"
    $d.Save()
    L ("campos atualizados; paginas=" + $d.ComputeStatistics(2))
    $d.Close(0)
}
catch { L ("ERRO: " + $_.Exception.Message) }
finally { $w.Quit(); L "word encerrado" }
# O PDF deve ser exportado manualmente no Word (Arquivo > Exportar > Criar PDF): a exportacao automatica por COM travou nesta maquina.
