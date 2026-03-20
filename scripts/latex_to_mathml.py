r"""
latex_to_mathml.py — LaTeX → MathML 公式固化脚本
支持 HTML 中以下四种 LaTeX 公式标记格式：
  1. <span class="math inline">\(...\)</span>     ← doc-writer 行内公式输出格式
  2. <span class="math display">\[...\]</span>    ← doc-writer 块级公式输出格式
  3. $...$ （行内，兼容旧版）
  4. $$...$$ （块级，兼容旧版）

转换引擎优先级：
  - latex2mathml (pip install latex2mathml) —— 纯 Python，无外部依赖，推荐
  - pandoc（fallback）—— 若已安装 pandoc 则作为备选

输出目标：Word 可识别的 MathML <math> 标签（OMML 兼容）
"""

import re
import sys
import os


# ─────────────────────────────────────────────
# 转换引擎选择
# ─────────────────────────────────────────────

def _convert_via_latex2mathml(latex: str, display: bool = False) -> str | None:
    """使用 latex2mathml 库进行转换（推荐）"""
    try:
        import latex2mathml.converter
        mathml = latex2mathml.converter.convert(latex)
        if display:
            mathml = mathml.replace('<math>', '<math display="block">', 1)
        else:
            mathml = mathml.replace('<math>', '<math display="inline">', 1)
        return mathml
    except ImportError:
        return None
    except Exception:
        return None


def _convert_via_pandoc(latex: str, display: bool = False) -> str | None:
    """使用 pandoc 作为备选转换引擎"""
    import subprocess
    try:
        # 为 pandoc 包装成完整的 LaTeX 数学环境
        if display:
            wrapped = f"$${latex}$$"
        else:
            wrapped = f"${latex}$"

        result = subprocess.run(
            ["pandoc", "--from=markdown", "--to=html5", "--mathml"],
            input=wrapped,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=10
        )
        # pandoc 输出包含 <p> 包裹，提取其中的 <math> 标签
        output = result.stdout.strip()
        math_match = re.search(r'<math[\s\S]*?</math>', output)
        if math_match:
            return math_match.group(0)
        return None
    except FileNotFoundError:
        return None
    except Exception:
        return None


def convert_latex(latex: str, display: bool = False) -> str | None:
    """尝试所有可用引擎转换单条 LaTeX，返回 MathML 字符串或 None"""
    # 优先使用 latex2mathml
    result = _convert_via_latex2mathml(latex, display)
    if result:
        return result
    # fallback 到 pandoc
    result = _convert_via_pandoc(latex, display)
    return result


# ─────────────────────────────────────────────
# HTML 公式替换逻辑
# ─────────────────────────────────────────────

def _make_inline_replacer(stats: dict):
    """生成行内公式替换函数"""
    def replacer(match):
        # group(1) = span 起始标签及 class 属性，group(2) = latex 内容，group(3) = latex 内容（\(...\) 格式）
        latex = (match.group(2) or match.group(3) or "").strip()
        if not latex:
            return match.group(0)
        mathml = convert_latex(latex, display=False)
        if mathml:
            stats["converted"] += 1
            return mathml
        else:
            stats["failed"] += 1
            print(f"  [WARN] 行内公式转换失败，保留原文: {latex[:60]}")
            return match.group(0)
    return replacer


def _make_block_replacer(stats: dict):
    """生成块级公式替换函数"""
    def replacer(match):
        latex = (match.group(1) or match.group(2) or "").strip()
        if not latex:
            return match.group(0)
        mathml = convert_latex(latex, display=True)
        if mathml:
            stats["converted"] += 1
            return f'<div class="math-block">{mathml}</div>'
        else:
            stats["failed"] += 1
            print(f"  [WARN] 块级公式转换失败，保留原文: {latex[:60]}")
            return match.group(0)
    return replacer


