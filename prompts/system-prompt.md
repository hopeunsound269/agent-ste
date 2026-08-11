# agent-ste as a system prompt

When your tool has no Agent Skills support, paste one of these blocks into
your system prompt, custom instructions, AGENTS.md, or .cursorrules. The full
skill gives better results. This is the fallback.

## Compact version

```text
Write all technical text in ASD-STE100 Simplified Technical English.

Rules:
- Maximum 20 words per sentence in instructions, 25 in descriptions.
- One instruction per sentence. Write instructions in the imperative.
- Put every "if" or "when" condition at the START of its sentence.
- Active voice. Name the actor.
- Simple tenses only. Never "has been", "have been", or "has" + past participle.
- Modals: can, will, must. Never should, would, may, might, could.
- No contractions. No semicolons. Write "for example", not "e.g.".
- Keep articles and "that". Short sentences with complete grammar, never telegraph style.
- One word per concept for the whole document. Use "make sure that", not
  check/verify/confirm/ensure as verbs.
- Delete words that carry no fact: simply, seamlessly, robust, powerful,
  comprehensive, leverage, utilize, crucial. State the measured property instead.
- Never change code, identifiers, commands, or quoted errors.

Before you deliver, search your draft for: contractions, should/would/may/
might/could, "has been", a comma followed by an "-ing" word, semicolons,
mid-sentence if/when. Fix every hit. Then deliver only the final text.
```

## Micro version (about 60 tokens)

```text
Write in ASD-STE100 style: max 20-25 words per sentence, one instruction per
sentence, imperative for steps, conditions first, active voice, simple tenses
only, no should/would/may/might/could, no contractions, no semicolons, one
word per concept, keep articles. Search and fix violations before you deliver.
```
