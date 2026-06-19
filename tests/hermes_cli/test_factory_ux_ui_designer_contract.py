from hermes_cli import factory_pg


def test_ux_ui_designer_satisfies_ui_implementation_category():
    task = {
        "task_id": "T-UI",
        "title": "Design and implement responsive dashboard interface with Open Design",
        "description": "Create frontend UI, prototype visual states, and implement the interface.",
        "phase": "ui_design",
        "owner_profile": "ux-ui-designer",
    }

    assert factory_pg._task_satisfies_mandatory_category(task, "implementation") is True


def test_ux_ui_designer_does_not_satisfy_non_ui_implementation_by_name_only():
    task = {
        "task_id": "T-NONUI",
        "title": "Implement database migration worker",
        "description": "Backend-only migration with no interface work.",
        "phase": "implementation",
        "owner_profile": "ux-ui-designer",
    }

    assert factory_pg._task_satisfies_mandatory_category(task, "implementation") is False
