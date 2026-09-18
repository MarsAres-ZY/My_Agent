# -*- coding: utf-8 -*-
"""Generate AI架构方案.pptx from scratch with native shapes (editable diagrams)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ---------- palette ----------
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
BLUE = RGBColor(0x2E, 0x6F, 0xD6)
LIGHT_BLUE = RGBColor(0xDC, 0xEA, 0xFB)
ORANGE = RGBColor(0xF2, 0x8C, 0x28)
LIGHT_ORANGE = RGBColor(0xFF, 0xEE, 0xD9)
GREEN = RGBColor(0x2E, 0x9E, 0x6B)
LIGHT_GREEN = RGBColor(0xDF, 0xF3, 0xE8)
RED = RGBColor(0xD9, 0x3C, 0x3C)
LIGHT_RED = RGBColor(0xFB, 0xE3, 0xE3)
PURPLE = RGBColor(0x7B, 0x4F, 0xC9)
LIGHT_PURPLE = RGBColor(0xEC, 0xE4, 0xF9)
GRAY = RGBColor(0x6B, 0x72, 0x80)
LIGHT_GRAY = RGBColor(0xF3, 0xF4, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x1F, 0x29, 0x37)

FONT = "Microsoft YaHei"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
W, H = prs.slide_width, prs.slide_height


# ---------- helpers ----------
def set_font(run, size=14, bold=False, color=DARK):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = etree.SubElement(rPr, qn("a:ea"))
    ea.set("typeface", FONT)


def add_text(slide, x, y, w, h, text, size=14, bold=False, color=DARK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.1):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    lines = text if isinstance(text, list) else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        set_font(r, size, bold, color)
    return tb


def box(slide, x, y, w, h, text, fill=LIGHT_BLUE, line=BLUE, size=12,
        bold=False, color=DARK, shape=MSO_SHAPE.ROUNDED_RECTANGLE, line_w=1.25,
        align=PP_ALIGN.CENTER, uniform=False):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.color.rgb = line
    s.line.width = Pt(line_w)
    s.shadow.inherit = False
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    lines = text if isinstance(text, list) else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        set_font(r, size if (i == 0 or uniform) else max(size - 2, 8), bold if i == 0 else False, color)
    return s


def group_box(slide, x, y, w, h, title, fill=LIGHT_GRAY, line=GRAY, title_color=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    s.adjustments[0] = 0.04
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.color.rgb = line
    s.line.width = Pt(1)
    s.line.dash_style = 4  # dash
    s.shadow.inherit = False
    add_text(slide, x + Inches(0.1), y + Inches(0.03), w - Inches(0.2), Inches(0.35),
             title, size=12, bold=True, color=title_color or line)
    return s


def arrow(slide, x1, y1, x2, y2, color=GRAY, width=1.5, dashed=False, head=True):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if dashed:
        c.line.dash_style = 4
    if head:
        ln = c.line._get_or_add_ln()
        tail = etree.SubElement(ln, qn("a:tailEnd"))
        tail.set("type", "triangle")
        tail.set("w", "med")
        tail.set("len", "med")
    return c


def down_arrow(slide, cx, y1, y2, **kw):
    return arrow(slide, cx, y1, cx, y2, **kw)


def header(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(0.9))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False
    add_text(slide, Inches(0.5), Inches(0.15), Inches(10), Inches(0.6), title,
             size=26, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    if subtitle:
        add_text(slide, Inches(0.5), Inches(0.95), Inches(12.3), Inches(0.4), subtitle,
                 size=13, color=GRAY)
    # accent line
    acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(0.9), W, Inches(0.05))
    acc.fill.solid()
    acc.fill.fore_color.rgb = ORANGE
    acc.line.fill.background()


def footer(slide, n):
    add_text(slide, Inches(0.5), H - Inches(0.4), Inches(8), Inches(0.3),
             "Android 车机 AI 集成架构方案 · ADK Kotlin + 可插拔 AIBox", size=9, color=GRAY)
    add_text(slide, W - Inches(1.2), H - Inches(0.4), Inches(0.8), Inches(0.3),
             str(n), size=9, color=GRAY, align=PP_ALIGN.RIGHT)


def table(slide, x, y, w, rows, col_widths=None, size=11, header_fill=NAVY, row_h=0.42):
    nrows, ncols = len(rows), len(rows[0])
    t = slide.shapes.add_table(nrows, ncols, x, y, w, Inches(row_h * nrows)).table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            t.columns[i].width = int(w * cw / total)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = t.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = str(val)
            if r == 0:
                set_font(run, size, True, WHITE)
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_fill
            else:
                set_font(run, size, c == 0, DARK)
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE if r % 2 else LIGHT_GRAY
    return t


def bullets(slide, x, y, w, h, items, size=14, color=DARK):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(6)
        level = 0
        if isinstance(it, tuple):
            level, it = it
        p.level = level
        r = p.add_run()
        r.text = ("• " if level == 0 else "– ") + it
        set_font(r, size - level * 2, False, color)
    return tb


slide_no = [0]


def new_slide(title, subtitle=None):
    s = prs.slides.add_slide(BLANK)
    slide_no[0] += 1
    if title:
        header(s, title, subtitle)
    footer(s, slide_no[0])
    return s


# ======================================================================
# 1. Cover
# ======================================================================
s = prs.slides.add_slide(BLANK)
slide_no[0] += 1
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
acc = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.55), Inches(1.5), Inches(0.08))
acc.fill.solid(); acc.fill.fore_color.rgb = ORANGE; acc.line.fill.background()
add_text(s, Inches(0.8), Inches(2.0), Inches(11.5), Inches(1.5),
         "Android 车机 AI 集成架构方案", size=44, bold=True, color=WHITE)
add_text(s, Inches(0.8), Inches(3.8), Inches(11.5), Inches(0.6),
         "基于 Google ADK Kotlin (Android) + 可插拔 AIBox 大模型推理盒", size=20, color=RGBColor(0xC9, 0xD6, 0xEA))
add_text(s, Inches(0.8), Inches(4.5), Inches(11.5), Inches(1.2),
         ["核心理念：Agent 是大脑的“意志”，AIBox 是大脑的“算力”",
          "语音 / UI / 物理按键 → ADK Agent 主导循环 ⇄ AIBox 推理 → Agent 执行 Tools → 反馈用户"],
         size=15, color=RGBColor(0xC9, 0xD6, 0xEA))
add_text(s, Inches(0.8), Inches(6.6), Inches(8), Inches(0.4), "v1.0 · 2026-09-04", size=12, color=GRAY)

# ======================================================================
# 2. Agenda
# ======================================================================
s = new_slide("目录")
items = ["方案概述与设计原则", "整体架构（分层 / 部署）", "核心交互流程（时序 / 状态机）",
         "模块详细设计（输入 / Agent / 通信 / Tools / 输出）", "AIBox 热插拔与降级策略",
         "安全与权限设计", "性能与时延优化", "常见理解误区澄清", "工程落地路线图"]
for i, it in enumerate(items):
    col, row = divmod(i, 5)
    x = Inches(0.8 + col * 6.3)
    y = Inches(1.5 + row * 1.05)
    num = box(s, x, y, Inches(0.7), Inches(0.7), f"{i+1:02d}", fill=ORANGE, line=ORANGE, size=18, bold=True, color=WHITE, shape=MSO_SHAPE.OVAL)
    add_text(s, x + Inches(0.9), y, Inches(5), Inches(0.7), it, size=18, anchor=MSO_ANCHOR.MIDDLE)

# ======================================================================
# 3. Overview
# ======================================================================
s = new_slide("1. 方案概述", "在 Android 车机 (AAOS) 上集成大模型能力，推理算力由可插拔 AIBox 承担")
add_text(s, Inches(0.5), Inches(1.5), Inches(5.8), Inches(0.4), "目标", size=18, bold=True, color=NAVY)
bullets(s, Inches(0.5), Inches(1.95), Inches(5.8), Inches(3), [
    "自然语言车控：“有点热，把空调调到 22 度”",
    "多轮对话：具备上下文记忆的语音助手",
    "多模态输入：语音、触屏 UI、方向盘物理按键统一进入同一 Agent",
    "算力解耦：大模型运行在可插拔 AIBox，车机本体不承担推理算力",
], size=14)
add_text(s, Inches(6.8), Inches(1.5), Inches(6), Inches(0.4), "核心设计原则", size=18, bold=True, color=NAVY)
table(s, Inches(6.8), Inches(1.95), Inches(6.0), [
    ["原则", "说明"],
    ["Agent 为控制中枢", "决策循环、工具执行、安全校验都在车机侧 ADK Agent 内完成"],
    ["AIBox 只做推理", "无状态“算力”，输入 prompt，输出文本 / tool-call 指令"],
    ["协议标准化", "AIBox 暴露 OpenAI 兼容 API，换模型/换盒子零改动"],
    ["可降级", "AIBox 未插入 / 故障时，基础车控仍可用"],
    ["安全优先", "白名单 + 参数校验 + 危险操作二次确认"],
], col_widths=[1.4, 3.6], size=11, row_h=0.55)
# one-liner flow
y = Inches(5.6)
steps = [("用户输入", LIGHT_GRAY, GRAY), ("Agent (车机, ADK)\n主导循环", LIGHT_BLUE, BLUE),
         ("AIBox\n推理", LIGHT_PURPLE, PURPLE), ("Agent 执行\nTools", LIGHT_ORANGE, ORANGE), ("反馈用户", LIGHT_GREEN, GREEN)]
bw, gap = Inches(2.1), Inches(0.45)
x0 = (W - (bw * 5 + gap * 4)) // 2
for i, (t, f, l) in enumerate(steps):
    x = x0 + i * (bw + gap)
    box(s, x, y, bw, Inches(0.9), t.split("\n"), fill=f, line=l, size=13, bold=True)
    if i < 4:
        arrow(s, x + bw, y + Inches(0.45), x + bw + gap, y + Inches(0.45), color=NAVY, width=2)
add_text(s, x0 + (bw + gap) * 1 + bw - Inches(0.1), y - Inches(0.35), Inches(1.2), Inches(0.3), "⇄ 多轮", size=11, color=PURPLE, align=PP_ALIGN.CENTER)

# ======================================================================
# 4. Layered architecture
# ======================================================================
s = new_slide("2.1 整体分层架构", "五层结构：输入 → Agent → 通信 → Tools → 输出；AIBox 为独立可插拔单元")
# HU outer
hu_x, hu_y, hu_w, hu_h = Inches(0.4), Inches(1.45), Inches(9.0), Inches(5.55)
group_box(s, hu_x, hu_y, hu_w, hu_h, "🚗 车机 Android (AAOS)", fill=RGBColor(0xFA, 0xFB, 0xFD), line=NAVY)

# input layer
lay_x = hu_x + Inches(0.2)
lay_w = Inches(8.6)
group_box(s, lay_x, Inches(1.85), lay_w, Inches(0.95), "① 输入层", fill=LIGHT_GRAY, line=GRAY)
for i, t in enumerate(["♪ 语音助手\n(唤醒 + ASR)", "▣ UI 触控\n(Compose / View)", "⌨ 物理按键\n(KeyEvent / VHAL)"]):
    box(s, lay_x + Inches(0.3 + i * 2.8), Inches(2.15), Inches(2.5), Inches(0.58), t.split("\n"), fill=WHITE, line=GRAY, size=11, bold=True)
# router
box(s, lay_x + Inches(2.0), Inches(2.95), Inches(4.6), Inches(0.42),
    "意图统一入口  UserRequest(text, source, carContext)", fill=WHITE, line=NAVY, size=11, bold=True)
down_arrow(s, lay_x + Inches(4.3), Inches(2.8), Inches(2.95), color=NAVY)
# agent layer
group_box(s, lay_x, Inches(3.5), Inches(5.5), Inches(1.7), "② Agent 层 (ADK Kotlin)", fill=LIGHT_BLUE, line=BLUE)
down_arrow(s, lay_x + Inches(4.3), Inches(3.37), Inches(3.5), color=NAVY)
ag = [("Runner\n驱动多轮循环", 0, 0), ("Session / Memory\n历史 · 偏好", 1, 0), ("LlmAgent\nInstruction + Tools", 2, 0),
      ("AIBoxModel : Model\nLLM 适配器", 0, 1), ("安全策略引擎\n白名单·校验·确认", 1, 1)]
for t, c, r in ag:
    box(s, lay_x + Inches(0.15 + c * 1.78), Inches(3.85 + r * 0.66), Inches(1.68), Inches(0.58), t.split("\n"), fill=WHITE, line=BLUE, size=10, bold=True)
# comm layer (right of agent)
group_box(s, lay_x + Inches(5.7), Inches(3.5), Inches(2.9), Inches(1.7), "③ AIBox 通信层", fill=LIGHT_PURPLE, line=PURPLE)
cm = ["设备发现 UsbManager/mDNS", "心跳 & 状态机", "HTTP/gRPC 客户端 (流式)", "降级路由 本地规则/云端"]
for i, t in enumerate(cm):
    box(s, lay_x + Inches(5.85), Inches(3.85 + i * 0.33), Inches(2.6), Inches(0.3), t, fill=WHITE, line=PURPLE, size=9)
arrow(s, lay_x + Inches(5.5), Inches(4.35), lay_x + Inches(5.7), Inches(4.35), color=PURPLE, width=2)
# tools layer
group_box(s, lay_x, Inches(5.35), Inches(5.5), Inches(0.75), "④ Tools 执行层  (权限白名单 + 确认机制)", fill=LIGHT_ORANGE, line=ORANGE)
for i, t in enumerate(["车控 CarProperty", "导航", "媒体", "电话", "系统设置"]):
    box(s, lay_x + Inches(0.15 + i * 1.07), Inches(5.7), Inches(1.0), Inches(0.32), t, fill=WHITE, line=ORANGE, size=9)
down_arrow(s, lay_x + Inches(2.75), Inches(5.2), Inches(5.35), color=ORANGE)
# output layer
group_box(s, lay_x, Inches(6.2), Inches(5.5), Inches(0.7), "⑤ 输出层", fill=LIGHT_GREEN, line=GREEN)
for i, t in enumerate(["♫ TTS 播报", "▣ UI 渲染 / 卡片", "车控执行反馈"]):
    box(s, lay_x + Inches(0.15 + i * 1.78), Inches(6.52), Inches(1.68), Inches(0.32), t, fill=WHITE, line=GREEN, size=9)
down_arrow(s, lay_x + Inches(2.75), Inches(6.1), Inches(6.2), color=GREEN)
# Right side: AIBox
bx = Inches(10.0)
group_box(s, bx, Inches(3.0), Inches(3.0), Inches(2.7), "📦 AIBox (可插拔)", fill=LIGHT_PURPLE, line=PURPLE)
box(s, bx + Inches(0.15), Inches(3.4), Inches(2.7), Inches(0.6), ["推理服务", "/v1/chat/completions (OpenAI 兼容)"], fill=WHITE, line=PURPLE, size=10, bold=True)
box(s, bx + Inches(0.15), Inches(4.1), Inches(2.7), Inches(0.6), ["本地大模型", "支持 function calling"], fill=WHITE, line=PURPLE, size=10, bold=True)
box(s, bx + Inches(0.15), Inches(4.8), Inches(2.7), Inches(0.6), ["可选", "ASR / TTS / RAG 向量库"], fill=WHITE, line=PURPLE, size=10, bold=True)
arrow(s, hu_x + hu_w, Inches(4.35), bx, Inches(4.35), color=PURPLE, width=2.5)
arrow(s, bx, Inches(4.55), hu_x + hu_w, Inches(4.55), color=PURPLE, width=2.5)
add_text(s, hu_x + hu_w, Inches(3.85), Inches(0.6), Inches(0.5), "USB / Ethernet / Wi-Fi", size=8, color=PURPLE, align=PP_ALIGN.CENTER)
add_text(s, Inches(10.0), Inches(5.9), Inches(3.0), Inches(1.0),
         ["💡 AIBox 是无状态推理引擎", "决策循环与 Tool 执行权", "全部在车机 Agent 侧"], size=11, color=NAVY)

# ======================================================================
# 5. Deployment view
# ======================================================================
s = new_slide("2.2 部署视图", "车机 SoC 运行 Agent App；AIBox 运行推理服务；云端 LLM 为可选降级")
group_box(s, Inches(0.8), Inches(2.0), Inches(4.4), Inches(3.6), "车机 SoC", fill=LIGHT_BLUE, line=BLUE)
box(s, Inches(1.1), Inches(2.5), Inches(3.8), Inches(0.8), ["Agent App", "(ADK Kotlin)"], fill=WHITE, line=BLUE, size=13, bold=True)
box(s, Inches(1.1), Inches(3.6), Inches(1.75), Inches(0.8), ["Car Service", "(VHAL)"], fill=WHITE, line=BLUE, size=11, bold=True)
box(s, Inches(3.15), Inches(3.6), Inches(1.75), Inches(0.8), ["Audio HAL", "(Mic / Speaker)"], fill=WHITE, line=BLUE, size=11, bold=True)
arrow(s, Inches(1.95), Inches(3.3), Inches(1.95), Inches(3.6), color=BLUE, head=False)
arrow(s, Inches(4.0), Inches(3.3), Inches(4.0), Inches(3.6), color=BLUE, head=False)
add_text(s, Inches(1.1), Inches(4.6), Inches(3.8), Inches(0.9),
         ["• 输入归一化 / Session / Tools", "• 安全策略 / 降级路由", "• 不承担模型推理"], size=11, color=NAVY)

group_box(s, Inches(8.1), Inches(2.0), Inches(4.4), Inches(3.6), "AIBox (NPU / GPU 盒子)", fill=LIGHT_PURPLE, line=PURPLE)
box(s, Inches(8.4), Inches(2.5), Inches(3.8), Inches(0.8), ["推理服务", "llama.cpp / vLLM / 厂商 SDK"], fill=WHITE, line=PURPLE, size=13, bold=True)
box(s, Inches(8.4), Inches(3.6), Inches(3.8), Inches(0.8), ["模型权重", "7B ~ 14B 量化"], fill=WHITE, line=PURPLE, size=11, bold=True)
arrow(s, Inches(10.3), Inches(3.3), Inches(10.3), Inches(3.6), color=PURPLE, head=False)
add_text(s, Inches(8.4), Inches(4.6), Inches(3.8), Inches(0.9),
         ["• OpenAI 兼容 HTTP + SSE 流式", "• /health 心跳", "• 可选 ASR / TTS / RAG"], size=11, color=PURPLE)

arrow(s, Inches(5.2), Inches(2.9), Inches(8.1), Inches(2.9), color=NAVY, width=2.5)
arrow(s, Inches(8.1), Inches(3.1), Inches(5.2), Inches(3.1), color=NAVY, width=2.5)
box(s, Inches(5.4), Inches(3.3), Inches(2.5), Inches(0.7), ["USB-C (RNDIS/NCM)", "或 车载以太网"], fill=LIGHT_GRAY, line=GRAY, size=10, bold=True)

box(s, Inches(4.9), Inches(6.0), Inches(3.5), Inches(0.75), ["☁ 云端 LLM (可选降级)", "有网络时使用"], fill=LIGHT_GRAY, line=GRAY, size=12, bold=True, shape=MSO_SHAPE.CLOUD)
arrow(s, Inches(3.0), Inches(5.6), Inches(5.2), Inches(6.2), color=GRAY, dashed=True)

# ======================================================================
# 6. Sequence diagram
# ======================================================================
s = new_slide("3.1 单次请求完整时序（含 Tool 调用循环）", "关键认知：LLM 不会“回调”Agent，它只返回 tool_call JSON；Agent 自己执行后再次请求 LLM")
parts = ["用户", "输入层\nASR/UI/按键", "ADK Runner", "LlmAgent", "AIBoxModel\n(适配器)", "AIBox LLM", "安全策略", "Tool\nCarProperty", "输出层\nTTS/UI"]
colors = [GRAY, GRAY, BLUE, BLUE, BLUE, PURPLE, ORANGE, ORANGE, GREEN]
n = len(parts)
left, right = Inches(0.5), W - Inches(0.5)
step = (right - left) // n
xs = [left + step * i + step // 2 for i in range(n)]
top_y = Inches(1.45)
bot_y = Inches(6.95)
for i, (p, c) in enumerate(zip(parts, colors)):
    box(s, xs[i] - Inches(0.65), top_y, Inches(1.3), Inches(0.55), p.split("\n"), fill=WHITE, line=c, size=10, bold=True)
    arrow(s, xs[i], top_y + Inches(0.55), xs[i], bot_y, color=RGBColor(0xC0, 0xC4, 0xCC), width=1, dashed=True, head=False)

msgs = [
    (0, 1, "“有点热，空调调到22度”", None),
    (1, 2, "UserRequest(text, 车况)", None),
    (2, 3, "组装 prompt", None),
    (3, 4, "generateContent()", "r1"),
    (4, 5, "POST /v1/chat/completions", "r1"),
    (5, 4, "tool_call: setAcTemp(22)", "r1"),
    (4, 3, "LlmResponse(functionCall)", "r1"),
    (3, 6, "校验：白名单? 范围16~30? 需确认?", "t"),
    (6, 3, "✔ 允许", "t"),
    (3, 7, "setAcTemperature(22, driver)", "t"),
    (7, 3, "{ok:true, current:22}", "t"),
    (3, 4, "generateContent(+result)", "r2"),
    (4, 5, "POST … (stream)", "r2"),
    (5, 4, "“已调到22度”(流式)", "r2"),
    (4, 3, "LlmResponse(text)", "r2"),
    (3, 2, "最终回答事件流", None),
    (2, 8, "边生成边 TTS + UI 卡片", None),
    (8, 0, "♫ 播报", None),
]
y = Inches(2.25)
dy = Inches(0.26)
# highlight regions
regions = {"r1": (3, 6, LIGHT_BLUE, "第 1 轮 LLM 调用"), "t": (7, 10, LIGHT_ORANGE, "Agent 本地执行 Tool"), "r2": (11, 14, LIGHT_BLUE, "第 2 轮 LLM 调用（回填工具结果）")}
for key, (a, b, fill, label) in regions.items():
    ry = y + dy * a - Inches(0.12)
    rh = dy * (b - a + 1) + Inches(0.05)
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, xs[2] - Inches(0.8), ry, xs[7] - xs[2] + Inches(1.6), rh)
    r.fill.solid(); r.fill.fore_color.rgb = fill; r.line.fill.background(); r.shadow.inherit = False
    # send to back (after lifelines)
    add_text(s, xs[7] + Inches(0.85), ry, Inches(1.6), Inches(0.3), label, size=9, bold=True, color=BLUE if fill == LIGHT_BLUE else ORANGE)
for i, (a, b, text, tag) in enumerate(msgs):
    yy = y + dy * i
    color = PURPLE if tag in ("r1", "r2") else ORANGE if tag == "t" else NAVY
    arrow(s, xs[a], yy, xs[b], yy, color=color, width=1.5)
    lx, rx = min(xs[a], xs[b]), max(xs[a], xs[b])
    lw = max(rx - lx, Inches(2.6))
    cx = (lx + rx) // 2
    tb = add_text(s, cx - lw // 2, yy - Inches(0.22), lw, Inches(0.22), f"{i+1}. {text}", size=8, color=DARK, align=PP_ALIGN.CENTER)
    tb.text_frame.word_wrap = False

# ======================================================================
# 7. Agent state machine
# ======================================================================
s = new_slide("3.2 Agent 决策循环状态机", "一次用户请求 = 2~N 次 LLM 调用；超时 / 取消 / 打断都要按循环设计")
def st(x, y, t, fill=LIGHT_BLUE, line=BLUE, w=1.9, h=0.65):
    return box(s, Inches(x), Inches(y), Inches(w), Inches(h), t, fill=fill, line=line, size=12, bold=True)
S = {}
MID, BOT, LOW = 3.1, 4.75, 6.15
S["idle"] = st(0.7, MID, "Idle", LIGHT_GRAY, GRAY)
S["comp"] = st(3.1, MID, ["Composing", "组装 prompt"])
S["call"] = st(5.5, MID, ["CallingLLM", "请求 AIBox"], LIGHT_PURPLE, PURPLE)
S["parse"] = st(7.9, MID, ["ParsingResponse", "解析响应"])
S["resp"] = st(10.7, MID, ["Responding", "TTS / UI"], LIGHT_GREEN, GREEN)
S["exec"] = st(7.9, BOT, ["ExecutingTool", "解析 tool_call"], LIGHT_ORANGE, ORANGE)
S["policy"] = st(5.5, BOT, ["PolicyCheck", "安全校验"], LIGHT_ORANGE, ORANGE)
S["run"] = st(3.1, BOT, ["RunTool", "执行工具"], LIGHT_ORANGE, ORANGE)
S["confirm"] = st(5.5, LOW, ["WaitConfirm", "二次确认"], LIGHT_RED, RED)

def pt(sh, side, off=0):
    l, t, w, h = sh.left, sh.top, sh.width, sh.height
    x, y = {"l": (l, t + h // 2), "r": (l + w, t + h // 2), "t": (l + w // 2, t), "b": (l + w // 2, t + h)}[side]
    return (x + off, y) if side in ("t", "b") else (x, y + off)

def edge(a, b, label, ax="r", bx="l", color=NAVY, dashed=False, offa=0, offb=0, lx=0, ly=-0.28):
    x1, y1 = pt(S[a], ax, offa); x2, y2 = pt(S[b], bx, offb)
    arrow(s, x1, y1, x2, y2, color=color, width=1.5, dashed=dashed)
    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
    add_text(s, mx - Inches(1.0) + Inches(lx), my + Inches(ly), Inches(2.0), Inches(0.28), label, size=9, color=color, align=PP_ALIGN.CENTER)

edge("idle", "comp", "收到 UserRequest")
edge("comp", "call", "prompt 就绪")
edge("call", "parse", "收到响应")
edge("parse", "resp", "纯文本回答", color=GREEN)
edge("parse", "exec", "含 tool_call", ax="b", bx="t", color=ORANGE, lx=0.9, ly=-0.14)
edge("exec", "policy", "", ax="l", bx="r", color=ORANGE)
edge("policy", "run", "允许", color=ORANGE)
edge("policy", "confirm", "高危操作", ax="b", bx="t", color=RED, lx=0.9, ly=-0.14)
edge("confirm", "run", "用户确认", ax="l", bx="b", color=GREEN, lx=-0.4, ly=0.0)
edge("run", "call", "回填 functionResponse", ax="t", bx="b", color=PURPLE, offb=Inches(-0.6), lx=-0.5, ly=-0.35)
edge("policy", "call", "拒绝(回填原因)", ax="t", bx="b", color=RED, dashed=True, offa=Inches(0.6), offb=Inches(0.6), lx=1.0, ly=-0.14)

# confirm 取消 -> Responding (bottom bus)
bus = Inches(6.95)
x1, y1 = pt(S["confirm"], "b")
xr, _ = pt(S["resp"], "b")
arrow(s, x1, y1, x1, bus, color=GRAY, width=1.5, head=False)
arrow(s, x1, bus, xr, bus, color=GRAY, width=1.5, head=False)
arrow(s, xr, bus, xr, S["resp"].top + S["resp"].height, color=GRAY, width=1.5)
add_text(s, Inches(7.0), Inches(6.67), Inches(3.5), Inches(0.28), "用户取消 → Responding", size=9, color=GRAY, align=PP_ALIGN.CENTER)

# Responding 完成 -> Idle (top loop)
top1 = Inches(2.35)
xr, yr = pt(S["resp"], "t")
xi, yi = pt(S["idle"], "t", Inches(0.3))
arrow(s, xr, yr, xr, top1, color=GREEN, width=1.5, head=False)
arrow(s, xr, top1, xi, top1, color=GREEN, width=1.5, head=False)
arrow(s, xi, top1, xi, yi, color=GREEN, width=1.5)
add_text(s, Inches(7.5), Inches(2.05), Inches(3.0), Inches(0.28), "TTS/UI 完成 → Idle", size=9, color=GREEN, align=PP_ALIGN.CENTER)

# CallingLLM 打断 -> Idle (second top loop)
top2 = Inches(2.7)
xc, yc = pt(S["call"], "t", Inches(-0.6))
xi2, yi2 = pt(S["idle"], "t", Inches(-0.3))
arrow(s, xc, yc, xc, top2, color=RED, width=1.2, dashed=True, head=False)
arrow(s, xc, top2, xi2, top2, color=RED, width=1.2, dashed=True, head=False)
arrow(s, xi2, top2, xi2, yi2, color=RED, width=1.2, dashed=True)
add_text(s, Inches(1.8), Inches(2.42), Inches(3.5), Inches(0.28), "用户打断 / 超时 / 取消 → Idle", size=9, color=RED, align=PP_ALIGN.CENTER)

add_text(s, Inches(0.7), Inches(4.75), Inches(2.3), Inches(1.6), [
    "图例：", "● 蓝：Agent 内部状态", "● 紫：与 AIBox 交互", "● 橙：Tool 执行路径", "● 红：安全拦截 / 中断"], size=10, color=NAVY)

# ======================================================================
# 8. Input normalization
# ======================================================================
s = new_slide("3.3 三种输入源归一化 & 4.1 输入层", "所有入口统一转成 UserRequest，Agent 无需感知来源差异")
box(s, Inches(0.6), Inches(1.7), Inches(3.6), Inches(0.9), ["♪ 语音", "唤醒词 → ASR → 文本"], fill=WHITE, line=GRAY, size=13, bold=True)
box(s, Inches(0.6), Inches(3.05), Inches(3.6), Inches(0.9), ["▣ UI", "点击“调低温度” → 预置意图文本"], fill=WHITE, line=GRAY, size=13, bold=True)
box(s, Inches(0.6), Inches(4.4), Inches(3.6), Inches(0.9), ["⌨ 按键", "KEYCODE_VOICE_ASSIST → 拾音；自定义键 → 预置意图"], fill=WHITE, line=GRAY, size=13, bold=True)
req = box(s, Inches(5.2), Inches(2.3), Inches(3.4), Inches(2.4),
          ["UserRequest {", "  text: String", "  source: VOICE | UI | KEY", "  carContext: 速度/档位/温度/导航态", "  uiContext: 当前页面", "}"],
          fill=LIGHT_BLUE, line=BLUE, size=12, bold=True, align=PP_ALIGN.LEFT)
for yy in (2.15, 3.5, 4.85):
    arrow(s, Inches(4.2), Inches(yy), Inches(5.2), Inches(3.5), color=NAVY)
box(s, Inches(9.6), Inches(3.0), Inches(3.0), Inches(1.0), ["ADK Runner", "runAsync()"], fill=LIGHT_BLUE, line=BLUE, size=13, bold=True)
arrow(s, Inches(8.6), Inches(3.5), Inches(9.6), Inches(3.5), color=NAVY, width=2)
table(s, Inches(0.6), Inches(5.6), Inches(12.1), [
    ["输入源", "技术实现", "备注"],
    ["语音", "唤醒词引擎(本地) → ASR", "ASR 建议车机端优先，保证无 AIBox 时仍可用；AIBox 可作增强"],
    ["UI", "Compose 点击事件 → 意图文本", "按钮“我要去公司” → text=“导航到公司”"],
    ["物理按键", "KeyEvent.KEYCODE_VOICE_ASSIST / VHAL HW_KEY_INPUT", "短按拾音、长按取消"],
], col_widths=[1, 3, 4], size=10, row_h=0.36)

# ======================================================================
# 9. Agent layer class diagram
# ======================================================================
s = new_slide("4.2 Agent 层 (ADK Kotlin) 类结构", "由当前工程 HelloTimeAgent.kt 直接演进；Tools 沿用 @Tool / @Param 注解 + KSP 生成 schema")
def cls(x, y, w, h, name, members, fill=WHITE, line=BLUE):
    b = box(s, Inches(x), Inches(y), Inches(w), Inches(0.4), name, fill=line, line=line, size=12, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)
    body = box(s, Inches(x), Inches(y + 0.4), Inches(w), Inches(h - 0.4), members, fill=fill, line=line, size=10, shape=MSO_SHAPE.RECTANGLE, align=PP_ALIGN.LEFT, uniform=True)
    return b
cls(4.6, 1.5, 3.2, 1.6, "LlmAgent", ["+ name: String", "+ instruction: Instruction", "+ model: Model", "+ tools: List<Tool>"])
cls(0.6, 1.5, 3.2, 1.3, "«interface» Model", ["+ name: String", "+ generateContent(request, stream)", "    : Flow<LlmResponse>"])
cls(0.6, 3.4, 3.2, 1.4, "AIBoxModel", ["- client: AIBoxClient", "- fallback: Model?", "+ generateContent(request, stream)"], fill=LIGHT_PURPLE, line=PURPLE)
cls(4.6, 3.9, 2.6, 1.5, "CarControlTools", ["@Tool setAcTemperature(temp, zone)", "@Tool setWindow(position, zone)", "@Tool setSeatHeater(level, zone)"], fill=LIGHT_ORANGE, line=ORANGE)
cls(7.5, 3.9, 2.4, 1.5, "NavigationTools", ["@Tool navigateTo(destination)", "@Tool cancelNavigation()"], fill=LIGHT_ORANGE, line=ORANGE)
cls(10.2, 3.9, 2.4, 1.5, "MediaTools", ["@Tool play(query)", "@Tool setVolume(level)"], fill=LIGHT_ORANGE, line=ORANGE)
cls(9.0, 1.5, 3.6, 1.3, "SafetyPolicy", ["+ check(toolName, args, carContext)", "    : Decision  (beforeToolCallback)"], fill=LIGHT_RED, line=RED)
arrow(s, Inches(4.6), Inches(2.1), Inches(3.8), Inches(2.1), color=BLUE)
add_text(s, Inches(3.8), Inches(1.75), Inches(0.8), Inches(0.3), "model", size=9, color=BLUE, align=PP_ALIGN.CENTER)
arrow(s, Inches(2.2), Inches(3.4), Inches(2.2), Inches(2.8), color=PURPLE, dashed=True)
add_text(s, Inches(2.3), Inches(2.95), Inches(1.5), Inches(0.3), "implements", size=9, color=PURPLE)
for x in (5.9, 8.7, 11.4):
    arrow(s, Inches(x), Inches(3.9), Inches(6.2), Inches(3.1), color=ORANGE)
add_text(s, Inches(6.3), Inches(3.35), Inches(3.5), Inches(0.3), "tools = xxx.generatedTools()  (KSP 生成)", size=9, color=ORANGE)
arrow(s, Inches(7.8), Inches(1.9), Inches(9.0), Inches(1.9), color=RED)
add_text(s, Inches(0.6), Inches(5.7), Inches(12.1), Inches(1.2), [
    "关键实现点：",
    "① AIBoxModel : Model —— 替换 Gemini(...)；将 ADK LlmRequest(含 tools schema) 转为 OpenAI chat/completions，再把 tool_calls / content 转回 LlmResponse",
    "② Session —— 用 ADK SessionService 保存多轮历史，按驾驶员账号隔离",
    "③ 动态 Instruction —— 每次注入车况快照：“车速 60km/h、档位 D、车内 28℃、导航中”，让模型少问多做",
], size=11, color=NAVY)

# ======================================================================
# 10. AIBox comm layer
# ======================================================================
s = new_slide("4.3 AIBox 通信层", "设备发现 → 状态机 → 客户端；协议标准化为 OpenAI 兼容 API")
group_box(s, Inches(0.6), Inches(1.6), Inches(3.4), Inches(2.6), "设备发现", fill=LIGHT_PURPLE, line=PURPLE)
for i, t in enumerate([["UsbManager", "ATTACHED / DETACHED"], ["ConnectivityManager", "以太网接口 up/down"], ["NsdManager (mDNS)", "_aibox._tcp"]]):
    box(s, Inches(0.8), Inches(2.0 + i * 0.7), Inches(3.0), Inches(0.6), t, fill=WHITE, line=PURPLE, size=10, bold=True)
sm = box(s, Inches(4.7), Inches(2.5), Inches(2.0), Inches(0.9), ["AIBox 状态机", "Absent→Ready→Busy…"], fill=LIGHT_BLUE, line=BLUE, size=11, bold=True)
for i in range(3):
    arrow(s, Inches(3.8), Inches(2.3 + i * 0.7), Inches(4.7), Inches(2.95), color=PURPLE)
group_box(s, Inches(7.4), Inches(1.6), Inches(3.4), Inches(2.6), "客户端", fill=LIGHT_BLUE, line=BLUE)
box(s, Inches(7.6), Inches(2.0), Inches(3.0), Inches(0.9), ["OkHttp + SSE", "OpenAI 兼容 / 流式"], fill=WHITE, line=BLUE, size=10, bold=True)
box(s, Inches(7.6), Inches(3.1), Inches(3.0), Inches(0.9), ["重试 / 超时 / 取消", "(协程 Job)"], fill=WHITE, line=BLUE, size=10, bold=True)
arrow(s, Inches(6.7), Inches(2.95), Inches(7.4), Inches(2.95), color=BLUE, width=2)
add_text(s, Inches(6.7), Inches(2.6), Inches(0.7), Inches(0.3), "READY", size=8, color=GREEN, align=PP_ALIGN.CENTER)
add_text(s, Inches(11.0), Inches(1.7), Inches(2.2), Inches(2.5), [
    "协议约定 (AIBox 侧实现)", "GET /health", "POST /v1/chat/completions", "  (tools, stream=true)", "GET /v1/models", "POST /v1/audio/transcriptions (可选)"], size=10, color=NAVY)
table(s, Inches(0.6), Inches(4.5), Inches(12.1), [
    ["物理链路", "优点", "缺点"],
    ["USB-C (RNDIS / NCM 网卡模式)", "供电 + 数据一体，带宽足", "需车机 USB Host 支持网卡驱动"],
    ["车载以太网 (100BASE-T1)", "稳定、低延迟", "需要硬件预留"],
    ["Wi-Fi P2P", "无线便捷", "干扰、功耗、配对复杂"],
], col_widths=[2.2, 2, 2.5], size=11, row_h=0.42)

# ======================================================================
# 11. Tools safety flow
# ======================================================================
s = new_slide("4.4 Tools 执行层：安全校验流程", "LLM 输出参数视为不可信输入；按危险等级分级放行")
def fb(x, y, t, fill=WHITE, line=NAVY, w=1.7, h=0.75, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    return box(s, Inches(x), Inches(y), Inches(w), Inches(h), t, fill=fill, line=line, size=10, bold=True, shape=shape)
def lbl(x, y, t, c=GRAY, w=1.2):
    add_text(s, Inches(x), Inches(y), Inches(w), Inches(0.3), t, size=9, color=c, align=PP_ALIGN.CENTER)
D = MSO_SHAPE.DIAMOND
y0 = 1.7
n1 = fb(0.4, y0, ["LLM 返回", "tool_call JSON"], LIGHT_PURPLE, PURPLE)
n2 = fb(2.4, y0, ["参数反序列化", "+ Schema 校验"])
n3 = fb(4.4, y0 - 0.15, "白名单?", LIGHT_GRAY, GRAY, w=1.7, h=1.05, shape=D)
n4 = fb(6.4, y0 - 0.15, ["参数范围", "合法?"], LIGHT_GRAY, GRAY, w=1.7, h=1.05, shape=D)
n5 = fb(8.4, y0 - 0.15, "危险等级", LIGHT_GRAY, GRAY, w=1.7, h=1.05, shape=D)
spd = fb(8.4, 3.3, "车速 > 0?", LIGHT_GRAY, GRAY, w=1.7, h=1.05, shape=D)
cfm = fb(8.4, 5.0, ["语音 / UI", "二次确认"], LIGHT_ORANGE, ORANGE)
rej = fb(5.4, 4.0, ["拒绝", "回填原因给 LLM"], LIGHT_RED, RED, w=1.7)
exe = fb(11.0, 5.0, ["执行", "→ 结构化结果回填 LLM"], LIGHT_GREEN, GREEN, w=1.9)

def P(sh, side, off=0):
    l, t, w, h = sh.left, sh.top, sh.width, sh.height
    x, y = {"l": (l, t + h // 2), "r": (l + w, t + h // 2), "t": (l + w // 2, t), "b": (l + w // 2, t + h)}[side]
    return (x + off, y) if side in ("t", "b") else (x, y + off)
def A(p1, p2, color=NAVY, dashed=False):
    arrow(s, p1[0], p1[1], p2[0], p2[1], color=color, width=1.5, dashed=dashed)

A(P(n1, "r"), P(n2, "l"))
A(P(n2, "r"), P(n3, "l"))
A(P(n3, "r"), P(n4, "l"), GREEN); lbl(5.85, y0 + 0.05, "是", GREEN, 0.6)
A(P(n4, "r"), P(n5, "l"), GREEN); lbl(7.85, y0 + 0.05, "是", GREEN, 0.6)
# L0/L1 -> exec (diagonal down-right)
A(P(n5, "r"), P(exe, "t", Inches(0.4)), GREEN); lbl(10.7, 2.6, "L0 只读 / L1 舒适", GREEN, 1.5)
# 否 -> rej
A(P(n3, "b"), (rej.left + Inches(0.3), rej.top), RED); lbl(4.6, 3.0, "否", RED, 0.6)
A(P(n4, "b"), (rej.left + Inches(1.2), rej.top), RED); lbl(6.7, 3.0, "否", RED, 0.6)
# L2 -> speed
A(P(n5, "b"), P(spd, "t"), ORANGE); lbl(9.3, 2.75, "L2 行车相关", ORANGE, 1.4)
# speed 否 -> exec
A(P(spd, "r"), P(exe, "t", Inches(-0.4)), GREEN); lbl(10.1, 3.5, "否(停车)", GREEN, 1.0)
# speed 是 -> confirm
A(P(spd, "b"), P(cfm, "t"), ORANGE); lbl(9.3, 4.5, "是(行驶中)", ORANGE, 1.4)
# L3 -> confirm via left bypass (x=8.15)
bx_ = Inches(8.15)
p0 = (n5.left + Inches(0.5), n5.top + Inches(0.78))
A(p0, (bx_, p0[1]), RED, True) if False else arrow(s, p0[0], p0[1], bx_, p0[1], color=RED, width=1.5, dashed=True, head=False)
arrow(s, bx_, p0[1], bx_, cfm.top + Inches(0.55), color=RED, width=1.5, dashed=True, head=False)
arrow(s, bx_, cfm.top + Inches(0.55), cfm.left, cfm.top + Inches(0.55), color=RED, width=1.5, dashed=True)
lbl(7.2, 3.2, "L3 高危", RED, 1.0)
# confirm 确认 -> exec
A(P(cfm, "r"), P(exe, "l"), GREEN); lbl(10.1, 5.05, "确认", GREEN, 0.9)
# confirm 取消 -> rej (bottom bus)
bus = Inches(6.1)
xc, yc = P(cfm, "b"); xr, yr = P(rej, "b")
arrow(s, xc, yc, xc, bus, color=RED, width=1.5, head=False)
arrow(s, xc, bus, xr, bus, color=RED, width=1.5, head=False)
arrow(s, xr, bus, xr, yr, color=RED, width=1.5)
lbl(7.2, 6.12, "取消", RED, 1.0)

table(s, Inches(0.4), Inches(2.9), Inches(4.8), [
    ["等级", "示例", "策略"],
    ["L0 只读", "查油量、天气、时间", "直接执行"],
    ["L1 舒适", "空调、座椅加热、音乐、音量", "直接执行"],
    ["L2 行车相关", "车窗、天窗、后备箱、导航变更", "行驶中需确认"],
    ["L3 高危", "车门解锁、支付、删除数据", "始终确认 + 身份校验"],
], col_widths=[1.1, 2.4, 1.6], size=9, row_h=0.3)
add_text(s, Inches(0.4), Inches(4.7), Inches(4.8), Inches(1.8), [
    "4.5 输出层要点", "• 流式 TTS：LLM 每输出一个句子片段即送 TTS，首字延迟 < 1s",
    "• UI 卡片：Tool 结果渲染为结构化卡片（导航路线、歌曲封面）",
    "• 打断机制：方向盘按键 / 新唤醒 → Job.cancel() 同时取消 LLM 请求与 TTS"], size=10, color=NAVY)

# ======================================================================
# 12. AIBox state machine + fallback
# ======================================================================
s = new_slide("5. AIBox 热插拔状态机 & 降级路由", "“插拔式”意味着必须处理“不在线”场景；降级层同样实现 Model 接口，Agent 无需感知")
def sb(x, y, t, fill, line, w=1.6, h=0.6):
    return box(s, Inches(x), Inches(y), Inches(w), Inches(h), t, fill=fill, line=line, size=11, bold=True)
A = {}
A["absent"] = sb(0.5, 3.0, "Absent", LIGHT_GRAY, GRAY)
A["attached"] = sb(2.5, 3.0, "Attached", LIGHT_BLUE, BLUE)
A["booting"] = sb(4.5, 3.0, "Booting", LIGHT_BLUE, BLUE)
A["ready"] = sb(6.5, 3.0, "Ready", LIGHT_GREEN, GREEN)
A["busy"] = sb(6.5, 1.6, "Busy", LIGHT_GREEN, GREEN)
A["degraded"] = sb(6.5, 4.4, "Degraded", LIGHT_ORANGE, ORANGE)
A["error"] = sb(4.5, 4.4, "Error", LIGHT_RED, RED)
def e2(a, b, label, ax="r", bx="l", color=NAVY, dashed=False, off=0):
    def pt(sh, side):
        l, t, w, h = sh.left, sh.top, sh.width, sh.height
        return {"l": (l, t + h // 2), "r": (l + w, t + h // 2), "t": (l + w // 2, t), "b": (l + w // 2, t + h)}[side]
    x1, y1 = pt(A[a], ax); x2, y2 = pt(A[b], bx)
    x1 += off; x2 += off
    arrow(s, x1, y1, x2, y2, color=color, width=1.5, dashed=dashed)
    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
    add_text(s, mx - Inches(0.9), my - Inches(0.3), Inches(1.8), Inches(0.3), label, size=8.5, color=color, align=PP_ALIGN.CENTER)
e2("absent", "attached", "检测到设备")
e2("attached", "booting", "建立链路")
e2("booting", "ready", "/health 模型已加载", color=GREEN)
e2("ready", "busy", "请求中", ax="t", bx="b", off=Inches(-0.3))
e2("busy", "ready", "完成", ax="b", bx="t", off=Inches(0.3), color=GREEN)
e2("ready", "degraded", "心跳失败×3", ax="b", bx="t", off=Inches(-0.3), color=ORANGE)
e2("degraded", "ready", "心跳恢复", ax="t", bx="b", off=Inches(0.3), color=GREEN)
e2("booting", "error", "超时/加载失败", ax="b", bx="t", off=Inches(-0.3), color=RED)
e2("error", "booting", "重试", ax="t", bx="b", off=Inches(0.3))
# to absent (拔出) — one bottom bus
for k in ("degraded", "error"):
    arrow(s, A[k].left + A[k].width // 2, A[k].top + A[k].height, A[k].left + A[k].width // 2, Inches(5.5), color=GRAY, dashed=True, head=False)
arrow(s, A["error"].left + A["error"].width // 2, Inches(5.5), A["absent"].left + A["absent"].width // 2, Inches(5.5), color=GRAY, dashed=True, head=False)
arrow(s, A["degraded"].left + A["degraded"].width // 2, Inches(5.5), A["error"].left + A["error"].width // 2, Inches(5.5), color=GRAY, dashed=True, head=False)
arrow(s, A["absent"].left + A["absent"].width // 2, Inches(5.5), A["absent"].left + A["absent"].width // 2, A["absent"].top + A["absent"].height, color=GRAY, dashed=True)
add_text(s, Inches(1.5), Inches(5.55), Inches(5), Inches(0.3), "任意状态检测到拔出 → Absent（Busy 时取消进行中请求）", size=9, color=GRAY)
add_text(s, Inches(0.5), Inches(1.5), Inches(5), Inches(0.4), "AIBox 状态机", size=15, bold=True, color=NAVY)

# fallback on right
rx = 9.2
add_text(s, Inches(rx), Inches(1.5), Inches(4), Inches(0.4), "降级路由", size=15, bold=True, color=NAVY)
f1 = box(s, Inches(rx), Inches(2.0), Inches(3.6), Inches(0.5), "UserRequest", fill=WHITE, line=NAVY, size=11, bold=True)
f2 = box(s, Inches(rx + 0.6), Inches(2.7), Inches(2.4), Inches(0.9), "AIBox 状态?", fill=LIGHT_GRAY, line=GRAY, size=11, bold=True, shape=D)
f3 = box(s, Inches(rx - 0.7), Inches(3.9), Inches(1.7), Inches(0.7), ["AIBox LLM", "完整 Agent 能力"], fill=LIGHT_GREEN, line=GREEN, size=10, bold=True)
f4 = box(s, Inches(rx + 1.9), Inches(3.8), Inches(1.7), Inches(0.9), ["有网络 &", "允许云端?"], fill=LIGHT_GRAY, line=GRAY, size=10, bold=True, shape=D)
f5 = box(s, Inches(rx + 0.2), Inches(5.0), Inches(1.7), Inches(0.7), ["云端 LLM", "Gemini / OpenAI 兼容"], fill=LIGHT_BLUE, line=BLUE, size=10, bold=True)
f6 = box(s, Inches(rx + 1.9), Inches(5.0), Inches(1.7), Inches(0.7), ["本地规则引擎", "关键词 → 直接映射 Tool"], fill=LIGHT_ORANGE, line=ORANGE, size=10, bold=True)
f7 = box(s, Inches(rx + 1.9), Inches(6.0), Inches(1.7), Inches(0.6), ["提示：AI 盒子未连接", "仅支持基础指令"], fill=LIGHT_RED, line=RED, size=9, bold=True)
arrow(s, f1.left + f1.width // 2, f1.top + f1.height, f2.left + f2.width // 2, f2.top, color=NAVY)
arrow(s, f2.left, f2.top + f2.height // 2, f3.left + f3.width // 2, f3.top, color=GREEN); lbl(rx - 0.5, 3.3, "Ready", GREEN, 0.8)
arrow(s, f2.left + f2.width, f2.top + f2.height // 2, f4.left + f4.width // 2, f4.top, color=ORANGE); lbl(rx + 2.7, 3.3, "非 Ready", ORANGE, 1.0)
arrow(s, f4.left, f4.top + f4.height // 2, f5.left + f5.width // 2, f5.top, color=BLUE); lbl(rx + 1.2, 4.6, "是", BLUE, 0.6)
arrow(s, f4.left + f4.width // 2, f4.top + f4.height, f6.left + f6.width // 2, f6.top, color=ORANGE); lbl(rx + 2.9, 4.7, "否", ORANGE, 0.6)
arrow(s, f6.left + f6.width // 2, f6.top + f6.height, f7.left + f7.width // 2, f7.top, color=RED, dashed=True); lbl(rx + 2.9, 5.7, "无法匹配", RED, 1.0)

# ======================================================================
# 13. Security
# ======================================================================
s = new_slide("6. 安全与权限设计", "数据边界 · 控制面 · 链路安全")
group_box(s, Inches(0.5), Inches(1.6), Inches(6.2), Inches(2.6), "数据边界", fill=LIGHT_GRAY, line=GRAY)
box(s, Inches(0.7), Inches(2.1), Inches(2.6), Inches(0.8), ["敏感数据", "通讯录 / 精确位置 / 账号"], fill=LIGHT_RED, line=RED, size=11, bold=True)
box(s, Inches(0.7), Inches(3.2), Inches(2.6), Inches(0.8), ["可外发数据", "意图文本 / 脱敏车况"], fill=LIGHT_GREEN, line=GREEN, size=11, bold=True)
box(s, Inches(4.6), Inches(2.1), Inches(1.9), Inches(0.8), "🚗 车机", fill=LIGHT_BLUE, line=BLUE, size=12, bold=True)
box(s, Inches(4.6), Inches(3.2), Inches(1.9), Inches(0.8), "📦 AIBox", fill=LIGHT_PURPLE, line=PURPLE, size=12, bold=True)
arrow(s, Inches(3.3), Inches(2.5), Inches(4.6), Inches(2.5), color=RED); lbl(3.3, 2.15, "仅车机内处理", RED, 1.3)
arrow(s, Inches(3.3), Inches(3.6), Inches(4.6), Inches(3.6), color=GREEN); lbl(3.3, 3.25, "发送", GREEN, 1.3)
group_box(s, Inches(7.0), Inches(1.6), Inches(5.8), Inches(2.6), "控制面", fill=LIGHT_ORANGE, line=ORANGE)
for i, t in enumerate([["Tool 白名单", "按车型/权限配置"], ["参数 Schema 校验", "拒绝越界 / 注入"], ["危险操作确认", "L2 行驶中 / L3 始终"], ["审计日志", "谁·何时·执行了什么"]]):
    box(s, Inches(7.2 + (i % 2) * 2.8), Inches(2.1 + (i // 2) * 1.0), Inches(2.6), Inches(0.8), t, fill=WHITE, line=ORANGE, size=11, bold=True)
group_box(s, Inches(0.5), Inches(4.5), Inches(6.2), Inches(1.4), "链路安全", fill=LIGHT_PURPLE, line=PURPLE)
box(s, Inches(0.7), Inches(4.95), Inches(2.8), Inches(0.75), ["AIBox 设备鉴权", "证书 / 配对码"], fill=WHITE, line=PURPLE, size=11, bold=True)
box(s, Inches(3.7), Inches(4.95), Inches(2.8), Inches(0.75), ["传输加密", "TLS"], fill=WHITE, line=PURPLE, size=11, bold=True)
bullets(s, Inches(7.0), Inches(4.5), Inches(5.8), Inches(2.4), [
    "Prompt 注入防护：LLM 输出参数视为不可信输入，一律做 Schema + 业务范围校验",
    "凭证管理：API Key 禁止硬编码进 APK（当前 HelloTimeAgent.kt 示例 Key 需移除并吊销）",
    "设备鉴权：只接受配对过的 AIBox，防止恶意设备伪装",
    "最小权限：Agent App 只申请必要的 Car.PERMISSION_*",
], size=12)

# ======================================================================
# 14. Performance
# ======================================================================
s = new_slide("7. 性能与时延优化", "目标：首字反馈 < 2.5s（“调空调”场景时延分解）")
# gantt
gx, gy, gw = Inches(0.8), Inches(1.7), Inches(11.8)
total = 2200
segs = [("ASR 识别", 0, 400, GRAY), ("组装 prompt", 400, 450, BLUE), ("AIBox 推理 (tool_call)", 450, 1100, PURPLE),
        ("策略校验 + 执行 Tool", 1100, 1250, ORANGE), ("AIBox 推理 (首 token)", 1250, 1800, PURPLE), ("TTS 首字播报", 1800, 2200, GREEN)]
rowh = Inches(0.42)
for i, (name, a, b, c) in enumerate(segs):
    yy = gy + rowh * i
    add_text(s, gx, yy, Inches(2.4), rowh, name, size=11, anchor=MSO_ANCHOR.MIDDLE)
    bx0 = gx + Inches(2.5) + int((gw - Inches(2.5)) * a / total)
    bw0 = int((gw - Inches(2.5)) * (b - a) / total)
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, bx0, yy + Inches(0.06), max(bw0, Inches(0.05)), rowh - Inches(0.12))
    r.fill.solid(); r.fill.fore_color.rgb = c; r.line.fill.background(); r.shadow.inherit = False
    add_text(s, bx0 + bw0 + Inches(0.05), yy, Inches(1.2), rowh, f"{b-a} ms", size=9, color=GRAY, anchor=MSO_ANCHOR.MIDDLE)
# axis
ay = gy + rowh * len(segs) + Inches(0.05)
arrow(s, gx + Inches(2.5), ay, gx + gw, ay, color=GRAY, width=1)
for ms in (0, 500, 1000, 1500, 2000):
    xx = gx + Inches(2.5) + int((gw - Inches(2.5)) * ms / total)
    add_text(s, xx - Inches(0.4), ay + Inches(0.02), Inches(0.8), Inches(0.3), f"{ms}ms", size=8, color=GRAY, align=PP_ALIGN.CENTER)
table(s, Inches(0.8), Inches(4.75), Inches(11.8), [
    ["优化手段", "效果"],
    ["流式输出 + 分句 TTS", "首字反馈时间大幅降低"],
    ["System Prompt KV Cache", "AIBox 侧缓存固定 system prompt，减少 prefill"],
    ["简单指令跳过第 2 轮", "L0/L1 工具可用模板直接播报“已调到 22 度”，省一次 LLM 调用"],
    ["并行 Tool 执行 / Tool 结果精简", "多个 tool_call 协程并发；只回填必要字段"],
    ["本地 ASR / 长连接", "避免音频跨设备传输；AIBox Ready 时保持 keep-alive"],
], col_widths=[2, 4], size=10, row_h=0.32)

# ======================================================================
# 15. Misconceptions
# ======================================================================
s = new_slide("8. 常见理解误区澄清", "原始理解 vs 修正后：核心差别在于“谁主导循环”")
group_box(s, Inches(0.5), Inches(1.6), Inches(5.6), Inches(4.0), "❌ 原始理解（单向直线）", fill=LIGHT_RED, line=RED)
wsteps = ["输入", "Agent", "访问 AIBox", "AIBox 大模型", "回调 Agent", "Agent 执行 Tools"]
for i, t in enumerate(wsteps):
    yy = Inches(2.05 + i * 0.58)
    b = box(s, Inches(2.2), yy, Inches(2.2), Inches(0.42), t, fill=WHITE, line=RED if t == "回调 Agent" else GRAY, size=11, bold=True, line_w=2.5 if t == "回调 Agent" else 1.25)
    if i < len(wsteps) - 1:
        down_arrow(s, Inches(3.3), yy + Inches(0.42), yy + Inches(0.58), color=GRAY)
add_text(s, Inches(4.5), Inches(4.2), Inches(1.6), Inches(0.9), "LLM 不会主动回调！", size=10, bold=True, color=RED)

group_box(s, Inches(6.5), Inches(1.6), Inches(6.3), Inches(4.0), "✅ 修正后（Agent 主导循环）", fill=LIGHT_GREEN, line=GREEN)
r1 = box(s, Inches(6.8), Inches(2.1), Inches(1.6), Inches(0.5), "输入", fill=WHITE, line=GRAY, size=11, bold=True)
r2 = box(s, Inches(8.7), Inches(2.1), Inches(1.8), Inches(0.5), "Agent 组装 prompt", fill=WHITE, line=BLUE, size=11, bold=True)
r3 = box(s, Inches(8.7), Inches(3.1), Inches(1.8), Inches(0.5), "请求 AIBox", fill=LIGHT_PURPLE, line=PURPLE, size=11, bold=True)
r4 = box(s, Inches(8.6), Inches(3.9), Inches(2.0), Inches(0.9), "响应类型?", fill=LIGHT_GRAY, line=GRAY, size=11, bold=True, shape=D)
r5 = box(s, Inches(6.8), Inches(4.1), Inches(1.6), Inches(0.6), ["Agent 校验", "+ 执行 Tool"], fill=LIGHT_ORANGE, line=ORANGE, size=10, bold=True)
r6 = box(s, Inches(11.0), Inches(4.1), Inches(1.6), Inches(0.6), ["输出", "TTS / UI"], fill=LIGHT_GREEN, line=GREEN, size=10, bold=True)
arrow(s, r1.left + r1.width, r1.top + r1.height // 2, r2.left, r2.top + r2.height // 2, color=NAVY)
arrow(s, r2.left + r2.width // 2, r2.top + r2.height, r3.left + r3.width // 2, r3.top, color=NAVY)
arrow(s, r3.left + r3.width // 2, r3.top + r3.height, r4.left + r4.width // 2, r4.top, color=NAVY)
arrow(s, r4.left, r4.top + r4.height // 2, r5.left + r5.width, r5.top + r5.height // 2, color=ORANGE); lbl(8.25, 4.2, "tool_call JSON", ORANGE, 1.2)
arrow(s, r4.left + r4.width, r4.top + r4.height // 2, r6.left, r6.top + r6.height // 2, color=GREEN); lbl(10.5, 4.2, "最终文本", GREEN, 0.8)
# loop back r5 -> r3
arrow(s, r5.left + r5.width // 2, r5.top, r5.left + r5.width // 2, r3.top + r3.height // 2, color=PURPLE, head=False, width=2)
arrow(s, r5.left + r5.width // 2, r3.top + r3.height // 2, r3.left, r3.top + r3.height // 2, color=PURPLE, width=2)
add_text(s, Inches(6.6), Inches(3.4), Inches(2.1), Inches(0.5), "回填结果，再次请求 (循环 2~N 次)", size=9, bold=True, color=PURPLE, align=PP_ALIGN.CENTER)
add_text(s, Inches(6.8), Inches(5.0), Inches(5.8), Inches(0.5), "执行权与循环控制权都在车机侧 Agent；AIBox 只是推理引擎。", size=11, bold=True, color=GREEN)

table(s, Inches(0.5), Inches(5.8), Inches(12.3), [
    ["#", "原始理解", "正确认知"],
    ["1", "“AIBox 回调 Agent”", "LLM 是无状态被调用方，只返回 tool_call JSON；Agent 解析后自己执行并再次请求"],
    ["2", "流程是单向直线", "实际是循环：一次请求 = 2~N 次 LLM 调用；超时/取消/打断按循环设计"],
    ["3", "语音直接进 Agent / 未考虑插拔 / Tools 无门槛", "需 ASR/TTS 环节；需状态机 + 降级；需白名单 + 校验 + 分级确认"],
], col_widths=[0.3, 3, 7], size=9.5, row_h=0.3)

# ======================================================================
# 16. Roadmap
# ======================================================================
s = new_slide("9. 工程落地路线图", "四阶段推进，每阶段可独立验证")
phases = [
    ("阶段 1 · 打通链路", BLUE, LIGHT_BLUE, ["实现 AIBoxModel : Model", "AIBox 跑起 OpenAI 兼容服务", "复用 HelloTimeAgent 验证 tool-call 循环"]),
    ("阶段 2 · 车控 Tools", ORANGE, LIGHT_ORANGE, ["CarPropertyManager 封装为 @Tool", "导航 / 媒体 Tools", "车况快照注入 prompt"]),
    ("阶段 3 · 热插拔 & 降级", PURPLE, LIGHT_PURPLE, ["USB / 网口发现 + 状态机", "心跳 & 重连", "本地规则引擎降级"]),
    ("阶段 4 · 安全 & 体验", GREEN, LIGHT_GREEN, ["安全策略引擎 (分级确认)", "流式 TTS + 打断", "审计日志 / 设备鉴权"]),
]
pw, pg = Inches(2.85), Inches(0.3)
px0 = (W - (pw * 4 + pg * 3)) // 2
for i, (t, c, lc, its) in enumerate(phases):
    x = px0 + i * (pw + pg)
    box(s, x, Inches(1.6), pw, Inches(0.6), t, fill=c, line=c, size=13, bold=True, color=WHITE, shape=MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON)
    b = box(s, x, Inches(2.35), pw, Inches(1.9), [""] + its, fill=lc, line=c, size=11, align=PP_ALIGN.LEFT)
    tf = b.text_frame
    for p in tf.paragraphs[1:]:
        for r in p.runs:
            r.text = "• " + r.text
add_text(s, Inches(0.5), Inches(4.5), Inches(12), Inches(0.4), "与当前工程的对应关系", size=15, bold=True, color=NAVY)
table(s, Inches(0.5), Inches(4.95), Inches(12.3), [
    ["当前文件", "演进方向"],
    ["HelloTimeAgent.kt → TimeService", "拆分为 CarControlTools / NavigationTools / MediaTools，保持 @Tool 注解写法"],
    ["HelloTimeAgent.kt → class OpenAI : Model (TODO)", "实现为 AIBoxModel，对接 AIBox 的 OpenAI 兼容接口"],
    ["HelloTimeAgent.kt → model = Gemini(...)", "替换为 AIBoxModel(fallback = Gemini(...))"],
    ["MainActivity.kt", "增加输入归一化层：语音 / UI / 按键 → UserRequest"],
    ["新增", "AIBoxManager（发现 + 状态机 + 心跳）、SafetyPolicy（beforeToolCallback）"],
], col_widths=[3, 5], size=10, row_h=0.33)

# ======================================================================
# 17. Closing
# ======================================================================
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
add_text(s, Inches(0.8), Inches(2.3), Inches(11.5), Inches(1.0), "总结", size=36, bold=True, color=WHITE)
add_text(s, Inches(0.8), Inches(3.3), Inches(11.5), Inches(2.5), [
    "✅ 分层思路正确：输入 → Agent → 推理 → Tools → 输出",
    "✅ 大模型放 AIBox、Agent 放车机，算力与控制解耦合理",
    "⚠ 关键修正：不是“AIBox 回调 Agent”，而是“Agent 反复调用 AIBox，AIBox 只返回决策，Agent 自己执行并再问”",
    "⚠ 必须补齐：ASR/TTS 环节、热插拔状态机与降级、Tools 安全分级",
], size=16, color=RGBColor(0xC9, 0xD6, 0xEA), line_spacing=1.4)
add_text(s, Inches(0.8), Inches(6.0), Inches(11.5), Inches(0.6), "AIBox = 大脑的推理算力，Agent = 真正的控制中枢", size=20, bold=True, color=ORANGE)

out = r"d:\DeveloperWorkspace\Tuner\My_Agent\docs\AI架构方案.pptx"
prs.save(out)
print("saved", out, "slides:", len(prs.slides))
