r"""
extract_references.py — 参考文献章节自动生成脚本
从文档项目的 docs/ 子目录中扫描 Markdown 文件，解析论文题录信息，
输出标准格式的参考文献 HTML 章节（chapter_refs.html）。

支持的 docs/ 文件格式：
  - 每篇文献用 ## N. 作者, 年份 标题（二级标题）分隔
  - 题录字段：标题、作者、期刊/会议、年份、卷期页码、DOI
  - 原文链接：从 DOI / PubMed / PMC 字段提取

用法:
    python scripts/extract_references.py <文档根目录> [输出html路径]

    文档根目录结构示例：
        my_report/
        ├── src/
        │   └── docs/          ← 脚本扫描此目录
        │       ├── papers.md
        │       └── review.md
        └── html_report/
            └── chapter_refs.html  ← 默认输出到此处

    若输出路径未指定，默认写入 <根目录>/html_report/chapter_refs.html
"""

import sys
import os
import re
import glob


# ─────────────────────────────────────────────
# Markdown 解析
# ─────────────────────────────────────────────

class Reference:
    """单条参考文献"""
    def __init__(self):
        self.index = 0          # 序号（全局排序用）
        self.raw_title = ""     # 论文标题（原文题名）
        self.authors = ""       # 作者
        self.journal = ""       # 期刊/会议
        self.year = ""          # 年份
        self.volume_pages = ""  # 卷期页码
        self.doi = ""           # DOI
        self.doi_url = ""       # DOI 链接
        self.pubmed_url = ""    # PubMed 链接
        self.pmc_url = ""       # PMC 链接
        self.source_file = ""   # 来源文件名

    def is_valid(self) -> bool:
        """至少有标题或作者才算有效"""
        return bool(self.authors or self.raw_title)


def _extract_url(text: str, prefix: str) -> str:
    """从文本中提取 URL"""
    url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)
    if prefix.lower() in text.lower():
        urls = url_pattern.findall(text)
        if urls:
            # 清理尾部标点
            return urls[0].rstrip('>;,.')
    return ""


