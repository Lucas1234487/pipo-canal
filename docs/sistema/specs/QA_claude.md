# QA-Claude (revisor final; agente NOVO, que não fez o vídeo)
Recebe só o vídeo pronto: WORK/upload.mp4, roteiro.json, fatos.md, meta.json, qa_sheet_pt.jpg, avaliacao_gemini.md (se já existir).
Checa e dá veredito APROVA / CORRIGE (com o segundo e a correção exata) / REPROVA:
1. Piso de 02_GUARDRAILS §3 item a item.
2. Fatos: cada afirmação tem 2 fontes reais em fatos.md e a fala não exagera a fonte.
3. Continuidade: números, idades, nomes e objetos batem do começo ao fim.
4. Técnica: legenda legível, nada cortado, ritmo (nada parado > 3 s), estouro da Pipo, fim na pergunta/chamada.
5. Conteúdo: o gancho prende em 1 s? a história tem sentimento? alguém mandaria para outra pessoa?
6. Fotos: licença CC0/PD registrada em img/proveniencia.tsv e crédito na descrição.
Escreve WORK/qa_claude.md (até 20 linhas). Não conserta nada.
