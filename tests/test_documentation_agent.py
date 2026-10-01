from app.agents import documentation_agent


def test_documentation_agent_has_expected_name() -> None:
    assert documentation_agent.name == (
        "documentation_agent"
    )


def test_documentation_agent_has_tool() -> None:
    assert len(documentation_agent.tools) == 1


def test_documentation_agent_uses_expected_model() -> None:
    assert documentation_agent.model == (
        "gemini-flash-latest"
    )