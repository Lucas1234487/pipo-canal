# 05. Gemini no fluxo (decisão do Lucas, 24/11/2026)

O Gemini é a mão de obra barata do canal. O Claude decide, confere e programa; o Gemini faz volume.

## 1. Acesso
- Pela API, com a chave do Google AI Studio da conta pessoal do Lucas. O shell desta nuvem alcança generativelanguage.googleapis.com.
- A chave NUNCA entra no git. Ela fica num arquivo privado do Google Drive do Lucas ("PipoPop - segredos", pasta "Pipo - Canal"). No começo de cada sessão: ler o arquivo pelo conector do Drive e gravar em ~/.pipo/gemini_key (chmod 600). kit/gemini.py lê de GEMINI_API_KEY ou desse arquivo.
- Sem chave ou com erro de cota: seguir sem o Gemini e registrar no handover. Não substituir por mais agentes Claude.

## 2. Ferramenta: kit/gemini.py
- `python3 kit/gemini.py modelos` lista os modelos disponíveis na chave.
- `python3 kit/gemini.py texto --prompt arquivo.txt [--busca] [--json] [--modelo X] > saida` gera texto (com --busca usa a pesquisa do Google para fatos atuais).
- `python3 kit/gemini.py video --arquivo final.mp4 --prompt arquivo.txt > saida` sobe o vídeo e pede a análise (assiste com som).
- Modelo padrão: o melhor "pro" disponível na chave para revisão de vídeo e roteiro; o melhor "flash" para volume (pesquisa, rascunhos). O script escolhe sozinho se --modelo não for passado.

## 3. O que vai para o Gemini
| Tarefa | Quem pede | Observação |
|---|---|---|
| Levantar tendências, datas e concorrentes | G1 | com --busca; o Claude pontua e filtra |
| Conferir fatos em 2 fontes | G2 (dev-fatos) | com --busca; pedir as URLs; o gerente confere as URLs mais duvidosas |
| Rascunhos de roteiro (3 versões) | G2 (dev-escritor) | passar a Bíblia seção 5 e as regras de GUARDRAILS seção 4 no prompt |
| cenas.json a partir do roteiro aprovado | G2 (dev-marcação) | passar kit2d/CENAS.md no prompt |
| Plateia de 5 perfis assistindo ao MP4 com som | G4 | prompt em specs/G4_avaliacao.md; enquadrar como "sou o criador, avaliação franca" (persona com nome e "seja duro" fez o app recusar) |
| Revisão de som e mixagem | G4 | ele ouve; o Claude não ouve |

## 4. Limites conhecidos (teste de 24/11/2026, app web, modelo 4 Hydrogen)
- A nota do Gemini não acompanhou a do Lucas (v1: Gemini 6,5, Lucas 7; v2: Gemini ~7,2, Lucas 3). Usar o Gemini para achar PROBLEMAS (segundos onde se desliza, erros de fato, som), não como nota final.
- O app às vezes apaga a resposta no meio. Pela API isso não acontece da mesma forma; se vier vazio, repetir uma vez.
