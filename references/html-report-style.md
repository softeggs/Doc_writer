# HTML Report Generation Style Guide

This document defines the strict formatting specifications for generating HTML reports. All automated report generation agents must adhere to these constraints.

## 1. Main Content Text (正文格式)
**Scope**: Standard paragraphs and body text.

| Property | Specification | CSS Rule |
| :--- | :--- | :--- |
| **Chinese Font** | SimSun (宋体) | `font-family: "SimSun", serif;` |
| **Western Font** | Times New Roman | `font-family: "Times New Roman", serif;` |
| **Font Size** | 10.5pt (五号) | `font-size: 10.5pt;` |
| **Indentation** | First line indent 2 chars | `text-indent: 2em;` |
| **Line Spacing** | 1.5 times | `line-height: 1.5;` |

**CSS Implementation**:
```css
body, p, div.content {
    font-family: "Times New Roman", "SimSun", serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #000000;
}

p {
    text-indent: 2em;
    margin-bottom: 0.5em; 
}
```

## 2. Table Formatting (表格格式)
**Scope**: All data tables.

| Property | Specification |
| :--- | :--- |
| **Font Family** | Microsoft YaHei (微软雅黑) |
| **Font Size** | 10.5pt (5号) |
| **Line Spacing** | Single (1.0) |
| **Indentation** | None |
| **Alignment** | Center (Vertical & Horizontal) |

### Row & Cell Styling
- **Header Row**:
  - Background: **Green (#00b050)**
  - Text Color: **White (#ffffff)**
  - Font Weight: **Bold**
- **Body Rows**:
  - Odd Rows: **White (#ffffff)**
  - Even Rows: **Light Gray (#f2f2f2)**

**CSS Implementation**:
```css
table {
    width: 100%; /* Or auto based on content */
    border-collapse: collapse;
    font-family: "Microsoft YaHei", sans-serif;
    font-size: 10.5pt;
    line-height: 1.0;
    margin: 1em auto;
}

th, td {
    padding: 6px 8px;
    border: 1px solid #d9d9d9; /* Standard border */
    text-align: center;
    vertical-align: middle;
    text-indent: 0;
}

/* Header Style */
thead th {
    background-color: #00b050;
    color: #ffffff;
    font-weight: bold;
}

/* Zebra Striping */
tbody tr:nth-child(odd) {
    background-color: #ffffff;
}

tbody tr:nth-child(even) {
    background-color: #f2f2f2;
}
```

## 3. Image & Caption Styling (图片及图注)
**Scope**: Images and their explanatory text below/above.

| Property | Specification |
| :--- | :--- |
| **Image Alignment** | Center |
| **Caption Chinese** | SimSun (宋体) |
| **Caption Western** | Times New Roman |
| **Caption Size** | 10pt (10号) |
| **Line Spacing** | Single (1.0) |
| **Alignment** | Center |

**CSS Implementation**:
```css
figure {
    display: block;
    text-align: center;
    margin: 1.5em 0;
}

img {
    max-width: 100%;
    height: auto;
    display: inline-block;
}

figcaption {
    font-family: "Times New Roman", "SimSun", serif;
    font-size: 10pt;
    text-align: center;
    line-height: 1.0;
    margin-top: 0.5em;
}
```

---
**Note to Agent**: When generating HTML, ensure these styles are included either as an inline `<style>` block in the `<head>` or strictly applied via inline styles if external stylesheets are not supported. Prefer the `<style>` block method for consistency.
