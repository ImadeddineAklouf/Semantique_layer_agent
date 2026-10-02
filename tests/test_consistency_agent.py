from app.agents import consistency_agent


def test_consistency_agent_has_expected_name() -> None:
    assert consistency_agent.name == (
        "consistency_agent"
    )


def test_consistency_agent_has_expected_business_tool() -> None:
    tool_names = {
        getattr(tool, "name", None)
        or getattr(tool, "__name__", None)
        for tool in consistency_agent.tools
    }

    assert (
        "compare_csv_with_documentation"
        in tool_names
    )


def test_consistency_agent_uses_expected_model() -> None:
    assert consistency_agent.model == (
        "gemini-flash-latest"
    )


def test_consistency_agent_has_description() -> None:
    assert consistency_agent.description