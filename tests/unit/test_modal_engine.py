import unittest
from foton_system.interfaces.cli.modal import ModalEngine, ModalMode, ModalBuffer


class TestModalEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ModalEngine({"modal_enabled": True, "modal_theme": "dark"})

    def test_inicializacao_padrao(self):
        """RULE-TUI-1.4 e 1.5: modo padrão NORMAL e buffer inicial presente."""
        self.assertEqual(self.engine.current_mode, ModalMode.NORMAL)
        self.assertGreaterEqual(len(self.engine.buffers), 1)
        self.assertIsNotNone(self.engine.active_buffer)
        self.assertEqual(len(self.engine.splits), 1)

    def test_fallback_quando_desabilitado(self):
        """RULE-TUI-1.3: modal_enabled false respeita config."""
        engine_disabled = ModalEngine({"modal_enabled": False})
        self.assertFalse(engine_disabled.modal_enabled)

    def test_navegacao_normal_j_k_gg_G(self):
        """RULE-TUI-2.2 e 2.4: navegacao vertical."""
        buf = ModalBuffer("Teste", ["Linha 1", "Linha 2", "Linha 3", "Linha 4"])
        self.engine.add_buffer(buf)

        self.assertEqual(buf.cursor_line, 0)
        self.engine.handle_key("j")
        self.assertEqual(buf.cursor_line, 1)
        self.engine.handle_key("j")
        self.assertEqual(buf.cursor_line, 2)
        self.engine.handle_key("k")
        self.assertEqual(buf.cursor_line, 1)

        # G -> fim
        self.engine.handle_key("G")
        self.assertEqual(buf.cursor_line, 3)

        # gg -> topo
        self.engine.handle_key("g")
        self.engine.handle_key("g")
        self.assertEqual(buf.cursor_line, 0)

    def test_transicoes_de_modo(self):
        """RULE-TUI-2.9, 2.12, 2.17: i, v, :, Esc."""
        # NORMAL -> INSERT via 'i'
        self.engine.handle_key("i")
        self.assertEqual(self.engine.current_mode, ModalMode.INSERT)

        # INSERT -> NORMAL via Esc
        self.engine.handle_key("Esc")
        self.assertEqual(self.engine.current_mode, ModalMode.NORMAL)

        # NORMAL -> VISUAL via 'v'
        self.engine.handle_key("v")
        self.assertEqual(self.engine.current_mode, ModalMode.VISUAL)

        # VISUAL -> NORMAL via Esc
        self.engine.handle_key("Esc")
        self.assertEqual(self.engine.current_mode, ModalMode.NORMAL)

        # NORMAL -> COMANDO via ':'
        self.engine.handle_key(":")
        self.assertEqual(self.engine.current_mode, ModalMode.COMANDO)
        self.assertEqual(self.engine.cmdline, ":")

    def test_modo_insert_insere_caracteres_e_newline(self):
        """Modo INSERT insere texto e cria quebras de linha."""
        buf = ModalBuffer("Edicao", [""])
        self.engine.add_buffer(buf)
        self.engine.set_mode(ModalMode.INSERT)

        for ch in "Foton":
            self.engine.handle_key(ch)
        self.assertEqual(buf.lines[0], "Foton")
        self.assertTrue(buf.modified)

        self.engine.handle_key("Enter")
        self.assertEqual(len(buf.lines), 2)
        self.assertEqual(buf.cursor_line, 1)

    def test_linha_de_comando_execucao(self):
        """Comandos :w, :q, :help e troca de buffers."""
        buf1 = ModalBuffer("Buffer1", ["Texto 1"])
        buf2 = ModalBuffer("Buffer2", ["Texto 2"])
        self.engine.add_buffer(buf1)
        self.engine.add_buffer(buf2)

        # :w
        res_w = self.engine.execute_command(":w")
        self.assertEqual(res_w, "SAVED")

        # :b Buffer1
        res_b = self.engine.execute_command(":b Buffer1")
        self.assertEqual(res_b, "BUFFER_SWITCH:Buffer1")
        self.assertEqual(self.engine.active_buffer.name, "Buffer1")

        # :help
        res_help = self.engine.execute_command(":help")
        self.assertEqual(res_help, "HELP")

        # :q
        res_q = self.engine.execute_command(":q")
        self.assertEqual(res_q, "QUIT")

    def test_busca_com_barra(self):
        """RULE-TUI-2.16: busca com / e navegacao com n e N."""
        buf = ModalBuffer("Busca", ["arquitetura moderna", "design de interiores", "outra arquitetura"])
        self.engine.add_buffer(buf)

        res = self.engine.execute_command("/arquitetura")
        self.assertEqual(res, "SEARCH:2")
        self.assertEqual(buf.cursor_line, 0)

        # n -> proximo match
        self.engine.handle_key("n")
        self.assertEqual(buf.cursor_line, 2)

        # N -> anterior
        self.engine.handle_key("N")
        self.assertEqual(buf.cursor_line, 0)

    def test_render_status_bar(self):
        """RULE-TUI-2.18: status bar renderizada."""
        bar = self.engine.render_status_bar()
        self.assertIn("NORMAL", bar)
        self.assertIn(self.engine.active_buffer.name, bar)


if __name__ == '__main__':
    unittest.main()
