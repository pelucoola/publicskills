# 排版数据协议

文中的题名、日期和生成时间均为虚构演示值，不来自真实学生资料。
脚本排版已经核验过的题目，不自动识题、判题或猜日期。以下示例均为合成内容。

## 调用与输出

    python /path/to/exam-review-booklet/scripts/render_booklet.py /task/booklet.json --output-dir /task/output

可加 --font /path/to/ChineseFont.ttf 指定中文字体；需要 ReportLab、Pillow。FontTools 可用于压缩嵌入网页的字体。优先使用当前工作区依赖运行时。

默认文件名由已确认标题、日期形成。--stem 可指定主干；更新同一本册子可加 --overwrite，勿覆盖另一批新卷。输出 PDF、自包含 HTML、.layout.json 布局诊断。

## 最小可运行输入

    {
      "exam": {
        "title": "方程单元练习（演示）",
        "exam_date": "4月12日（年份未提供）",
        "date_label": "作业日期",
        "generated_at": "2000-04-13T16:30:00+08:00",
        "confirmation": {"title": true, "exam_date": true}
      },
      "pages": [
        {
          "topic": "第1题｜思路讲解",
          "kind": "explanation",
          "intro": "解方程4x＋3＝19。",
          "left": [
            {"type": "text", "heading": "原作答（合成演示）", "text": "4x＝19＋3＝22，所以x＝5.5。"}
          ],
          "right": [
            {"type": "text", "heading": "错在哪里", "text": "要消去左侧的＋3，应在等式两边同时减3，右边应为19－3。"},
            {"type": "text", "heading": "为什么这样想", "text": "先让4x单独留下。两边减3得4x＝16，再同时除以4得x＝4。代回原式检查。"}
          ],
          "key_tip": "每次对等式两边做同一种运算。"
        },
        {
          "topic": "第1题｜标准答案",
          "kind": "answer",
          "left": [],
          "right": [
            {"type": "text", "heading": "标准答案（按题面整理）", "text": "解：4x＋3＝19。\n两边同时减3，得4x＝16。\n两边同时除以4，得x＝4。\n代回检验成立，故x＝4。"}
          ]
        }
      ]
    }

生成时间只是示范格式；运行时取实际的用户时区时间，不复用示例值。

## 元数据

- exam.title：非空，每页主标题，最多400字符。过长到挤占正文时脚本拒绝，需使用用户认可的短标题。
- exam.exam_date：用户确认的日期显示文本，最多80字符；可以是完整日期、部分日期或“日期未提供”，脚本不补年份。
- exam.date_label：可选，默认“试卷日期”，也可设“作业日期”。
- exam.generated_at：非空，建议 ISO 8601 带时区；在独立的生成时间区域显示，不能代填考试日期。
- exam.confirmation.title 和 exam.confirmation.exam_date：必须都为布尔值 true，未确认输入将失败。不能把尚未得到答复的字段设成已确认。

## 逻辑页

pages 的每项是逻辑讲义页，内容过长自动续页，不是强制只占一张纸。

- topic：必填，原题号与页面主题。
- kind：explanation（默认）或 answer，决定两栏标识。
- intro：可选题面要点，放左栏顶部。
- left、right：内容块数组，按顺序排版。
- key_tip：可选关键指导，放右栏内容后。

同一题讲解页和答案页相邻。左右栏独立流动；一栏结束而另一栏续页时，页上提示回看本题首页。需要原图始终与某步同时出现时，在后续逻辑页重复关键裁图或辅助图。

## 文本块

    {"type": "text", "heading": "先想什么", "text": "第一段解释。\n\n第二段解释。"}

heading 可省略。所有文字按纯文本处理，保留换行；不要填 HTML、Markdown 表格或 LaTeX 源码。使用 Unicode 数学符号、清楚的括号及逐行等式；复杂公式也可制成清晰图像块。脚本不核验数学正确性。

按一个推理小目标分块，空行分段。能放入完整新页的段落会整体移至续页；超过整栏的段落按测量后的行拆分并给诊断。不可拆的推导应先按语义分段，再检查续页上下文。

## 图像块

    {
      "type": "image",
      "heading": "原作答",
      "path": "photos/work.jpg",
      "crop": [0.12, 0.28, 0.86, 0.55],
      "caption": "第1题原作答局部，保留笔迹与批改。",
      "max_height_pt": 190
    }

路径相对 JSON 所在目录解析，也支持绝对路径。crop 可省略，默认整图；在 EXIF 方向纠正后按 [左,上,右,下] 归一化裁剪，要求0≤左<右≤1、0≤上<下≤1，图像坐标原点在左上。

max_height_pt 可省略，单位磅，至少24。脚本保留长宽比，不拉伸，不覆盖源图，只在输出中内嵌派生图。过长或过窄的图应分段裁剪，不能压成读不清的缩略图。

## 验收

默认正文11.5磅，不通过不断缩字硬塞。检查 .layout.json 的页数、font_size、每页正文边界和图像框；注意 font_missing_symbols、image_low_resolution、image_extreme_aspect 等诊断。警告需实际核查；没有警告也不能跳过目视检查。

多卷分别建 JSON、分别出册；用户明确要求合并时再合并 PDF 原页，保留每页所属试卷标题与日期，勿用一个日期覆盖不同卷。
