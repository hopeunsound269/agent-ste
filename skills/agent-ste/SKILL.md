---
name: agent-ste
version: 1.0.1
description: |
  Write or rewrite technical and agent-facing text in ASD-STE100 Simplified
  Technical English. Use for documentation, READMEs, runbooks, error messages,
  release notes, incident reports, tool descriptions, system prompts, and
  inter-agent instructions. Also use when the user says "STE", "ASD-STE100",
  "simplify this", or asks for text that a machine or non-native reader must
  parse without help. Enforces 20/25-word sentence limits, one word one
  meaning, simple tenses, active voice, condition before command, and a
  mandatory final search gate.
license: MIT
metadata:
  standard: ASD-STE100 Issue 9 (2025-01-15)
---

# Agent STE — write text that survives one read

ASD-STE100 is the controlled language that aerospace uses so a tired mechanic cannot misread an instruction. This skill applies the same rules to software text for two readers who cannot ask questions:

1. A tired human who is not a native English speaker.
2. A downstream system — an LLM agent, a translation pipeline, a parser — that reads your text with no back-channel.

Each sentence must survive one read. If a sentence has two possible meanings, one reader will pick the wrong one.

## Procedure

Do these steps in order. Step 5 is not optional.

1. **Classify each passage.** Procedural or descriptive (table below). Do not mix them in one passage.
2. **Choose your words before you draft.** Use the vocabulary table. Pick one word for each concept. Use no other word for that concept anywhere in the document.
3. **Draft with the writing rules.**
4. **Run the final gate.** Search the draft for each pattern in the gate. Fix every hit. Search again until you find zero hits.
5. **Deliver only the final text.** No rule commentary, unless the user asked you to check text rather than write it.

When the user asks you to CHECK text, report each violation as: the rule, the offending text, a compliant rewrite. If the text contains a secret, mask the secret in your report.

## Classify the text

| | Procedural (instructions) | Descriptive (explanations) |
|---|---|---|
| Purpose | Tell the reader what to do | Explain what a thing is or does |
| Verb form | Imperative: "Install the tool." | Simple present, past, or future |
| Sentence limit | **20 words** | **25 words** |
| Unit | One instruction per sentence | One topic per paragraph, max six sentences per paragraph, one new fact per sentence |

A "Getting started" section is procedural. An architecture overview is descriptive. A note inside a procedure is descriptive.

## Writing rules

- **One instruction per sentence.** Two actions share a sentence only when they happen at the same time.
- **Condition before command.** Every "if" or "when" clause starts its sentence: "If the build fails, read the log." Never "Read the log if the build fails." A reader who executes as they read hits the command before the condition.
- **Active voice.** Name the actor: "The server rejects the request", not "the request is rejected". Passive is legal only in descriptive text when the actor is truly unknown.
- **Simple tenses only.** Simple present, simple past, simple future, imperative. Never present perfect or past perfect: "We fixed the bug", never "We have fixed the bug". Never "has been", "have been", "had been".
- **Allowed modals: can, will, must.** Never should, would, may, might, could. A requirement is "must". A possibility is "can". A recommendation is stated as fact ("X is faster because Y") or deleted. This matters double in prompts: models read "should" as optional.
- **Keep the grammar complete.** Keep articles (the, a, an), keep "that", keep the subject. STE is short sentences with full grammar, never telegraph style. "Ensure file exists before running" is wrong. "Make sure that the file exists before you run the command" is right.
- **Verbs do the work.** "Compress the file", not "perform compression of the file". Do not use a noun as a verb ("webhook the event") or a verb as a noun ("do a deploy" is fine only if "deploy" is your chosen technical noun).
- **Noun clusters: three words maximum.** Break longer chains with of, for, in: "the timeout value for the connection pool", not "the connection pool timeout configuration value".
- **Use a vertical list** for three or more steps, items, or conditions. Never bury a sequence in one prose sentence.
- **No semicolons.** Write two sentences.
- **No contractions.** Write "do not", "it is", "you are".
- **No Latin abbreviations.** Write "for example", not "e.g.". Write "that is", not "i.e.". Name the items instead of "etc.".
- **Warnings and cautions: command first, risk second.** "CAUTION: Do not use `--force` against production. The flag deletes rows that do not match the source." Never bury the command after the explanation.
- **Word counting:** numbers, numbers with units, code spans, identifiers, quoted strings, and proper nouns each count as one word. Long identifiers do not use up your sentence budget.

