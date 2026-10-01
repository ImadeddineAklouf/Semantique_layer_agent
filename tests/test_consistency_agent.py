from app.agents import consistency_agent


def test_consistency_agent_has_expected_name() -> None:
    assert consistency_agent.name == (
        "consistency_agent"
    )


def test_consistency_agent_has_one_tool() -> None:
    assert len(consistency_agent.tools) == 1


def test_consistency_agent_uses_expected_model() -> None:
    assert consistency_agent.model == (
        "gemini-flash-latest"
    )


def test_consistency_agent_has_description() -> None:
    assert consistency_agent.description