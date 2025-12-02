# Guia de Deploy e Releases

Este guia descreve como gerar uma nova versão executável do [**FOTON System**](../README.md) e distribuí-la via GitHub Releases de acordo com os [requisitos de arquitetura](concepts.md) do sistema.

## 1. Preparação

Certifique-se de que todas as dependências estão instaladas, incluindo o `pyinstaller`:

```bash
pip install -r requirements.txt
```

## 2. Gerar o Executável

Utilize o script de build automatizado para compilar o sistema em um único arquivo `.exe`.

1. Abra o terminal na raiz do projeto.
2. Execute o script:

    ```bash
    python foton_system/scripts/build.py
    ```

3. Aguarde o processo. O executável será gerado na pasta `dist/` com o nome `foton_system.exe`.

## 3. Testar

Antes de liberar, teste o executável:

1. Vá até a pasta `dist/`.
2. Execute `foton_system.exe`.
3. Verifique se todas as funcionalidades (menus, geração de documentos) estão operando corretamente.

## 4. Criar Release no GitHub

1. **Commit e Push:** Certifique-se de que todo o código está commitado e enviado para o repositório.
2. **Tag:** Crie uma tag para a versão (ex: v1.0.0).

    ```bash
    git tag v1.0.0
    git push origin v1.0.0
    ```

3. **GitHub:**
    * Acesse a página do repositório no GitHub.
    * Clique em **Releases** (barra lateral direita).
    * Clique em **Draft a new release**.
    * Selecione a tag que você criou (`v1.0.0`).
    * Dê um título (ex: "Versão 1.0.0 - Lançamento Inicial").
    * Descreva as mudanças.
    * **Anexar Binários:** Arraste o arquivo `dist/foton_system.exe` para a área de upload.
    * Clique em **Publish release**.

## 5. Atualização do Cliente

O usuário final deve:

1. Acessar a página de Releases do GitHub.
2. Baixar o `foton_system.exe` mais recente.
3. Substituir o arquivo antigo em sua máquina.

---

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
