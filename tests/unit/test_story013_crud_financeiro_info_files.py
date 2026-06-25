import pytest
from pathlib import Path
from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
from foton_system.modules.finance.application.ports.finance_repository_port import FinanceRepositoryPort
from foton_system.modules.clients.application.use_cases.client_crud import update_client_info_file


# @story: STORY-013
# @rule: RULE-DOMAIN-2.5, RULE-DOMAIN-2.6


# ==============================================================================
# Fake Repositories for testing
# ==============================================================================

class FakeFinanceRepository(FinanceRepositoryPort):
    """In-memory fake repository for finance tests."""

    def __init__(self):
        self._entries = []

    def save_entry(self, client_path, entry, headers):
        self._entries.append(dict(zip(headers, entry)))

    def get_entries(self, client_path):
        return self._entries


# ==============================================================================
# RULE-DOMAIN-2.5: Financeiro — Duplicate Detection
# ==============================================================================

class TestFinanceiroDuplicateDetection:

    def test_add_entry_duplicate_detected(self):
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        client_path = Path('/fake')

        result1 = service.add_entry(client_path, 'Pagamento', 1000.0, 'ENTRADA')
        assert 'duplicate_warning' not in result1

        result2 = service.add_entry(client_path, 'Pagamento', 1000.0, 'ENTRADA')
        assert result2.get('duplicate_warning') is True

    def test_add_entry_different_description_no_warning(self):
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        client_path = Path('/fake')

        service.add_entry(client_path, 'Pagamento A', 1000.0, 'ENTRADA')
        result = service.add_entry(client_path, 'Pagamento B', 1000.0, 'ENTRADA')
        assert 'duplicate_warning' not in result

    def test_add_entry_different_value_no_warning(self):
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        client_path = Path('/fake')

        service.add_entry(client_path, 'Pagamento', 1000.0, 'ENTRADA')
        result = service.add_entry(client_path, 'Pagamento', 500.0, 'ENTRADA')
        assert 'duplicate_warning' not in result

    def test_add_entry_same_data_different_type_no_warning(self):
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        client_path = Path('/fake')

        service.add_entry(client_path, 'Transferencia', 1000.0, 'ENTRADA')
        result = service.add_entry(client_path, 'Transferencia', 1000.0, 'SAIDA')
        assert 'duplicate_warning' in result


# ==============================================================================
# RULE-DOMAIN-2.6: INFO File — Section Operations
# ==============================================================================

@pytest.fixture
def info_file(tmp_path):
    """Create a temporary INFO file with sample sections."""
    content = (
        "## DADOS DO CLIENTE\n"
        "@nomeCliente: João\n"
        "@cpf: 123.456.789-00\n"
        "\n"
        "## Notas de Reunião\n"
        "Cliente solicitou orçamento.\n"
        "Preferência por estilo moderno.\n"
        "\n"
        "## Dados Técnicos\n"
        "@areaTotal: 200m²\n"
        "@estilo: Moderno\n"
    )
    info = tmp_path / "INFO-CLIENTE-TESTE_01_R00.md"
    info.write_text(content, encoding="utf-8")
    return tmp_path


class TestUpdateClientInfoReplaceSection:

    def test_replace_existing_section_content(self, info_file):
        result = update_client_info_file(
            info_file, "Notas de Reunião", "Nova observação importante.", operacao="replace"
        )
        assert result.endswith(".bak")

        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "Nova observação importante." in content
        assert "Cliente solicitou orçamento." not in content

    def test_replace_last_section(self, info_file):
        update_client_info_file(
            info_file, "Dados Técnicos", "@areaTotal: 300m²", operacao="replace"
        )
        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "@areaTotal: 300m²" in content
        assert "@areaTotal: 200m²" not in content

    def test_replace_nonexistent_section_raises(self, info_file):
        with pytest.raises(ValueError, match="not found"):
            update_client_info_file(
                info_file, "Seção Inexistente", "conteúdo", operacao="replace"
            )


class TestUpdateClientInfoRemoveSection:

    def test_remove_existing_section(self, info_file):
        update_client_info_file(
            info_file, "Notas de Reunião", "", operacao="remove"
        )
        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "Notas de Reunião" not in content
        assert "Cliente solicitou orçamento." not in content
        assert "DADOS DO CLIENTE" in content
        assert "Dados Técnicos" in content

    def test_remove_first_section(self, info_file):
        update_client_info_file(
            info_file, "DADOS DO CLIENTE", "", operacao="remove"
        )
        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "DADOS DO CLIENTE" not in content
        assert "@nomeCliente" not in content
        assert "Notas de Reunião" in content

    def test_remove_last_section(self, info_file):
        update_client_info_file(
            info_file, "Dados Técnicos", "", operacao="remove"
        )
        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "Dados Técnicos" not in content
        assert "@areaTotal" not in content
        assert "Notas de Reunião" in content

    def test_remove_nonexistent_section_raises(self, info_file):
        with pytest.raises(ValueError, match="not found"):
            update_client_info_file(
                info_file, "Seção Inexistente", "", operacao="remove"
            )


class TestUpdateClientInfoFieldUpdate:

    def test_update_field_with_semicolon(self, info_file):
        update_client_info_file(
            info_file, "", "@areaTotal: 300m²", operacao="field", campo="areaTotal"
        )
        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "@areaTotal: 300m²" in content

    def test_update_field_with_colon(self, info_file):
        update_client_info_file(
            info_file, "", "João Silva", operacao="field", campo="nomeCliente"
        )
        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "@nomeCliente: João Silva" in content

    def test_update_nonexistent_field_raises(self, info_file):
        with pytest.raises(ValueError, match="not found"):
            update_client_info_file(
                info_file, "", "valor", operacao="field", campo="campoInexistente"
            )

    def test_field_update_without_campo_raises(self, info_file):
        with pytest.raises(ValueError, match="required"):
            update_client_info_file(
                info_file, "", "valor", operacao="field", campo=""
            )


class TestUpdateClientInfoAppendBackwardCompat:

    def test_append_to_existing_section(self, info_file):
        update_client_info_file(info_file, "Notas de Reunião", "Nova anotação.")
        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "Nova anotação." in content
        assert "Cliente solicitou orçamento." in content

    def test_append_new_section(self, info_file):
        update_client_info_file(info_file, "Aprovações", "Projeto aprovado em 2026-06-25.")
        content = (info_file / "INFO-CLIENTE-TESTE_01_R00.md").read_text(encoding="utf-8")
        assert "Aprovações" in content
        assert "Projeto aprovado em 2026-06-25." in content

    def test_append_creates_backup(self, info_file):
        result = update_client_info_file(info_file, "Notas de Reunião", "Anotação.")
        backup = info_file / result
        assert backup.exists()
        original_content = backup.read_text(encoding="utf-8")
        assert "Nova anotação." not in original_content
        assert "Cliente solicitou orçamento." in original_content


class TestUpdateClientInfoBackup:

    def test_backup_created_on_replace(self, info_file):
        result = update_client_info_file(
            info_file, "Notas de Reunião", "novo", operacao="replace"
        )
        assert (info_file / result).exists()

    def test_backup_created_on_remove(self, info_file):
        result = update_client_info_file(
            info_file, "Notas de Reunião", "", operacao="remove"
        )
        assert (info_file / result).exists()

    def test_backup_created_on_field_update(self, info_file):
        result = update_client_info_file(
            info_file, "", "300m²", operacao="field", campo="areaTotal"
        )
        assert (info_file / result).exists()
