from app.agents import semantic_model_agent


def get_tool_names() -> set:
    return {
        getattr(tool, "name", None)
        or getattr(tool, "__name__", None)
        or type(tool).__name__
        for tool in semantic_model_agent.tools
    }


def test_semantic_model_agent_has_expected_name() -> None:
    assert semantic_model_agent.name == (
        "semantic_model_agent"
    )


def test_semantic_model_agent_uses_expected_model() -> None:
    assert semantic_model_agent.model == (
        "gemini-flash-latest"
    )


def test_semantic_model_agent_uses_task_mode() -> None:
    assert semantic_model_agent.mode == "task"


def test_semantic_model_agent_has_description() -> None:
    assert semantic_model_agent.description

    assert (
        "sémantique"
        in semantic_model_agent.description.lower()
    )


def test_semantic_model_agent_has_business_tool() -> None:
    assert (
        "build_semantic_model_from_sources"
        in get_tool_names()
    )


def test_semantic_model_agent_has_finish_task_tool() -> None:
    tool_type_names = {
        type(tool).__name__
        for tool in semantic_model_agent.tools
    }

    assert "FinishTaskTool" in tool_type_names


def test_semantic_model_agent_has_no_sub_agents() -> None:
    assert semantic_model_agent.sub_agents == []