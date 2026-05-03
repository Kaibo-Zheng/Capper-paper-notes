# PDF 图表提取工具

这个目录里的 `pdf_screenshot.py` 是一个通用的论文 PDF 图表提取工具，适合把论文里的主要 figure/table 截成图片后放进笔记。

## 设计思路

论文 PDF 里的“图”不总是普通图片：

- 有些 figure 是嵌入的 raster image，可以直接抽取。
- 有些 figure 是矢量图、文字和线条混排。
- 大多数 table 本质是 PDF 文本和线框，不是图片。

所以这个工具采用更稳定的方式：**按页渲染 PDF，然后根据配置裁剪页面区域**。这样 figure、table、矢量图和文字表格都能统一导出成 PNG。

## 依赖

需要 Python 包：

```powershell
pip install pymupdf pillow
```

当前环境里已经有这两个依赖时，可以直接使用。

## 新论文推荐流程

假设论文目录是：

```text
paper/AI4S/Protein/ProtCLIP/
  paper.pdf
  README.md
```

### 1. 生成裁剪配置草稿

```powershell
python scripts\pdf_screenshot.py init paper\AI4S\Protein\ProtCLIP\paper.pdf --pages 2-7 --out paper\AI4S\Protein\ProtCLIP\figure-crops.generated.json
```

`init` 会扫描 PDF 里的 `Figure 1:`、`Table 3:` 这类 caption，生成一份可编辑 JSON。

建议先输出为 `figure-crops.generated.json`，检查无误后再改名为 `figure-crops.json`。

### 2. 生成带网格的页面预览

```powershell
python scripts\pdf_screenshot.py preview paper\AI4S\Protein\ProtCLIP\paper.pdf --pages 4,7 --grid --out $env:TEMP\pdf-preview
```

打开生成的 PNG，根据蓝色网格估计裁剪区域。网格坐标是 normalized 坐标：

- 左上角是 `[0, 0]`
- 右下角是 `[1, 1]`
- `rect` 格式是 `[x0, y0, x1, y1]`

### 3. 微调 JSON

示例：

```json
{
  "name": "fig3.png",
  "page": 4,
  "rect": [0.07, 0.05, 0.93, 0.32],
  "caption": "Figure 3: Overview of ProtCLIP..."
}
```

常用字段：

- `name`：输出文件名，例如 `fig3.png` 或 `table4.png`。
- `page`：PDF 页码，从 1 开始。
- `rect`：裁剪区域。
- `caption`：辅助字段，方便知道这条配置对应原文哪个图表；裁剪时不会使用。

顶层字段：

```json
{
  "pdf": "paper.pdf",
  "output_dir": "figures",
  "dpi": 300,
  "units": "normalized",
  "trim": true
}
```

- `pdf`：PDF 路径，通常写 `paper.pdf`。
- `output_dir`：输出目录，通常写 `figures`。
- `dpi`：导出清晰度，推荐 `300`。
- `units`：`normalized` 或 `points`。新配置推荐用 `normalized`，方便配合网格预览。
- `trim`：是否自动裁掉白边。

### 4. 批量导出正式图片

```powershell
python scripts\pdf_screenshot.py crop paper\AI4S\Protein\ProtCLIP\figure-crops.json
```

图片会输出到论文目录下的 `figures/`。

### 5. 测试时不要覆盖正式图片

如果只是试裁剪范围，可以指定临时输出目录：

```powershell
python scripts\pdf_screenshot.py crop paper\AI4S\Protein\ProtCLIP\figure-crops.json --out $env:TEMP\test-crops
```

## 其他辅助命令

列出 PDF 里的图表 caption：

```powershell
python scripts\pdf_screenshot.py captions paper\AI4S\Protein\ProtCLIP\paper.pdf
```

只生成某几页预览：

```powershell
python scripts\pdf_screenshot.py preview paper\AI4S\Protein\ProtCLIP\paper.pdf --pages 2,4,7 --out $env:TEMP\preview
```

覆盖导出 DPI：

```powershell
python scripts\pdf_screenshot.py crop paper\AI4S\Protein\ProtCLIP\figure-crops.json --dpi 200 --out $env:TEMP\test-crops
```

## 当前已配置的论文

- `paper/AI4S/Protein/OntoProtein/figure-crops.json`
- `paper/AI4S/Protein/ProtCLIP/figure-crops.json`

这两份可以作为后续论文的配置参考。