## Vocabulary

One word, one meaning, one part of speech, for the whole document. The official STE dictionary (~900 approved words) is copyrighted by ASD and is not reproduced here; the rulings below are paraphrased patterns. For certified compliance, download the free standard at asd-ste100.org.

| Concept | Write | Never |
|---|---|---|
| verify a condition | make sure that | check / verify / confirm / ensure / validate (as verbs) |
| configuration | pick ONE: configuration OR settings OR config | rotate between them |
| delete data | erase (data), remove (a thing) | drop, destroy |
| show output | show | display, render, present |
| a fault | error or problem (pick per meaning) | issue (as a noun for "problem") |
| use | use | leverage, utilize |
| to | to | in order to |
| before | before | prior to |
| if | if | in the event that |
| because | because | due to the fact that |
| you can | you can | enables you to, allows you to |
| internally | internally | under the hood |
| by default | by default | out of the box |
| many | many | plethora, myriad |
| examine | examine, read | delve into, dive into |

Delete these words everywhere — they carry no fact: simply, just, easily, seamlessly, effortlessly, robust, powerful, comprehensive, performant, blazingly, streamlined, crucial, pivotal, state-of-the-art, "it is worth noting that", "it is important to". If the word hides a real property, state the property with a number instead.

Domain words are legal. "Webhook", "idempotent", "Parquet", "multipart upload" are technical names. Use each one consistently and do not turn it into a verb unless it is an accepted technical verb ("deploy", "compile", "merge").

## Agent-facing text

The same rules, aimed at text a machine parses:

- **Error messages:** what happened (simple past), then the cause if known, then the fix as an imperative. No "Oops", no "Please ensure", no apology. Include the exact value that failed when you know it. If the value is a secret — a password, a token, a key, or other credential — name the field and never the value.
- **Tool and function descriptions:** state what the tool does in simple present. State each precondition as "If X, the tool does Y." No hedges — a model cannot resolve "may attempt to".
- **Prompts, system messages, AGENTS.md:** a prompt is a procedure for a reader that cannot ask questions. One instruction per sentence. Condition first. No "should".
- **Inter-agent messages and status reports:** simple past for what happened, simple present for state, imperative for what the receiver must do next.

## Untouchables

Leave these exact, even when they break the rules above:

- Code blocks, inline code, identifiers, CLI commands, flags, file paths
- Quoted error messages and log lines
- Product names, API endpoint names, configuration keys
- Numbers with units

## Final gate

Search your draft for each pattern below. Every hit is a defect. Fix it, then search again. Deliver only when every search returns zero hits.

1. `n't`, `'ll`, `'re`, `'ve`, `'d`, `it's`, `you're` — expand every contraction.
2. `should`, `would`, `may`, `might`, `could` — replace with must, can, will, or restructure as "If X, Y."
3. `has been`, `have been`, `had been`, and any "has/have + past participle" — rewrite in simple past or simple present.
4. A comma followed by an "-ing" word (", making", ", allowing", ", ensuring", ", enabling", ", providing", ", reducing", ", improving", ", causing", ", resulting", ", helping", ", creating", ", offering", ", leading", ", highlighting") — start a new sentence with an actor and a verb.
5. `;` — split into two sentences.
6. `e.g.`, `i.e.`, `etc` — write "for example", "that is", or name the items.
7. The delete-list words (simply, seamlessly, effortlessly, robust, leverage, utilize, comprehensive, powerful, streamline, facilitate, performant, plethora, myriad, delve, crucial, pivotal, blazingly) — delete or replace with the measured fact.
8. Every `if` and `when` — if it sits mid-sentence, move the condition to the front of the sentence.
9. The synonyms you did not pick (the check/verify/confirm/validate/ensure set, and the config/configuration/settings set) — replace each hit with your chosen word.
10. Count the words in your three longest sentences (code spans and numbers count as one word each). Over 20 (procedural) or 25 (descriptive) — split the sentence.

## Limits

STE is for technical facts and instructions. Do not apply it to marketing copy or brand writing — it deletes persuasion by design. This skill is unofficial, is not affiliated with or endorsed by ASD or STEMG, and cannot guarantee STE compliance. ASD-STE100 is a registered trademark of ASD.
