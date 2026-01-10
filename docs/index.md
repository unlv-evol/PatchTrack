# PatchTrack Documentation

## Comprehensive Analysis of ChatGPT's Influence on Pull Request Outcomes

---

## Overview

The rapid adoption of **large language models (LLMs)** like ChatGPT has fundamentally transformed software development workflows. While existing research has examined the quality of AI-generated code in isolation, there is limited understanding of how developers integrate these suggestions into real-world collaborative environments.

This research introduces **PatchTrack**, a novel tool that enables fine-grained analysis of AI-assisted code decisions by classifying ChatGPT patch integration patterns in pull request workflows.

---

## Research Scope

Our comprehensive study analyzed:

- **338 pull requests** from **255 GitHub repositories** with documented ChatGPT usage
- **645 AI-generated code snippets** integrated into patches
- **3,486 developer-authored modifications** and refinements
- **89 qualitative case studies** of integrated patches

---

## Key Findings

### Integration Patterns

Contrary to expectations, full adoption of ChatGPT suggestions is remarkably low. Our analysis reveals:

- **Median integration rate: 25%** — developers adopt approximately one-quarter of suggested code
- **Selective application** — developers extract and refactor AI suggestions rather than applying them verbatim
- **Iterative refinement** — ChatGPT output serves as a foundation for developer-driven improvements

### Developer Behavior

Qualitative analysis identified three recurring integration strategies:

1. **Structural Integration** — Adapting AI-generated logic to existing codebases
2. **Selective Extraction** — Extracting specific components from broader suggestions
3. **Iterative Refinement** — Incremental improvements and customization

---

## Impact

These findings demonstrate that developers treat LLM-generated code as a **starting point rather than production-ready solutions**. This insight reshapes our understanding of human-AI collaboration in software engineering, revealing sophisticated developer decision-making processes that balance automation with quality assurance.

---

## Publication
### How to Cite

**BibTeX:**
```bibtex
@misc{ogenrwot2025patchtrackcomprehensiveanalysischatgpts,
      title={PatchTrack: A Comprehensive Analysis of ChatGPT's Influence on Pull Request Outcomes}, 
      author={Daniel Ogenrwot and John Businge},
      year={2025},
      eprint={2505.07700},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2505.07700}, 
}
```

**APA:**
```
Ogenrwot, D., & Businge, J. (2025). PatchTrack: A comprehensive analysis of ChatGPT's influence on pull request outcomes. arXiv preprint arXiv:2505.07700.
```

---

## License

PatchTrack is released under an open-source license. For complete license terms and conditions, see the [LICENSE](../LICENSE) file in the repository.