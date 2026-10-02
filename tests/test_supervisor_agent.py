from app.agents import supervisor_agent


def test_supervisor_has_expected_name() -> None:
    assert supervisor_agent.name == (
        "semantic_layer_supervisor"
    )


def test_supervisor_uses_expected_model() -> None:
    assert supervisor_agent.model == (
        "gemini-flash-latest"
    )


def test_supervisor_has_expected_sub_agents() -> None:
    sub_agent_names = {
        agent.name
        for agent in supervisor_agent.sub_agents
    }

    assert sub_agent_names == {
        "metadata_agent",
        "documentation_agent",
        "consistency_agent",
        "relationship_agent",
        "semantic_model_agent",
        "lookml_generator_agent",
    }

def test_sub_agents_have_supervisor_as_parent() -> None:
    for agent in supervisor_agent.sub_agents:
        assert (
            agent.parent_agent
            is supervisor_agent
        )


def test_relationship_agent_is_attached_to_supervisor(
) -> None:
    relationship_agents = [
        agent
        for agent in supervisor_agent.sub_agents
        if agent.name == "relationship_agent"
    ]

    assert len(relationship_agents) == 1

    assert (
        relationship_agents[0].parent_agent
        is supervisor_agent
    )


def test_supervisor_has_description() -> None:
    assert supervisor_agent.description


def test_supervisor_has_instructions() -> None:
    assert supervisor_agent.instruction

def test_semantic_model_agent_is_attached_to_supervisor(
) -> None:
    semantic_model_agents = [
        agent
        for agent in supervisor_agent.sub_agents
        if agent.name == "semantic_model_agent"
    ]

    assert len(semantic_model_agents) == 1

    assert (
        semantic_model_agents[0].parent_agent
        is supervisor_agent
    )

def test_lookml_generator_agent_is_attached_to_supervisor(
) -> None:
    matching_agents = [
        agent
        for agent in supervisor_agent.sub_agents
        if agent.name == "lookml_generator_agent"
    ]

    assert len(matching_agents) == 1

    assert (
        matching_agents[0].parent_agent
        is supervisor_agent
    )