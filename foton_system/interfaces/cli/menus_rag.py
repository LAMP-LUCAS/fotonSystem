from colorama import Fore, Style
from foton_system.interfaces.cli.views.tui_layout import TUILayout
from foton_system.interfaces.cli.helpers.error_suggestions import format_error_with_suggestion


class MenuRagHandler:
    def __init__(self, menu):
        self.menu = menu

    def display_rag_menu(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        config = Config()
        current_mode = config.rag_config.get("mode", "minilm")

        TUILayout.clear()
        TUILayout.print_header("CONFIGURACOES RAG")
        self.menu.print_breadcrumb(["Configuracoes", "RAG / Modelo de Embedding"])

        mode_label = {"minilm": "MiniLM", "bgem3": "BGE-M3", "dual": "Ambos (MiniLM + BGE-M3)"}
        current = mode_label.get(current_mode, current_mode)

        options = [
            ("1", "Diagnostico do Sistema (Hardware + Colecoes)"),
            ("2", f"Modo de Embedding: [{current}]"),
            ("3", "Re-indexar Base para Modelo Ativo"),
            ("4", "Status dos Modelos Instalados"),
            ("0", "Voltar"),
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        try:
            tip = self.menu.tip_service.get_random_tip("IA")
            TUILayout.print_tip(tip, "RAG")
        except Exception:
            pass
        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha: {Style.RESET_ALL}").strip()

    def handle_rag_config(self):
        while True:
            choice = self.display_rag_menu()
            if choice == '1':
                self.show_diagnostics()
                input("  Pressione Enter para continuar...")
            elif choice == '2':
                self.show_change_mode_menu()
            elif choice == '3':
                self.reindex_knowledge_base()
                input("  Pressione Enter para continuar...")
            elif choice == '4':
                self.show_model_status()
                input("  Pressione Enter para continuar...")
            elif choice in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def show_diagnostics(self):
        TUILayout.clear()
        TUILayout.print_header("DIAGNOSTICO DO SISTEMA RAG")
        self.menu.print_breadcrumb(["Sistema", "Diagnostico"])

        try:
            from foton_system.core.rag.hardware_profiler import HardwareProfiler, recommended_mode
            profiler = HardwareProfiler()
            hw = profiler.detect()

            self.menu.print_info("  [Hardware Detectado]")
            print(f"    CPU: {hw.cpu_cores} cores")
            print(f"    RAM: {hw.ram_total_gb:.1f}GB total, {hw.ram_available_gb:.1f}GB disponivel")
            print(f"    Disco livre: {hw.disk_free_gb:.1f}GB")
            if hw.has_cuda:
                print(f"    GPU: CUDA {hw.cuda_version}, VRAM: {hw.vram_gb:.1f}GB")
            elif hw.has_mps:
                print("    GPU: MPS (Apple Silicon)")
            elif hw.has_nvidia_gpu:
                print(f"    GPU: {hw.nvidia_gpu_name} (nvidia-smi)")
            else:
                print("    GPU: Nao detectada")
            rec = recommended_mode(hw)
            print(f"    Modo recomendado: {rec}")
            print()
        except Exception as e:
            self.menu.print_error(f"  Erro ao detectar hardware: {format_error_with_suggestion(e)}")

        try:
            from foton_system.core.memory.vector_store import VectorStoreManager
            store = VectorStoreManager()
            diag = store.diagnostic()

            self.menu.print_info(f"  [Colecoes Ativas - Modo: {diag.get('mode', '?')}]")
            stores = diag.get("stores", {})
            if not stores:
                self.menu.print_warning("    Nenhuma colecao ativa encontrada")
            for tag, info in stores.items():
                print(f"    {Fore.CYAN}{tag}{Style.RESET_ALL}:")
                print(f"      Modelo: {info.get('model_name', '?')}")
                print(f"      Colecao: {info.get('collection_name', '?')}")
                print(f"      Chunks: {info.get('total_chunks', 0)}")
                print(f"      Circuit Breaker: {info.get('circuit_breaker_status', '?')}")
                print(f"      Ultima indexacao: {info.get('ultima_indexacao', 'Nunca')}")
        except Exception as e:
            self.menu.print_error(f"  Erro ao consultar diagnostic: {format_error_with_suggestion(e)}")

    def show_change_mode_menu(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        config = Config()
        current_mode = config.rag_config.get("mode", "minilm")

        mode_map = {"1": "minilm", "2": "bgem3", "3": "dual"}
        mode_label = {"minilm": "MiniLM", "bgem3": "BGE-M3", "dual": "Ambos (MiniLM + BGE-M3)"}

        TUILayout.clear()
        TUILayout.print_header("MODO DE EMBEDDING")
        self.menu.print_breadcrumb(["Configuracoes", "RAG", "Modo de Embedding"])

        print(f"  Modo atual: {mode_label.get(current_mode, current_mode)}\n")
        print("  Escolha o modo desejado:")
        print("    1 - MiniLM (leve, 384 dims, ~1GB RAM)")
        print("    2 - BGE-M3 (preciso, 1024 dims, ~4.5GB RAM)")
        print("    3 - Ambos (redundancia, ~5.5GB RAM)")
        print("    0 - Cancelar\n")

        choice = input(f"{Fore.CYAN}>> {Fore.WHITE}Modo: {Style.RESET_ALL}").strip()
        if choice == '0':
            return

        new_mode = mode_map.get(choice)
        if not new_mode:
            self.menu.print_error("  Opção inválida.")
            input("  Enter...")
            return

        if new_mode == current_mode:
            self.menu.print_info("  Modo ja esta ativo.")
            input("  Enter...")
            return

        try:
            from foton_system.core.rag.hardware_profiler import HardwareProfiler
            from foton_system.core.rag.model_router import ModelRouter
            profiler = HardwareProfiler()
            hw = profiler.detect()

            warnings = ModelRouter.validate_pipeline_feasibility(
                {"rag": {"mode": new_mode}}, hw
            )
            if warnings:
                self.menu.print_warning("  [!] Avisos de viabilidade:")
                for w in warnings:
                    print(f"      - {w}")
                if not self.menu.confirm_action("Deseja continuar mesmo assim?", dangerous=True):
                    return
        except Exception as e:
            self.menu.print_error(f"  Erro na validacao: {format_error_with_suggestion(e)}")
            return

        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()

        models_to_check = {"minilm": ["minilm"], "bgem3": ["bgem3"], "dual": ["minilm", "bgem3"]}
        need_install = [m for m in models_to_check.get(new_mode, []) if not registry.is_installed(m)]

        if need_install:
            self.menu.print_info(f"  Modelos a instalar: {', '.join(need_install)}")
            from foton_system.core.rag.download_manager import DownloadManager
            for model_id in need_install:
                entry = registry.get(model_id)
                if entry:
                    size = entry.disk_required_gb
                    self.menu.print_info(f"  {model_id}: ~{size:.1f}GB para download")

                if not self.menu.confirm_action(f"Baixar modelo '{model_id}'?"):
                    self.menu.print_warning(
                        f"  Modelo {model_id} nao instalado. Modo pode nao funcionar."
                    )
                    continue

                hw_profiler = HardwareProfiler()

                def progress_callback(downloaded, total):
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(f"\r    Progresso: {downloaded / 1024 / 1024:.1f}MB / {total / 1024 / 1024:.1f}MB ({pct:.0f}%)", end="")
                    else:
                        print(f"\r    Baixando... {downloaded / 1024 / 1024:.1f}MB", end="")

                report = DownloadManager.ensure_model(model_id, registry, hw_profiler, progress_callback)
                print()
                if report.success:
                    self.menu.print_success(f"  Modelo {model_id} instalado com sucesso!")
                else:
                    self.menu.print_error(f"  Falha ao instalar {model_id}: {report.error}")
                    return

        rag_settings = dict(config.rag_config)
        rag_settings["mode"] = new_mode
        if new_mode == "minilm":
            rag_settings["models"] = {"primary": "minilm", "fallback": []}
        elif new_mode == "bgem3":
            rag_settings["models"] = {"primary": "bgem3", "fallback": ["minilm"]}
        elif new_mode == "dual":
            rag_settings["models"] = {"primary": "minilm", "fallback": ["bgem3"]}

        config.set("rag", rag_settings)
        config.save()
        self.menu.print_success(f"  Modo alterado para: {mode_label[new_mode]}")

        if self.menu.confirm_action("Deseja re-indexar a base para o novo modo agora?"):
            self.reindex_knowledge_base()

    def reindex_knowledge_base(self):
        TUILayout.clear()
        TUILayout.print_header("RE-INDEXAR BASE DE CONHECIMENTO")

        cliente = input("\n  Cliente (ENTER para todos): ").strip()
        scope = f"cliente '{cliente}'" if cliente else "todos os clientes"
        self.menu.print_info(f"  Escaneando documentos para {scope}...")

        if not self.menu.confirm_action("Prosseguir com a indexacao?"):
            return

        try:
            from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
            op = OpIndexKnowledge(actor="User")
            kwargs = {"cliente": cliente} if cliente else {}
            res = op.execute(**kwargs)
            self.menu.print_success(
                f"\n  Indexado: {res.get('files_scanned', 0)} arquivos, {res.get('chunks_created', 0)} chunks criados."
            )
        except Exception as e:
            self.menu.print_error(f"  Erro na indexacao: {format_error_with_suggestion(e)}")

    def _index_knowledge_ui(self):
        self.reindex_knowledge_base()

    def _query_knowledge_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CONSULTAR CONHECIMENTO (RAG)")
        query = input("\n  Pergunta: ").strip()
        if not query:
            return
        cliente = input("  Filtrar por cliente (ENTER para pular): ").strip()
        tipo_doc = input("  Filtrar por tipo doc (INFO/dados/ENTER para pular): ").strip()
        try:
            from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
            op = OpQueryKnowledge(actor="User")
            kwargs = {"query": query}
            if cliente:
                kwargs["cliente"] = cliente
            if tipo_doc:
                kwargs["tipo_doc"] = tipo_doc
            res = op.execute(**kwargs)
            if res['status'] == 'EMPTY':
                self.menu.print_warning("  Nada encontrado.")
            else:
                for i, r in enumerate(res['results'], 1):
                    print(f"\n  [Score: {r['score']:.0%}] — Fonte: {r['source']}")
                    print(f"  {r.get('contexto', r['document'][:200])}")
        except Exception as e:
            self.menu.print_error(f"Erro: {format_error_with_suggestion(e)}")
        input("\nEnter...")

    def show_model_status(self):
        TUILayout.clear()
        TUILayout.print_header("STATUS DOS MODELOS")

        try:
            from foton_system.core.rag.model_registry import ModelRegistry
            registry = ModelRegistry()
            models = registry.list_models()

            self.menu.print_info("  [Modelos Registrados]")
            for model in models:
                installed = registry.is_installed(model.id)
                if installed:
                    status = f"{Fore.GREEN}Instalado{Style.RESET_ALL}"
                else:
                    status = f"{Fore.YELLOW}Nao instalado{Style.RESET_ALL}"
                print(f"    {Fore.CYAN}{model.id}{Style.RESET_ALL}: {model.name}")
                print(f"      Tipo: {model.type} | Dimensoes: {model.dimensions}")
                print(f"      RAM: {model.ram_required_gb:.1f}GB | Disco: {model.disk_required_gb:.1f}GB | GPU: {'Sim' if model.requires_gpu else 'Nao'}")
                print(f"      Status: {status}")
                print()
            from foton_system.core.rag.hardware_profiler import HardwareProfiler
            hw = HardwareProfiler().detect()
            if hw.has_nvidia_gpu and not hw.has_cuda:
                print()
                self.menu.print_warning(
                    f"  GPU NVIDIA detectada ({hw.nvidia_gpu_name}), mas torch e CPU-only."
                )
                self.menu.print_info(
                    "  O suporte CUDA acelera significativamente as operacoes RAG."
                )
                if self.menu.confirm_action("Atualizar torch para versao CUDA?"):
                    from foton_system.infrastructure.dependency_manager import DependencyManager
                    result = DependencyManager.upgrade_torch_to_cuda()
                    if result["success"]:
                        self.menu.print_success(
                            "  torch com CUDA instalado no VENV do AI Pack!"
                        )
                        self.menu.print_info(
                            "  Reinicie o programa se for usar o torch do VENV."
                        )
                    else:
                        self.menu.print_error(
                            f"  Falha: {result['message']}"
                        )
        except Exception as e:
            self.menu.print_error(f"  Erro ao listar modelos: {format_error_with_suggestion(e)}")
