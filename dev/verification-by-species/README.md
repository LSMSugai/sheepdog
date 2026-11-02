# Verificação por espécie

Passo 3 da fase 5 do `dev/roadmap-integration.md`: quantos clipes
verificados cada espécie recebe em cada desenho do `select_clips()`. É o
risco que a Fase A do roadmap do crywolf aponta para o `fp_occu_ms()`: a
verificação pode ser rara demais nas espécies raras.

`run.R` usa os dados de exemplo (8 espécies, 4 sítios, 354 gravações) em
dois cenários: o exemplo como está e um cenário raro, em que *lep_fus*
fica só com 15 detecções sorteadas em ARA. Os positivos esperados são o
número de clipes vezes a precisão da espécie nos clipes revisados do
exemplo; no `random_recordings`, são as gravações sorteadas em que a
espécie tem predição ≥ 0,5, vezes a precisão. Não há novo sorteio de
vereditos, então os números são esperanças, não realizações.

## Resultado para *lep_fus* (clipes verificados; positivos esperados)

| Desenho | Exemplo (545 detecções) | Rara (15 detecções em ARA) |
|---|---|---|
| `top`, `target_total = 40` | 20 (7,9) | 5 (2,0) |
| `top`, `target_total = 80` | 40 (15,7) | 10 (3,9) |
| `top`, `target_total = 160` | 80 (31,5) | 15 (5,9) |
| `random_detections`, `target_total = 40` | 29 (11,4) | 1 (0,4) |
| `random_detections`, `target_total = 160` | 106 (41,7) | 1 (0,4) |
| `random_recordings`, 5% | 18 (7,0) | 18 (0,0) |
| `random_recordings`, 20% | 71 (27,8) | 71 (0,2) |

`target_total` é por sítio e dividido igualmente entre as espécies
(water filling). Com o exemplo como está, isso protege as espécies menos
detectadas: todas recebem a mesma cota. Mas uma espécie rara de fato não
tem candidatas para preencher a cota:

- no `top`, ela fica com todas as suas detecções (15) e não passa disso,
  qualquer que seja o orçamento;
- no `random_detections` com limiar 0,5, só uma ocasião dela passa o
  limiar;
- no `random_recordings`, cada gravação é revisada para todas as
  espécies, mas a espécie quase nunca canta nas gravações sorteadas: os
  clipes viram negativos, que informam a ausência, mas não dão nenhum
  positivo.

Nenhum desenho resolve isso sozinho, e aumentar o orçamento não ajuda no
`top` nem no `random_detections`. Duas consequências:

1. A taxa de falso positivo de uma espécie rara vem das outras espécies
   (o empréstimo de informação do modelo de comunidade) ou da priori. É
   justamente o que o `fp_occu_ms()` deve medir.
2. O export precisa dizer quais espécies estão nessa situação. Daí o
   aviso do `export_occupancy_data()` (`min_verified = 10`): nomeia as
   espécies com predições e menos de 10 clipes revisados, ou sem nenhum
   positivo ou nenhum negativo. O mínimo de 10 é um piso, não um cálculo
   de tamanho amostral.

Para a espécie rara, o caminho de desenho que sobra é a verificação
dirigida (por exemplo, as noites de chuva do *tra_typ* no FrogNet), que
não é um sorteio independente do score e precisa ser declarada como tal.