def convert_formulas_in_html(html_content: str) -> tuple[str, dict]:
    """
    扫描 HTML 内容，将所有 LaTeX 公式转换为 MathML。
    返回 (处理后的HTML, 统计信息)
    """
    stats = {"converted": 0, "failed": 0}
    content = html_content

    # ── 格式 1：<span class="math inline">\(...\)</span>
    # doc-writer 行内公式标准输出格式
    pattern_inline_span = re.compile(
        r'<span\s+class=["\']math\s+inline["\']\s*>'
        r'\\\(([\s\S]*?)\\\)'
        r'</span>',
        re.DOTALL
    )
    def _inline_span_replacer(m):
        latex = m.group(1).strip()
        mathml = convert_latex(latex, display=False)
        if mathml:
            stats["converted"] += 1
            return mathml
        stats["failed"] += 1
        print(f"  [WARN] 行内公式转换失败: {latex[:60]}")
        return m.group(0)
    content = pattern_inline_span.sub(_inline_span_replacer, content)

    # ── 格式 2：<span class="math display">\[...\]</span>
    # doc-writer 块级公式标准输出格式
    pattern_block_span = re.compile(
        r'<span\s+class=["\']math\s+display["\']\s*>'
        r'\\\[([\s\S]*?)\\\]'
        r'</span>',
        re.DOTALL
    )
    def _block_span_replacer(m):
        latex = m.group(1).strip()
        mathml = convert_latex(latex, display=True)
        if mathml:
            stats["converted"] += 1
            return f'<div class="math-block">{mathml}</div>'
        stats["failed"] += 1
        print(f"  [WARN] 块级公式转换失败: {latex[:60]}")
        return m.group(0)
    content = pattern_block_span.sub(_block_span_replacer, content)

    # ── 格式 3：裸 \[...\]（块级，无 span 包裹）
    pattern_bare_block = re.compile(r'\\\[([\s\S]*?)\\\]', re.DOTALL)
    def _bare_block_replacer(m):
        latex = m.group(1).strip()
        mathml = convert_latex(latex, display=True)
        if mathml:
            stats["converted"] += 1
            return f'<div class="math-block">{mathml}</div>'
        stats["failed"] += 1
        print(f"  [WARN] 块级公式转换失败: {latex[:60]}")
        return m.group(0)
    content = pattern_bare_block.sub(_bare_block_replacer, content)

    # ── 格式 4：裸 \(...\)（行内，无 span 包裹）
    pattern_bare_inline = re.compile(r'\\\(([\s\S]*?)\\\)', re.DOTALL)
    def _bare_inline_replacer(m):
        latex = m.group(1).strip()
        mathml = convert_latex(latex, display=False)
        if mathml:
            stats["converted"] += 1
            return mathml
        stats["failed"] += 1
        print(f"  [WARN] 行内公式转换失败: {latex[:60]}")
        return m.group(0)
    content = pattern_bare_inline.sub(_bare_inline_replacer, content)

    # ── 格式 5：$$...$$ （块级，兼容旧版）
    pattern_dollar_block = re.compile(r'\$\$([\s\S]*?)\$\$', re.DOTALL)
    def _dollar_block_replacer(m):
        latex = m.group(1).strip()
        mathml = convert_latex(latex, display=True)
        if mathml:
            stats["converted"] += 1
            return f'<div class="math-block">{mathml}</div>'
        stats["failed"] += 1
        print(f"  [WARN] 块级公式转换失败: {latex[:60]}")
        return m.group(0)
    content = pattern_dollar_block.sub(_dollar_block_replacer, content)

    # ── 格式 6：$...$ （行内，兼容旧版，需避免匹配 $$）
    pattern_dollar_inline = re.compile(r'(?<!\$)\$(?!\$)([\s\S]*?)(?<!\$)\$(?!\$)')
    def _dollar_inline_replacer(m):
        latex = m.group(1).strip()
        mathml = convert_latex(latex, display=False)
        if mathml:
            stats["converted"] += 1
            return mathml
        stats["failed"] += 1
        print(f"  [WARN] 行内公式转换失败: {latex[:60]}")
        return m.group(0)
    content = pattern_dollar_inline.sub(_dollar_inline_replacer, content)

    return content, stats


# ─────────────────────────────────────────────
# 依赖检查
# ─────────────────────────────────────────────

def check_dependencies() -> bool:
    """检查可用的转换引擎"""
    has_latex2mathml = False
    has_pandoc = False

    try:
        import latex2mathml
        has_latex2mathml = True
        print("  [OK] latex2mathml 已安装（主引擎）")
    except ImportError:
        print("  [!] latex2mathml 未安装，将尝试 pandoc fallback")
        print("      安装命令: pip install latex2mathml")

    if not has_latex2mathml:
        import subprocess
        try:
            subprocess.run(["pandoc", "--version"], capture_output=True, check=True, timeout=5)
            has_pandoc = True
            print("  [OK] pandoc 已安装（备用引擎）")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("  [!] pandoc 未找到")

    if not has_latex2mathml and not has_pandoc:
        print("\n[ERROR] 未找到任何可用的 LaTeX 转换引擎！")
        print("  请安装至少一个：")
        print("    pip install latex2mathml   （推荐，纯 Python）")
        print("    或安装 pandoc: https://pandoc.org/installing.html")
        return False
    return True


# ─────────────────────────────────────────────
# 主程序入口
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: python latex_to_mathml.py <输入HTML路径> [输出HTML路径]")
        print("      若不指定输出路径，则覆盖输入文件。")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    if not os.path.exists(input_file):
        print(f"[ERROR] 文件不存在: {input_file}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  LaTeX → MathML 公式固化脚本")
    print(f"{'='*60}")
    print(f"  输入: {input_file}")
    print(f"  输出: {output_file}")
    print(f"{'='*60}\n")

    print("[Step 1] 检查转换引擎...")
    if not check_dependencies():
        sys.exit(1)

    print(f"\n[Step 2] 读取 HTML 文件...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    print(f"  文件大小: {len(html)} 字符")

    print(f"\n[Step 3] 扫描并转换 LaTeX 公式...")
    processed_html, stats = convert_formulas_in_html(html)

    print(f"\n[Step 4] 写入输出文件...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed_html)

    print(f"\n{'='*60}")
    print(f"  完成！")
    print(f"  成功转换: {stats['converted']} 条公式")
    print(f"  转换失败: {stats['failed']} 条公式（已保留原文）")
    print(f"  输出文件: {output_file}")
    print(f"{'='*60}\n")

    if stats["failed"] > 0:
        print("[提示] 部分公式转换失败。请检查 LaTeX 语法是否合法，")
        print("       或手动在 Word 中用 Alt+= 进行升格处理。")


if __name__ == "__main__":
    main()
