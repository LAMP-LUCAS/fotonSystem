"""
Tests for InfoPatternResolver — Value Object for configurable INFO file naming.

Placeholder system:
  {codCliente}, {nomeCliente}, {aliasCliente}
  {codServico}, {aliasServico}, {aliasCliente}
  {versao}, {revisao}
  {data}, {dataISO}, {ano}, {mes}, {timestamp}, {extensao}

Tests follow RED → GREEN → REFACTOR.
"""

import unittest
import re
from datetime import date


class TestInfoPatternResolverInit(unittest.TestCase):
    """Fase 0.2 — Testes de construção do Value Object."""

    def test_init_com_pattern_valido(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md")
        self.assertIsNotNone(resolver)

    def test_init_pattern_sem_placeholders(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-CLIENTE.md")
        self.assertEqual(resolver.placeholders, set())

    def test_init_com_pattern_vazio_lanca(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        with self.assertRaises(ValueError):
            InfoPatternResolver("")

    def test_init_com_pattern_sem_extensao_lanca(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        with self.assertRaises(ValueError):
            InfoPatternResolver("INFO-CLIENTE-{codCliente}")

    def test_placeholders_property_extrai_todos(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-{codCliente}-{versao}_R{revisao}.md")
        self.assertEqual(resolver.placeholders, {"codCliente", "versao", "revisao"})

    def test_init_pattern_com_todos_placeholders_disponiveis(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("PREFIXO-{codCliente}-{nomeCliente}-{aliasCliente}-{codServico}-{aliasServico}-{versao}-{revisao}-{data}-{dataISO}-{ano}-{mes}-{timestamp}.{extensao}")
        expected = {"codCliente", "nomeCliente", "aliasCliente", "codServico", "aliasServico",
                    "versao", "revisao", "data", "dataISO", "ano", "mes", "timestamp", "extensao"}
        self.assertEqual(resolver.placeholders, expected)


class TestInfoPatternResolverResolve(unittest.TestCase):
    """Fase 0.2 — Testes do método resolve()."""

    def setUp(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        self.resolver = InfoPatternResolver("INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md")

    def test_resolve_substitui_todos_placeholders(self):
        resultado = self.resolver.resolve(codCliente="JOS01", versao="00", revisao="01")
        self.assertEqual(resultado, "INFO-CLIENTE-JOS01_00_R01.md")

    def test_resolve_com_placeholders_parciais(self):
        resultado = self.resolver.resolve(codCliente="MAR01", versao="01", revisao="02")
        self.assertEqual(resultado, "INFO-CLIENTE-MAR01_01_R02.md")

    def test_resolve_placeholder_extra_e_ignorado(self):
        resultado = self.resolver.resolve(codCliente="JOS01", versao="00", revisao="00", extra="ignorado")
        self.assertEqual(resultado, "INFO-CLIENTE-JOS01_00_R00.md")

    def test_resolve_placeholder_faltante_lanca_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.resolver.resolve(codCliente="JOS01")
        self.assertIn("revisao", str(ctx.exception))

    def test_resolve_sem_argumentos_lanca(self):
        with self.assertRaises(ValueError):
            self.resolver.resolve()

    def test_resolve_com_pattern_sem_placeholders(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-FIXO.md")
        resultado = resolver.resolve()
        self.assertEqual(resultado, "INFO-FIXO.md")

    def test_resolve_substitui_placeholders_adjacentes(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("{codCliente}{versao}.md")
        resultado = resolver.resolve(codCliente="ABC", versao="99")
        self.assertEqual(resultado, "ABC99.md")

    def test_resolve_com_extensao_configuravel(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-{codCliente}.{extensao}")
        resultado = resolver.resolve(codCliente="JOS01", extensao="txt")
        self.assertEqual(resultado, "INFO-JOS01.txt")

    def test_resolve_com_placeholder_data(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-{codCliente}_{data}.md")
        hoje = str(date.today())
        resultado = resolver.resolve(codCliente="JOS01", data=hoje)
        self.assertEqual(resultado, f"INFO-JOS01_{hoje}.md")

    def test_resolve_com_placeholder_ano(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-{codCliente}_{ano}.{extensao}")
        resultado = resolver.resolve(codCliente="JOS01", ano="2026", extensao="md")
        self.assertEqual(resultado, "INFO-JOS01_2026.md")


class TestInfoPatternResolverToGlob(unittest.TestCase):
    """Fase 0.2 — Testes do método to_glob()."""

    def test_to_glob_substitui_placeholders_por_asterisco(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md")
        self.assertEqual(resolver.to_glob(), "INFO-CLIENTE-*_*_R*.md")

    def test_to_glob_sem_placeholders_retorna_pattern_inalterado(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-CLIENTE.md")
        self.assertEqual(resolver.to_glob(), "INFO-CLIENTE.md")

    def test_to_glob_placeholders_adjacentes(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("{codCliente}{versao}.md")
        # Adjacent placeholders are collapsed into a single '*'
        self.assertEqual(resolver.to_glob(), "*.md")

    def test_to_glob_com_extensao(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-{codCliente}.{extensao}")
        self.assertEqual(resolver.to_glob(), "INFO-*.*")


class TestInfoPatternResolverToHeader(unittest.TestCase):
    """Fase 0.2 — Testes do método to_header()."""

    def test_to_header_prefixo_com_cerquilha(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md")
        self.assertTrue(resolver.to_header().startswith("## "))

    def test_to_header_mantem_placeholders_como_literais(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        header = InfoPatternResolver("INFO-CLIENTE-{codCliente}.md").to_header()
        self.assertIn("{codCliente}", header)
        self.assertIn("INFO-CLIENTE-{codCliente}.md", header)

    def test_to_header_sem_placeholders(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        header = InfoPatternResolver("INFO-FIXO.md").to_header()
        self.assertEqual(header, "## INFO-FIXO.md")


class TestInfoPatternResolverExtract(unittest.TestCase):
    """Fase 0.2 — Testes do método extract() — operação inversa do resolve()."""

    def test_extract_extrai_valores_do_filename(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md")
        valores = resolver.extract("INFO-CLIENTE-JOS01_00_R01.md")
        self.assertEqual(valores, {"codCliente": "JOS01", "versao": "00", "revisao": "01"})

    def test_extract_filename_nao_correspondente_retorna_dict_vazio(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md")
        valores = resolver.extract("OUTRO-PADRAO-JOS01.md")
        self.assertEqual(valores, {})

    def test_extract_sem_placeholders_retorna_vazio(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-FIXO.md")
        valores = resolver.extract("INFO-FIXO.md")
        self.assertEqual(valores, {})

    def test_extract_extrai_com_extensao(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("INFO-{codCliente}.{extensao}")
        valores = resolver.extract("INFO-JOS01.txt")
        self.assertEqual(valores, {"codCliente": "JOS01", "extensao": "txt"})

    def test_extract_placeholders_adjacentes(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        resolver = InfoPatternResolver("{codCliente}{versao}.md")
        # Non-last groups use .+? (minimal), last uses .+ (remaining)
        # For adjacent placeholders, first captures shortest possible.
        valores = resolver.extract("ABC99.md")
        self.assertEqual(valores, {"codCliente": "A", "versao": "BC99"})


class TestInfoPatternResolverValidate(unittest.TestCase):
    """Fase 0.2 — Testes do método de classe validate()."""

    def test_validate_pattern_valido(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        self.assertTrue(InfoPatternResolver.validate("INFO-{codCliente}.md"))

    def test_validate_pattern_sem_extensao_retorna_false(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        self.assertFalse(InfoPatternResolver.validate("INFO-{codCliente}"))

    def test_validate_pattern_vazio_retorna_false(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        self.assertFalse(InfoPatternResolver.validate(""))

    def test_validate_pattern_com_separador_invalido(self):
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        self.assertTrue(InfoPatternResolver.validate("INFO_{codCliente}.md"))


if __name__ == "__main__":
    unittest.main()
