# PRIMEIRA VERSAO (02/11/2026), feita com DiagrammeR::grViz() antes da leitura
# completa de Rhinehart et al. (2022) e Ogawa et al. (2025). Notacao antiga
# (j, V_ij, U_ij) e score sem a distribuicao do maximo. A DAG de referencia e
# dev/dag/fase2_dag.dot (estilo da vinheta do crywolf). Mantida para registro.

# DAG do modelo conjunto score–ocupação (fase 2, roadmap-integration.md)
# Requer: install.packages(c("DiagrammeR", "DiagrammeRsvg", "rsvg"))
library(DiagrammeR)

dag <- grViz('
digraph fp_occu_score {
  graph [rankdir = TB, fontname = "Helvetica", fontsize = 11,
         nodesep = 0.35, ranksep = 0.45, newrank = true, compound = true]
  node  [fontname = "Helvetica", fontsize = 11]
  edge  [color = "#555555", arrowsize = 0.7, fontname = "Helvetica"]

  # ---- parâmetros (fora das placas) ----
  node [shape = plaintext]
  beta   [label = "β"]
  alpha  [label = "α"]
  delta  [label = "δ (Markov)", fontcolor = "#C2410C"]
  sig_r  [label = "σ_rec"]
  g1     [label = "μ₁, γ₁, σ₁", fontcolor = "#C2410C"]
  g0     [label = "μ₀, γ₀, σ₀", fontcolor = "#C2410C"]
  cmin   [label = "c = min_confidence", fontcolor = "#777777"]

  # ---- efeito aleatório de gravador ----
  subgraph cluster_rec {
    label = "gravador r"; labeljust = l; style = "rounded,dashed"; color = "#999999"
    node [shape = ellipse, style = solid]
    eps_r [label = "ε_r"]
  }

  subgraph cluster_site {
    label = "sítio (ou sítio-noite) i"; labeljust = l; style = rounded; color = "#333333"

    node [shape = box, style = filled, fillcolor = "#F3F4F6"]
    X   [label = "X_i"]
    node [shape = ellipse, style = solid, fillcolor = white]
    psi [label = "ψ_i"]
    z   [label = "z_i\\n(ocupação)", penwidth = 1.6]

    subgraph cluster_occ {
      label = "ocasião j (dentro da noite)"; labeljust = l; style = rounded; color = "#666666"

      node [shape = box, style = filled, fillcolor = "#F3F4F6"]
      V  [label = "V_ij"]
      U  [label = "U_ij\\n(BIO, ACI, gravador)", color = "#C2410C", penwidth = 1.6]

      node [shape = ellipse, style = solid, fillcolor = white]
      wprev [label = "w_i,j−1", style = dashed]
      theta [label = "θ_ij"]
      w     [label = "w_ij\\n(canto na ocasião)", penwidth = 1.6]
      m1    [label = "m₁ij = μ₁ + U_ij γ₁"]
      m0    [label = "m₀ij = μ₀ + U_ij γ₀"]

      node [shape = ellipse, style = filled, fillcolor = "#D1D5DB"]
      s     [label = "s_ij = logit(max_score)\\n(censurado em c)", penwidth = 1.6]

      subgraph cluster_ver {
        label = "verificação (desenho conhecido)"; labeljust = l
        style = "rounded,filled"; fillcolor = "#EFF6FF"; color = "#1D4ED8"
        node [shape = box, style = filled, fillcolor = "#DBEAFE", color = "#1D4ED8"]
        vrec [label = "ocasião anotada\\n(observa w_ij)"]
        vpos [label = "clipe positivo\\n(⇒ w_ij = 1)"]
        vneg [label = "clipe negativo\\n(informa só f₀)"]
        sel  [label = "seleção do clipe\\n(sampling_mode, inclusion_prob)",
              style = "filled,dashed"]
      }
    }
  }

  # ---- estado ----
  X -> psi; beta -> psi; psi -> z

  # ---- canto ----
  z -> w; theta -> w
  V -> theta; alpha -> theta
  wprev -> theta [color = "#C2410C", style = dashed]
  delta -> theta [color = "#C2410C"]
  sig_r -> eps_r; eps_r -> theta

  # ---- score: mistura f1/f0 ----
  w  -> s [penwidth = 1.6]
  U  -> m1 [color = "#C2410C"]; U -> m0 [color = "#C2410C"]
  g1 -> m1; g0 -> m0
  m1 -> s [label = " f₁ (w=1)", fontsize = 9]
  m0 -> s [label = " f₀ (w=0)", fontsize = 9]
  cmin -> s [color = "#999999", style = dotted]
  g1 -> g0 [label = " μ₁ > μ₀", style = dotted, arrowhead = none,
            fontsize = 9, constraint = false]

  # ---- verificação ----
  w  -> vrec [color = "#1D4ED8"]
  w  -> vpos [color = "#1D4ED8"]
  m0 -> vneg [color = "#1D4ED8"]
  s  -> sel  [color = "#1D4ED8", style = dashed,
              label = " ignorável se f₁, f₀\\n corretas (a testar)", fontsize = 9]

  # ---- legenda (abaixo do modelo) ----
  sel -> l3 [style = invis]
  subgraph cluster_leg {
    label = "legenda"; labeljust = l; style = rounded; color = "#BBBBBB"; fontsize = 10
    node [fontsize = 9]
    l1 [shape = box, style = filled, fillcolor = "#F3F4F6", label = "covariável"]
    l2 [shape = ellipse, label = "latente"]
    l3 [shape = ellipse, style = filled, fillcolor = "#D1D5DB", label = "observado"]
    l4 [shape = plaintext, fontcolor = "#C2410C", label = "novo em relação a\\nRhinehart 2022 e Ogawa 2025"]
    l5 [shape = plaintext, fontcolor = "#1D4ED8", label = "Miller 2011 /\\nChambert 2015"]
    {rank = same; l1; l2; l3; l4; l5}
    l1 -> l2 -> l3 -> l4 -> l5 [style = invis]
  }
}
')

dag

# Exportar
svg <- DiagrammeRsvg::export_svg(dag)
writeLines(svg, "dag_diagrammer_v0.svg")
rsvg::rsvg_png(charToRaw(svg), "dag_diagrammer_v0.png", width = 2400)
