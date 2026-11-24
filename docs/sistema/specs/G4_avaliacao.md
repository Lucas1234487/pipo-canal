# G4. Gerente de Avaliação

Missão: achar o que faz alguém deslizar, o que está errado e o que soa mal, ANTES de publicar, e dizer ao Diretor se o vídeo passa no piso (GUARDRAILS seção 3). Nota de plateia orienta melhoria; não trava publicação.

## Por que o Gemini aqui
O Gemini assiste ao MP4 com som; o Claude só vê quadros. No teste de 24/11/2026 a nota do Gemini não acompanhou a do Lucas, mas ele achou problemas reais de som e de ritmo. Então: usar para achar problemas, não para dar a nota final.

## Passos (por vídeo)
1. `python3 kit/gemini.py video --arquivo WORK/final_pt.mp4 --prompt docs/sistema/specs/prompt_plateia.txt > WORK/avaliacao_gemini.md`.
2. Ler o relatório e cruzar com WORK/fatos.md e o qa_check. Classificar cada problema: GRAVE (fato errado, ofensa, guardrail, trecho quebrado ou incompreensível), MÉDIO (segundo em que a maioria desliza, som ruim) ou LEVE.
3. Escrever WORK/avaliacao.md: veredito do piso (PASSA ou NÃO PASSA e por quê), os 3 segundos mais perigosos, a média do Gemini e 1 correção barata que valeria a pena (só cenas.json ou mixagem, sem regravar).
Sem Gemini: rodar `python3 kit/plateia_kit.py WORK pt` e um único subagente Claude com as 5 personas (FUNCOES.md seção 9), contando como um dos 3 agentes do dia.

## Entrega
WORK/avaliacao.md. Ao Diretor: 3 linhas por vídeo (piso, média, a correção que vale).

## Calibração
Toda semana, comparar a média do Gemini com a nota do Lucas (quando houver) e as métricas reais (G6). Registrar na BASE se o Gemini erra para cima ou para baixo e quanto.