def parse_md_file(filepath: str) -> list[Reference]:
    """解析单个 Markdown 文件，返回 Reference 列表"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    refs = []
    filename = os.path.basename(filepath)

    # 按二级标题 (## N. ...) 或 (## 作者...) 分割各文献块
    # 兼容格式：## 1. Dikkema et al., 2023  或  ## 作者, 年份
    sections = re.split(r'\n(?=## )', content)

    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue

        header = lines[0].strip()
        # 跳过文件级大标题（# 开头）和非文献块（如 ## 检索目标、## 综述结论 等）
        if not header.startswith('## '):
            continue

        # 判断是否为文献块：标题行含有年份数字（4位）
        if not re.search(r'\b(19|20)\d{2}\b', header):
            continue

        ref = Reference()
        ref.source_file = filename

        # 从块内容中提取各字段
        block_text = '\n'.join(lines[1:])

        # ── 标题（论文原文题名）
        title_match = re.search(r'-\s*标题[：:]\s*(.+)', block_text)
        if title_match:
            ref.raw_title = title_match.group(1).strip().strip('《》*_')

        # ── 作者
        author_match = re.search(r'-\s*作者[：:]\s*(.+)', block_text)
        if author_match:
            ref.authors = author_match.group(1).strip().strip('*_')

        # ── 期刊/会议
        journal_match = re.search(r'-\s*(期刊|会议)[：:]\s*(.+)', block_text)
        if journal_match:
            ref.journal = journal_match.group(2).strip().strip('*_')

        # ── 年份
        year_match = re.search(r'-\s*年份[：:]\s*(\d{4})', block_text)
        if year_match:
            ref.year = year_match.group(1)
        else:
            # 从章节标题中提取
            year_in_header = re.search(r'\b(19|20)\d{2}\b', header)
            if year_in_header:
                ref.year = year_in_header.group(0)

        # ── 卷期页码
        vol_match = re.search(r'-\s*卷期页码[：:]\s*(.+)', block_text)
        if vol_match:
            ref.volume_pages = vol_match.group(1).strip().strip('*_')

        # ── DOI
        doi_match = re.search(r'-\s*DOI[：:]\s*[`]?(10\.\S+)[`]?', block_text)
        if doi_match:
            ref.doi = doi_match.group(1).strip('`').rstrip('>;,.')
            ref.doi_url = f"https://doi.org/{ref.doi}"
        else:
            # 尝试从链接行直接提取
            doi_url_match = re.search(r'https?://doi\.org/(\S+)', block_text)
            if doi_url_match:
                ref.doi = doi_url_match.group(1).rstrip('>;,.')
                ref.doi_url = f"https://doi.org/{ref.doi}"

        # ── PubMed / PMC 链接
        for line in block_text.split('\n'):
            if 'pubmed' in line.lower() and not ref.pubmed_url:
                url = _extract_url(line, 'pubmed')
                if url:
                    ref.pubmed_url = url
            if 'pmc' in line.lower() and not ref.pmc_url:
                url = _extract_url(line, 'pmc.ncbi')
                if url:
                    ref.pmc_url = url

        if ref.is_valid():
            refs.append(ref)

    return refs


def scan_docs_directory(docs_dir: str) -> list[Reference]:
    """扫描 docs/ 目录下所有 Markdown 文件，合并并去重返回文献列表"""
    if not os.path.isdir(docs_dir):
        return []

    md_files = glob.glob(os.path.join(docs_dir, '*.md'))
    md_files += glob.glob(os.path.join(docs_dir, '**/*.md'), recursive=True)
    md_files = list(set(md_files))  # 去重

    all_refs = []
    seen_dois = set()

    for md_file in sorted(md_files):
        refs = parse_md_file(md_file)
        for ref in refs:
            # 按 DOI 去重（多个 md 文件可能引用同一篇）
            key = ref.doi if ref.doi else f"{ref.authors}_{ref.year}"
            if key and key not in seen_dois:
                seen_dois.add(key)
                all_refs.append(ref)

    # 按年份降序排列，年份相同按作者字母升序
    all_refs.sort(key=lambda r: (-int(r.year) if r.year.isdigit() else 0, r.authors))

    # 赋全局序号
    for i, ref in enumerate(all_refs, 1):
        ref.index = i

    return all_refs


# ─────────────────────────────────────────────
# HTML 生成
# ─────────────────────────────────────────────

def format_citation(ref: Reference) -> str:
    """生成标准引文格式字符串（Vancouver 风格）"""
    parts = []
    if ref.authors:
        parts.append(ref.authors)
    if ref.raw_title:
        parts.append(f"<em>{ref.raw_title}</em>")
    if ref.journal:
        parts.append(f"<em>{ref.journal}</em>")
    if ref.year:
        vol = f"; {ref.volume_pages}" if ref.volume_pages else ""
        parts.append(f"{ref.year}{vol}")
    return ". ".join(parts)


def build_links_html(ref: Reference) -> str:
    """生成原文链接 HTML"""
    links = []
    if ref.doi_url:
        links.append(f'<a href="{ref.doi_url}" target="_blank" class="ref-link doi-link">DOI</a>')
    if ref.pubmed_url:
        links.append(f'<a href="{ref.pubmed_url}" target="_blank" class="ref-link pubmed-link">PubMed</a>')
    if ref.pmc_url:
        links.append(f'<a href="{ref.pmc_url}" target="_blank" class="ref-link pmc-link">PMC 全文</a>')
    return " ".join(links)


REF_CSS = """
<style>
body { font-family: 'Microsoft YaHei', 'SimSun', serif; font-size: 10.5pt; }
.ref-section h2 { font-family: '黑体', sans-serif; font-size: 14pt; font-weight: bold;
                   border-bottom: 2px solid #00b050; padding-bottom: 6px; margin-top: 40px; }
.ref-list { list-style: none; padding: 0; margin: 0; }
.ref-item { display: flex; align-items: flex-start; gap: 12px;
            padding: 10px 0; border-bottom: 1px solid #eee; }
.ref-index { min-width: 28px; font-weight: bold; color: #00b050;
             font-size: 10pt; padding-top: 2px; }
.ref-content { flex: 1; line-height: 1.6; font-size: 10pt; }
.ref-content em { font-style: italic; }
.ref-links { margin-top: 5px; display: flex; gap: 8px; flex-wrap: wrap; }
.ref-link { display: inline-block; padding: 2px 8px; border-radius: 3px;
            font-size: 9pt; text-decoration: none; font-family: Arial, sans-serif; }
.doi-link    { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.pubmed-link { background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; }
.pmc-link    { background: #fff3e0; color: #e65100; border: 1px solid #ffcc80; }
.ref-link:hover { opacity: 0.8; }
.ref-source { font-size: 8pt; color: #bbb; margin-top: 3px; }
.ref-notice { background: #f9fffb; border-left: 4px solid #00b050; padding: 10px 16px;
              margin: 16px 0; font-size: 10pt; border-radius: 0 4px 4px 0; }
</style>
"""


def generate_refs_html(refs: list[Reference], chapter_num: int,
                       doc_title: str = "", docs_dir: str = "") -> str:
    """生成完整的参考文献章节 HTML"""

    # 章节编号（动态，由调用者传入）
    chapter_label = f"第{chapter_num}章"

    items_html = ""
    for ref in refs:
        citation = format_citation(ref)
        links = build_links_html(ref)
        source_hint = f'<div class="ref-source">来源文件：{ref.source_file}</div>' if ref.source_file else ""
        items_html += f"""
        <li class="ref-item">
            <span class="ref-index">[{ref.index}]</span>
            <div class="ref-content">
                <div>{citation}</div>
                <div class="ref-links">{links}</div>
                {source_hint}
            </div>
        </li>"""

    if not refs:
        items_html = '<li class="ref-item"><span style="color:#999;">（未检测到有效文献条目）</span></li>'

    docs_path_hint = f'<code>{docs_dir}</code>' if docs_dir else '<code>src/docs/</code>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>参考文献</title>
{REF_CSS}
</head>
<body>
<div class="content ref-section">

    <h2>{chapter_label} 参考文献</h2>

    <div class="ref-notice">
        以下参考文献由 <strong>extract_references.py</strong> 自动从 {docs_path_hint} 目录解析生成，
        共检索到 <strong>{len(refs)}</strong> 条有效文献。如需补充或修正，请编辑对应 Markdown 文件后重新运行脚本。
    </div>

    <ol class="ref-list">
        {items_html}
    </ol>

    <p style="text-align: center; margin-top: 50px;">
        <a href="index.html" style="color: #00b050; text-decoration: none; font-weight: bold;">
            [ 返回总览目录 / Return to Index ]
        </a>
    </p>

</div>
</body>
</html>"""

    return html


# ─────────────────────────────────────────────
# 主程序
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: python extract_references.py <文档根目录> [输出html路径] [章节序号]")
        print("      章节序号默认自动推断（取 html_report/ 下 chapter_N.html 的最大 N + 1）")
        sys.exit(1)

    root_dir = sys.argv[1]
    docs_dir = os.path.join(root_dir, 'src', 'docs')

    # 默认输出路径
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        html_dir = os.path.join(root_dir, 'html_report')
        os.makedirs(html_dir, exist_ok=True)
        output_path = os.path.join(html_dir, 'chapter_refs.html')

    # 自动推断章节编号
    if len(sys.argv) >= 4:
        chapter_num = int(sys.argv[3])
    else:
        html_dir = os.path.join(root_dir, 'html_report')
        existing = glob.glob(os.path.join(html_dir, 'chapter_*.html'))
        nums = []
        for f in existing:
            m = re.search(r'chapter_(\d+)\.html', os.path.basename(f))
            if m:
                nums.append(int(m.group(1)))
        chapter_num = (max(nums) + 1) if nums else 1

    print(f"\n{'='*60}")
    print(f"  参考文献章节生成脚本")
    print(f"{'='*60}")
    print(f"  文档根目录: {root_dir}")
    print(f"  docs 目录:  {docs_dir}")
    print(f"  输出路径:   {output_path}")
    print(f"  章节编号:   第 {chapter_num} 章")
    print(f"{'='*60}\n")

    # 检查 docs 目录
    if not os.path.isdir(docs_dir):
        print(f"[WARN] docs 目录不存在: {docs_dir}")
        print(f"       请在该目录下放置包含文献信息的 Markdown 文件。")
        print(f"       Markdown 格式要求：")
        print(f"         ## N. 作者, 年份 标题")
        print(f"         - 标题：论文英文题名")
        print(f"         - 作者：Author et al.")
        print(f"         - 期刊：期刊名")
        print(f"         - 年份：YYYY")
        print(f"         - 卷期页码：Vol(Issue):pp")
        print(f"         - DOI：10.xxxx/xxxxx")
        # 生成空壳 HTML 供占位
        refs = []
    else:
        md_files = glob.glob(os.path.join(docs_dir, '**/*.md'), recursive=True) + \
                   glob.glob(os.path.join(docs_dir, '*.md'))
        md_files = list(set(md_files))
        print(f"[Step 1] 扫描到 {len(md_files)} 个 Markdown 文件：")
        for f in sorted(md_files):
            print(f"         - {os.path.basename(f)}")

        print(f"\n[Step 2] 解析文献条目...")
        refs = scan_docs_directory(docs_dir)
        print(f"         解析完成，共 {len(refs)} 条有效文献（已去重）")

    print(f"\n[Step 3] 生成参考文献 HTML...")
    html = generate_refs_html(refs, chapter_num=chapter_num, docs_dir=docs_dir)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n{'='*60}")
    print(f"  完成！")
    print(f"  文献总数: {len(refs)} 条")
    print(f"  输出文件: {output_path}")
    print(f"{'='*60}\n")

    if refs:
        print("References preview:")
        for ref in refs:
            title_preview = ref.raw_title[:50].encode('ascii', errors='replace').decode('ascii')
            author_preview = ref.authors[:30].encode('ascii', errors='replace').decode('ascii')
            print(f"  [{ref.index}] {author_preview} ({ref.year})")


if __name__ == "__main__":
    main()
