from app.agents import relationship_agent


def get_tool_names() -> set[str]:
    return {
        getattr(tool, "name", None)
        or getattr(tool, "__name__", None)
        or type(tool).__name__
        for tool in relationship_agent.tools
    }


def test_relationship_agent_has_expected_name() -> None:
    assert relationship_agent.name == (
        "relationship_agent"
    )


def test_relationship_agent_uses_expected_model() -> None:
    assert relationship_agent.model == (
        "gemini-flash-latest"
    )


def test_relationship_agent_uses_task_mode() -> None:
    assert relationship_agent.mode == "task"


def test_relationship_agent_has_description() -> None:
    assert relationship_agent.description

    assert (
        "relation"
        in relationship_agent.description.lower()
    )


def test_relationship_agent_has_expected_business_tool(
) -> None:
    tool_names = get_tool_names()

    assert (
        "analyze_table_relationship"
        in tool_names
    )


def test_relationship_agent_has_finish_task_tool() -> None:
    tool_type_names = {
        type(tool).__name__
        for tool in relationship_agent.tools
    }

    assert "FinishTaskTool" in tool_type_names


def test_relationship_agent_has_no_sub_agents() -> None:
    assert relationship_agent.sub_agents == []