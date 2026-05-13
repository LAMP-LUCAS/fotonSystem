"""
Unit tests for FormSession domain model.
"""

import pytest
from foton_system.modules.documents.domain.models.form_session import FormSession

def test_parse_markdown_variables():
    md = """# Title
@nomeCliente; Nome do Cliente
@areaTotal; Área do terreno
Some text
@ACEqv; [calculo: @areaTotal * 0.7] Área equivalente
"""
    session = FormSession()
    session.parse_markdown(md)
    
    assert len(session.fields) == 3
    assert session.fields[0].name == "nomeCliente"
    assert session.fields[1].name == "areaTotal"
    assert session.fields[2].is_calculated is True

def test_navigation():
    md = "@var1; desc\n@var2; desc"
    session = FormSession()
    session.parse_markdown(md)
    
    assert session.cursor == 0
    assert session.get_current_field().name == "var1"
    
    session.next()
    assert session.cursor == 1
    assert session.get_current_field().name == "var2"
    
    session.next() # Limit
    assert session.cursor == 1
    
    session.prev()
    assert session.cursor == 0

def test_calculation_logic():
    md = """@area; 100
@preco; 2
@total; [calculo: @area * @preco] Total
"""
    session = FormSession()
    session.parse_markdown(md)
    
    session.cursor = 0 # @area
    session.update_current("100")
    
    session.next() # @preco
    session.update_current("5")
    
    # @total deve ser 500.00
    total_field = session.fields[2]
    assert total_field.current_value == "500.00"

def test_markdown_regeneration():
    md = """# Header
@nome;Fulano
Texto extra
@total;[calculo: 10*10] Valor"""
    
    session = FormSession()
    session.parse_markdown(md)
    session.update_current("Lucas")
    
    new_md = session.generate_markdown()
    assert "# Header" in new_md
    assert "@nome;Lucas" in new_md
    assert "@total;[calculo: 10*10] Valor" in new_md
    assert "Texto extra" in new_md
