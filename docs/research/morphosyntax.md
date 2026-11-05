# Research notes: The Acquisition of Morphosyntax (LAMS, UPV/EHU, 2026–27)

Course by Prof. María del Pilar García Mayo. Distilled from the course handouts (Units 1–6) and readings.
Full annotated reading list lives in Roman's Notion ("LAMS — материалы курсов" → "Чтения").
Use these principles when designing LingMate features. Cite the source in PR descriptions.

## Core principles for LingMate

### 1. Meaning first, with short episodes of focus on form (FonF)
- Long & Robinson (1998): three options — focus on forms (grammar drills), focus on meaning (pure communication), focus on form (attention to form *inside* meaningful communication).
- Meaning-only input is not enough for grammatical accuracy (Canadian immersion; García Mayo & Villarreal Olaizola 2011: more CLIL hours did not remove variability in affixal morphology).
- **Design rule:** the conversation stays communicative. Form gets attention in brief episodes, never as a grammar lecture that hijacks the dialogue.

### 2. Corrective feedback must be *noticeable* for grammar
- Taxonomy (Nassaji & Kartchava; Lyster & Ranta): recast, explicit correction, metalinguistic clue, elicitation, clarification request, repetition. Input-providing (recast, explicit) vs output-prompting (elicitation, clarification, metalinguistic).
- Mackey, Gass & McDonough (2000): learners notice lexical/phonological feedback well but often **miss morphosyntactic recasts** — they read them as conversation.
- **Design rule:** for morphosyntax, prefer prompts (let the learner self-repair) or make the recast visibly marked (highlight the changed morpheme). Record the CF type used.

### 3. Pushed output and negotiation of meaning
- Interaction Hypothesis (Long), Output Hypothesis (Swain): producing language makes learners notice gaps and test hypotheses.
- Clarification requests, confirmation checks, comprehension checks drive learning; information-gap tasks generate them naturally (García Mayo & Lázaro Ibarrola 2015).
- **Design rule:** the tutor should sometimes ask the learner to reformulate rather than always supply the answer. Scenarios should contain an information gap (the bot knows things the learner must find out, and vice versa).

### 4. Tasks, not exercises (TBLT)
- Shehadeh (2024): a task has a primary focus on meaning, a gap, reliance on the learner's own resources, and a **non-linguistic outcome**.
- **Design rule:** every scenario has an explicit outcome (table booked, flat viewing arranged) that the system checks to decide completion.

### 5. Task repetition + pre-task focus on form
- Calzada & García Mayo (2023), Hidalgo & García Mayo (2021): repeating a task improves accuracy; procedural repetition with new content is also useful; brief pre-task FFI improves use of target forms.
- **Design rule:** schedule repeats of scenarios (same scenario, varied details, days later). Offer a 30-second "before you start" form tip tied to the learner's recurrent errors.

### 6. Textual enhancement and metalinguistic explanations
- Luquin & García Mayo (2023): long-term visual enhancement of target forms improved accuracy; short-term did not.
- Delgado-Garza & García Mayo (2025), Zhang et al. (2026): brief metalinguistic explanations help with non-salient forms; adults benefit from explicit instruction.
- **Design rule:** consistently highlight the learner's target forms in bot replies over weeks; offer short rule cards for non-salient forms.

### 7. L1 transfer — model the learner's L1 explicitly
- Chrabaszcz & Jiang (2014): Russian L1 learners (no articles) omit/misuse definite articles more than Spanish L1 learners.
- Lightbown & Spada (2000): learners transfer L1 patterns systematically but are often unaware of it.
- Johannessen et al. (2024): L1 gender system affects L2 gender assignment.
- **Design rule:** keep an L1-specific difficulty map. For Russian → Spanish: articles (el/la/un/una/∅), ser/estar, gender mismatches (el problema, la leche), preterite vs imperfect, subjunctive, clitic order. When an error is a transfer error, show the explicit RU vs ES contrast.

### 8. L1 use is a resource
- Azkarai & García Mayo (2015), Storch & Aldosari (2010): L1 serves word search, task management and metatalk; moderate use does not hurt.
- **Design rule:** let the learner drop a Russian word mid-sentence ("Quiero un *пододеяльник*") and get the Spanish word, without breaking the conversation.

### 9. Learner-initiated (preemptive) focus on form
- Ellis, Basturkmen & Loewen (2012): preemptive FFEs are as frequent as reactive ones, mostly learner-initiated and lexical; uptake is higher when the learner asked.
- **Design rule:** a "¿Cómo se dice…?" / "What does … mean?" affordance inside the chat.

### 10. Interlanguage is systematic; development follows stages
- Unit 1, Myles (2008): learner errors reveal a systematic interlanguage → log and classify errors; the error log is a mini learner corpus.
- Processability Theory (Pienemann; Son & Lee 2026), morpheme order studies (Kwon 2005): learners pass through stages in a fixed sequence; suppletive forms precede affixal ones (Unit 4).
- Distinguish knowledge errors from performance variability (Missing Surface Inflection): if the learner sometimes produces the form correctly, it needs practice/automatisation, not re-explanation.
- **Design rule:** don't demand structures beyond the learner's current stage; prioritise correcting what they are ready for; track per-form accuracy over time, not just a flat list of mistakes.

### 11. Adjust input, don't break it
- Foreigner talk (Unit 5 materials): native speakers simplify for non-natives (shorter, slower, frequent vocabulary) without ungrammaticality.
- **Design rule:** bot replies are calibrated to CEFR level but always grammatical.

## Course caution
The course forbids AI in assessed work. LingMate is a learning tool for Roman's own Spanish, never a homework generator.
