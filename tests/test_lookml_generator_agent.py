from app.agents import lookml_generator_agent


def get_tool_names() -> set:
    """
    Retourne les noms des Tools attachés
    au LookML Generator Agent.
    """

    return {
        getattr(tool, "name", None)
        or getattr(tool, "__name__", None)
        or type(tool).__name__
        for tool in lookml_generator_agent.tools
    }


def test_lookml_generator_agent_has_expected_name(
) -> None:
    assert lookml_generator_agent.name == (
        "lookml_generator_agent"
    )


def test_lookml_generator_agent_uses_expected_model(
) -> None:
    assert lookml_generator_agent.model == (
        "gemini-flash-latest"
    )


def test_lookml_generator_agent_uses_task_mode(
) -> None:
    assert lookml_generator_agent.mode == "task"


def test_lookml_generator_agent_has_description(
) -> None:
    assert lookml_generator_agent.description

    assert (
        "lookml"
        in lookml_generator_agent.description.lower()
    )


def test_lookml_generator_agent_has_instruction(
) -> None:
    assert lookml_generator_agent.instruction

    assert (
        "generate_lookml_project"
        in lookml_generator_agent.instruction
    )


def test_lookml_generator_agent_has_business_tool(
) -> None:
    tool_names = get_tool_names()

    assert (
        "generate_lookml_project"
        in tool_names
    )


def test_lookml_generator_agent_has_finish_task_tool(
) -> None:
    tool_type_names = {
        type(tool).__name__
        for tool in lookml_generator_agent.tools
    }

    assert "FinishTaskTool" in tool_type_names


def test_lookml_generator_agent_has_no_sub_agents(
) -> None:
    assert lookml_generator_agent.sub_agents == []