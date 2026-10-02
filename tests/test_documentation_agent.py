from app.agents import documentation_agent


def test_documentation_agent_has_expected_name() -> None:
    assert documentation_agent.name == (
        "documentation_agent"
    )


def test_documentation_agent_has_expected_business_tool() -> None:
    tool_names = {
        getattr(tool, "name", None)
        or getattr(tool, "__name__", None)
        for tool in documentation_agent.tools
    }

    assert (
        "analyze_documentation_file"
        in tool_names
    )


def test_documentation_agent_uses_expected_model() -> None:
    assert documentation_agent.model == (
        "gemini-flash-latest"
    )