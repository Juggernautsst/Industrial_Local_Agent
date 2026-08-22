# Thesis Weekly Progress Presentation / 论文每周进展汇报

本目录包含 Issue #6 的可审查工作稿：可维护的 XeLaTeX/Beamer 源码、UQ 风格背景和当前 PDF。当前版本为 9 页英文 slides，既有 PowerPoint-compatible 草稿未重新生成；因此 Issue #6 要求的约十页中英双语内容和可打开的 PPTX 仍是未完成验收项，本分支不表示 Issue 已完成。

This directory contains a reviewable work in progress for Issue #6: maintainable XeLaTeX/Beamer source, UQ-style backgrounds, and the current PDF. The current version has nine English slides, and the existing PowerPoint-compatible draft was not regenerated. The approximately ten bilingual slides and openable PPTX required by Issue #6 therefore remain incomplete acceptance items; this branch does not represent Issue completion.

## 内容与证据边界 / Content and Evidence Boundary

- 9 页核心 slides 全部使用英文；本 README 继续按仓库规则保留中英对照。 / All nine core slides are English-only; this README remains bilingual under repository policy.
- 项目状态来自父仓库 README、路线图、架构、实施手册和 Stage 1A 交接记录。 / Project status comes from the parent README, roadmap, architecture, implementation handbook, and Stage 1A handoff.
- 主线聚焦内网研究者、授权后检索、本地模型、MCP 对只读 Tidy3D 导出结果适配器的边界，以及受控外发与外部区块链。 / The main story focuses on the intranet researcher, retrieval after authorization, the local model, the MCP boundary for a read-only Tidy3D export-result adapter, and controlled release to an external blockchain path.
- 当前只有单用户、本地证据闭环可运行；企业 RAG、MCP 工具、安全外发、外部应用和区块链集成都明确标为待验证能力。 / Only the single-user local evidence loop runs today; enterprise RAG, MCP tools, secure release, the external application, and blockchain integration are explicitly marked as capabilities still requiring validation.
- 保密数据只允许通过链下受保护数据包传输；区块链在概念上仅保存最小证明，外部接口和链类型尚未定义。 / Confidential data may move only in a protected off-chain package; conceptually, the blockchain stores only a minimal proof, while the external interface and ledger type remain undefined.
- 模型选择页使用 Qwen2.5-3B-Instruct 和 Kimi K3 的官方 Hugging Face 模型卡截图；Qwen2.5-3B 已通过单个合成光子学 fixture 的工程 smoke test，但这不代表科研质量验收；`qwen2.5:7b` 仍是记录中的交接基线。 / The model-options slide uses official Hugging Face model-card captures for Qwen2.5-3B-Instruct and Kimi K3. Qwen2.5-3B has passed one synthetic-photonics fixture engineering smoke test, which is not scientific-quality acceptance; `qwen2.5:7b` remains the recorded handoff baseline.
- 原始模板 PPTX、其分类/作者元数据和字体文件不在本目录中。 / The original template PPTX, its classification/author metadata, and font files are not present in this directory.

## 编辑封面 / Edit the Title Slide

在 `weekly-progress.tex` 顶部修改以下宏：

Edit these macros near the top of `weekly-progress.tex`:

```tex
\newcommand{\StudentName}{Chang Yin}
\newcommand{\SupervisorName}{Xiao Guo}
\newcommand{\PresentationDate}{5/8/2026}
```

封面与全部正文 slides 均使用英文。

The cover and all slide content are English-only.

## 构建 PDF / Build the PDF

从本目录运行 Windows TeX Live 2025：

Run Windows TeX Live 2025 from this directory:

```bash
cmd.exe /c "latexmk -xelatex -interaction=nonstopmode -halt-on-error weekly-progress.tex"
```

输出为 `weekly-progress.pdf`。源码按字体名称使用已安装的 Arial 和 Times New Roman；字体会嵌入 PDF，但字体文件不会复制到项目中。

The output is `weekly-progress.pdf`. The source resolves the installed Arial and Times New Roman fonts by name. Fonts are embedded in the PDF, but font files are not copied into the project.

## PlantUML diagrams / PlantUML 图

四张架构图由 `diagrams/*.puml` 生成，使用固定版本 PlantUML `1.2025.4` 的 Smetana 布局，因此不依赖 Graphviz。图先输出 SVG，再转为供 Beamer 使用的矢量 PDF；PNG 仅保留作预览。 / The four architecture figures are generated from `diagrams/*.puml` with PlantUML `1.2025.4` and its Smetana layout, so Graphviz is not required. Each figure is exported to SVG and then converted to a vector PDF for Beamer; PNG files are retained only as previews.

在本目录运行以下命令可重建图（需要 Java 和 Python `cairosvg`）： / Run the following commands in this directory to rebuild the figures (requires Java and Python `cairosvg`):

```bash
java -DPLANTUML_LIMIT_SIZE=8192 \
  -jar /tmp/industrial-local-agent-plantuml-1.2025.4.jar \
  -tsvg diagrams/target-workflow.puml \
  diagrams/authorize-before-retrieval.puml \
  diagrams/mcp-tool-boundary.puml \
  diagrams/confidential-collaboration.puml
python3 -c "import cairosvg, pathlib; src=pathlib.Path('diagrams'); dst=pathlib.Path('assets/diagrams'); [cairosvg.svg2pdf(url=str(p), write_to=str(dst/(p.stem+'.pdf'))) for p in src.glob('*.svg') if p.stem in {'target-workflow','authorize-before-retrieval','mcp-tool-boundary','confidential-collaboration'}]"
```

图中使用短节点和单向箭头，避免把未定义的实现细节表现成已完成能力。 / The figures use short node labels and one-way arrows so undefined implementation details are not presented as completed capabilities.

## 验证 / Validation

最低验证包括：

Minimum validation includes:

```bash
pdfinfo weekly-progress.pdf
pdffonts weekly-progress.pdf
pdftotext -layout weekly-progress.pdf -
rg -n "Overfull|LaTeX Error|Package .* Error|Emergency stop|Fatal error" weekly-progress.log
```

还应将 PDF 临时渲染为 1600 x 900 PNG 并逐页检查，确认 16:9 画布、内容边界和视觉一致性；这些检查图不属于交付物。

Also render the PDF temporarily to 1600 x 900 PNG files and inspect every page for the 16:9 canvas, content boundaries, and visual consistency. These inspection images are not deliverables.

## 分发限制 / Distribution Boundary

背景包含 UQ 品牌资产，仅用于该内部 thesis progress presentation。公开发布主题、背景或兼容副本前，应单独核对 UQ Brand Centre 规则。

The backgrounds contain UQ brand assets and are intended only for this internal thesis-progress presentation. Check UQ Brand Centre requirements separately before public redistribution of the theme, backgrounds, or compatible copy.
