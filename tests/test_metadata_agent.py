from app.agents import metadata_agent


def get_tool_names() -> set[str]:
    """
    Retourne les noms des Tools attachés au Metadata Agent.

    Une fonctionlise généralement __name__.
    Un Tool ADK sous forme d'objet peut exposer name.
    """

    return {
        getattr(tool, "name", None)
        or getattr(tool, "__name__", None)
        or type(tool).__name__
        for tool in metadata_agent.tools
    }


def test_metadata_agent_has_expected_name() -> None:
    """
    Vérifie l'identifiant interne du Metadata Agent.
    """

    assert metadata_agent.name == "metadata_agent"


def test_metadata_agent_uses_expected_model() -> None:
    """
    Vérifie le modèle configuré pour l'agent.
    """

    assert metadata_agent.model == (
        "gemini-flash-latest"
    )


def test_metadata_agent_has_description() -> None:
    """
    Vérifie que l'agent possède une description utile
    pour le routage du Supervisor Agent.
    """

    assert metadata_agent.description

    assert (
        "CSV"
        in metadata_agent.description
    )


def test_metadata_agent_has_instruction() -> None:
    """
    Vérifie que l'agent possède des instructions.
    """

    assert metadata_agent.instruction


def test_metadata_agent_has_expected_business_tool() -> None:
    """
    Vérifie la présence du Tool métier analyze_csv_file.

    Le nombre total de Tools n'est pas vérifié, car ADK ajoute
    automatiquement FinishTaskTool lorsque mode='task'.
    """

    tool_names = get_tool_names()

    assert "analyze_csv_file" in tool_names


def test_metadata_agent_uses_task_mode() -> None:
    """
    Vérifie que le sous-agent retourne automatiquement
    le contrôle au Supervisor après sa tâche.
    """

    assert metadata_agent.mode == "task"


def test_metadata_agent_has_finish_task_tool() -> None:
    """
    Vérifie qu'ADK a ajouté un Tool de fin de tâche.

    Le nom exact peut varier légèrement selon la version ADK.
    """

    tool_names = get_tool_names()

    normalized_tool_names = {
        tool_name.lower()
        for tool_name in tool_names
        if tool_name
    }

    assert any(
        "finish" in tool_name
        and "task" in tool_name
        for tool_name in normalized_tool_names
    )


def test_metadata_agent_has_supervisor_as_parent() -> None:
    """
    Vérifie que le Metadata Agent appartient à la hiérarchie
    du Semantic Layer Supervisor.
    """

    assert metadata_agent.parent_agent is not None

    assert (
        metadata_agent.parent_agent.name
        == "semantic_layer_supervisor"
    )


def test_metadata_agent_has_no_sub_agents() -> None:
    """
    Vérifie que le Metadata Agent reste un agent spécialisé
    terminal, sans sous-agents.
    """

    assert metadata_agent.sub_agents == []