# Attribution and third-party material

The repository retains its existing [Apache License 2.0](LICENSE). Upstream material keeps its original license; the repository license does not override third-party terms.

The starting growing gecko and trained persistent control derive from **Growing Neural Cellular Automata** by Alexander Mordvintsev, Ettore Randazzo, Eyvind Niklasson and Michael Levin (Distill, 2020), https://doi.org/10.23915/distill.00023. Source repository: https://github.com/distillpub/post--growing-ca, pinned commit `a12c7efa541b5770043a8d5470bffeacfd7b0435`. The upstream CC BY 4.0 license is preserved in [code/SOURCE_LICENSE](code/SOURCE_LICENSE). Source URLs and checkpoint hashes are in [data/manifest.json](data/manifest.json).

The weights in `weights/original.npz` and `weights/trained_control.npz` decode the published demo checkpoints into float32. The other seven checkpoints modify the original weights; their exact constructions and changes are documented in `code/edits.py`, `code/persistence.py`, and the report. Figures and animations depict simulations of those checkpoints. Preserve this attribution when redistributing these materials.

Research report and experiment documentation: Stefano Nichele, 2026. GPT-6 Astra produced the recorded weight-edit proposals and submitted explanations; the accompanying report describes their independent evaluation and limitations.
