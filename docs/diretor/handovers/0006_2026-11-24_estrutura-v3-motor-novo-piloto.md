# Handover 0006 (24/11/2026 tarde/noite): estrutura v3, motor novo e o piloto

## Decisões do Lucas
- Publica sozinho, todo santo dia; ele só veta (segurar.json). 3 pilares por dia (momento, história, conhecimento).
- Estrutura obrigatória: Diretor -> Gerente de Produção -> O1 Roteiro e Fala, O2 Cenário, O3 Sonoplastia, O4 Montagem -> QA-Claude novo + QA-Gemini. Subagente não abre subagente: o Diretor faz a ponte e o gerente confere via SendMessage (funcionou no piloto).
- Interação em todo vídeo (like/comentário/compartilhar natural), errinho de cenário ou ortografia ~1 a cada 5, duplo sentido leve opcional, memes só redesenhados, imagens CC0/NASA, fundo condizente com a história, imersão com foto real, atualização constante, exceção única "Neymaro".
- Revisão completa do motor em docs/diretor/REVISAO_LUCAS_2026-11-24.md.

## O que entrou no motor
cenarios2 (24+ cenários com vida, camadas, âncoras, porta), fundos (14 animados, foto em tela cheia, mergulho, transições), humano2 + elenco (assinatura, traços, 16+ presets), memes (20), reações de meme com 20 sons CC0 + "fa" gerado, brilho de cena, chuva, split, mapa, árvore/casa soltas, sons audíveis no celular (kit/checa_sons.py), whoosh de 1 passada.

## Piloto ep008 (C) "Dá pra ver o Natal do espaço"
Feito inteiro na estrutura nova. QA-Claude APROVA (fatos conferidos nas fontes NASA), Gemini 7,5 (leu "MOTV" por causa da fonte: falso positivo). Agendado 25/11 12:07: https://youtube.com/shorts/i5Q7cLsiN9g. Briefings e bilhetes em episodios/ep008/.

## Pendente
- Mostrar ao Lucas a página de revisão v2 (o que mudou depois da revisão dele).
- Backlog no G3 (loudnorm de 2 passadas, cache no ônibus/carro).
- Tarefa de publicação em lote ainda não está presa ao PC do Lucas (a produção agenda sozinha quando o Chrome responde).
