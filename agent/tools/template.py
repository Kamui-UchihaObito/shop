"""Template tools used for rendering structured responses."""
from __future__ import annotations

from typing import Any, Dict, List

from .base import ToolSpec


_TEMPLATE_LIBRARY: Dict[str, str] = {
    "onboarding_plan": """# 新人入职计划\n\n- 第1天: 完成账号权限申请与团队介绍。\n- 第2天: 研读产品SOP，并梳理关键指标。\n- 第3天: 影子跟班体验重点流程。\n- 第4-5天: 参与一次正在进行的项目，记录观察。\n- 第6-7天: 输出一份入职周报与改进建议。\n""",
    "ops_review": """# 运营复盘模板\n\n## 目标复盘\n- 目标：{goal}\n- 结果：{result}\n\n## 数据表现\n- 核心指标：{metrics}\n\n## 正向亮点\n{highlights}\n\n## 问题与优化\n{issues}\n\n## 后续行动\n{next_steps}\n""",
}


class TemplateFillTool:
    spec = ToolSpec(
        name="template.fill",
        description="根据槽位填充标准模板",
    )

    def __call__(self, template: str | None = None, **slots: Any) -> Dict[str, Any]:
        if template and template in _TEMPLATE_LIBRARY:
            raw_template = _TEMPLATE_LIBRARY[template]
        else:
            raw_template = _TEMPLATE_LIBRARY["onboarding_plan"]
        return {"rendered": raw_template.format(**{k: v for k, v in slots.items() if isinstance(v, str)})}


class ChecklistTool:
    spec = ToolSpec(
        name="template.checklist",
        description="根据上下文生成下一步行动清单",
    )

    def __call__(self, **_: Any) -> Dict[str, Any]:
        checklist = [
            "明确当前目标与成功指标",
            "确认关键联系人及Owner",
            "检查是否存在最新SOP或模板",
            "拆解任务并排定优先级",
        ]
        return {"checklist": checklist}
