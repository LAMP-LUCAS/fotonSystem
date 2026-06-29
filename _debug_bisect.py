import subprocess, sys

all_tests = [
    'tests/unit/test_audit_logger.py',
    'tests/unit/test_circuit_breaker.py',
    'tests/unit/test_cli_menus_agnostic.py',
    'tests/unit/test_cli_menus_comprehensive.py',
    'tests/unit/test_client_conformance.py',
    'tests/unit/test_client_crud_info_pattern.py',
    'tests/unit/test_client_service.py',
    'tests/unit/test_client_service_create_client.py',
    'tests/unit/test_config.py',
    'tests/unit/test_create_service_entry.py',
    'tests/unit/test_document_service.py',
    'tests/unit/test_environment_porter.py',
    'tests/unit/test_excel_repository_hidden_folders.py',
    'tests/unit/test_fill_missing_codes.py',
    'tests/unit/test_finance.py',
    'tests/unit/test_finance_service.py',
    'tests/unit/test_form_session.py',
    'tests/unit/test_formatting.py',
    'tests/unit/test_import_client_data.py',
    'tests/unit/test_info_pattern_resolver.py',
    'tests/unit/test_io_resilience.py',
    'tests/unit/test_mcp_client_service.py',
    'tests/unit/test_mcp_integration.py',
    'tests/unit/test_mcp_server.py',
    'tests/unit/test_mcp_services.py',
    'tests/unit/test_op_query_knowledge.py',
    'tests/unit/test_ops_update_client_info.py',
    'tests/unit/test_path_manager_info_pattern.py',
    'tests/unit/test_path_manager_sandbox.py',
    'tests/unit/test_path_traversal.py',
    'tests/unit/test_story012_crud_delete_restore.py',
    'tests/unit/test_story013_crud_financeiro_info_files.py',
    'tests/unit/test_story014_pipeline_sync_unificado.py',
    'tests/unit/test_story015_ux_menus_split_helpers.py',
    'tests/unit/test_story016_ux_menu_restructuring.py',
]

story017 = 'tests/unit/test_story017_integracao_entidades.py'

for i in range(0, len(all_tests), 5):
    batch = all_tests[i:i+5]
    cmd = [sys.executable, '-m', 'pytest'] + batch + [story017, '--tb=line', '-q']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if '1 failed' in result.stdout:
        names = [t.split('/')[-1].replace('.py', '') for t in batch]
        print(f'Batch at {i}: {names} => TRIGGERED')
        for line in result.stdout.split('\n'):
            if 'FAILED' in line and 'test_get_services' in line:
                print(f'  {line}')
    else:
        names = [t.split('/')[-1].replace('.py', '') for t in batch]
        print(f'Batch at {i}: {names} => OK')
