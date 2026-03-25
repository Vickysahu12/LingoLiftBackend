"""
MockPortal Seed Script
──────────────────────
Run: python -m app.seeds.mock_seed

Seeds:
  - 3 MockTests  (CAT Full Mock #1, Half Mock #1, Para Jumbles topic)
  - Sections, Marking, Rules, Syllabus, Instructions for each
  - Passages (2 RC passages for full mock)
  - Questions (full question set for CAT Full Mock #1 — 24Q: 15 RC + 9 VA)

Pattern matches existing Article seed style exactly.
"""

import asyncio
import sys
sys.path.insert(0, r"D:\Verbify\backend")

from app.db.database import AsyncSessionLocal
from app.account.models import User
from app.models.mock import (
    MockTest, MockSection, MarkingScheme, MockRule,
    MockSyllabus, MockInstruction, Passage, MockQuestion,
    MockType, DifficultyLevel, BadgeType, QuestionType,
)
from sqlalchemy import select

# ─── SEED DATA ────────────────────────────────────────────────────────────────

MOCKS = [

    # ══════════════════════════════════════════════════════════════════════════
    # MOCK 1: CAT Full Mock #1  (Full — 24Q, 40 min, Hard)
    # Maps to id='1' in MockListScreen MOCK_DATA
    # ══════════════════════════════════════════════════════════════════════════
    {
        "mock": {
            "title":           "CAT Full Mock #1",
            "subtitle":        "VARC",
            "description":     "Full-length CAT simulation. VARC section live — DILR & QA unlock after launch.",
            "type":            MockType.full,
            "icon":            "🔥",
            "badge":           BadgeType.hot,
            "difficulty":      DifficultyLevel.hard,
            "total_duration":  "40 Minutes",
            "duration_secs":   2400,
            "total_questions": 24,
            "max_score":       72,
            "attempt_count":   1200,
            "order_index":     1,
        },
        "sections": [
            {
                "section_key":  "varc",
                "label":        "VARC",
                "icon":         "📖",
                "duration":     "40 mins",
                "duration_secs": 2400,
                "questions":    24,
                "breakdown":    "3 RC Passages (15Q) + 9 VA Questions",
                "color":        "#1F3B1F",
                "is_locked":    False,
                "order_index":  0,
            }
        ],
        "marking": {
            "correct_marks":   3,
            "incorrect_marks": -1,
            "tita_marks":      0,
            "correct_sub":     "For every correct answer",
            "wrong_sub":       "For every wrong MCQ answer",
            "tita_sub":        "No negative marking for TITA",
            "has_tita":        True,
        },
        "rules": [
            {"icon": "📖", "label": "3 RC Passages",          "order_index": 0},
            {"icon": "🔀", "label": "Para Jumbles (TITA)",    "order_index": 1},
            {"icon": "⏸️", "label": "Cannot Pause Test",      "order_index": 2},
            {"icon": "📱", "label": "Auto-submit on Timeout", "order_index": 3},
        ],
        "syllabus": [
            {"label": "Reading Comprehension — Inference",  "covered": True,  "order_index": 0},
            {"label": "Reading Comprehension — Main Idea",  "covered": True,  "order_index": 1},
            {"label": "Para Jumbles (TITA)",                "covered": True,  "order_index": 2},
            {"label": "Para Summary",                       "covered": True,  "order_index": 3},
            {"label": "Odd Sentence Out",                   "covered": True,  "order_index": 4},
            {"label": "Vocabulary in Context",              "covered": False, "order_index": 5},
        ],
        "instructions": [
            {"text": "VARC section auto-submits after 40 minutes.",                        "order_index": 0},
            {"text": "RC questions carry negative marking (−1 per wrong).",                "order_index": 1},
            {"text": "TITA questions (Para Jumbles, Odd One Out) have NO negative marking.", "order_index": 2},
            {"text": "You cannot pause the test once started.",                            "order_index": 3},
            {"text": "Read each passage carefully before attempting questions.",           "order_index": 4},
        ],
        "passages": [
            {
                "passage_key": "p1",
                "label":       "Passage 1",
                "title":       "The Philosophy of Consciousness",
                "content": [
                    "Consciousness remains one of the most profound and unresolved problems in both philosophy and neuroscience. Despite centuries of inquiry, thinkers have yet to agree on what consciousness fundamentally is, how it arises, or why it exists at all.",
                    "The 'hard problem' of consciousness, as articulated by philosopher David Chalmers, distinguishes between explaining cognitive functions — perception, memory, attention — and explaining the subjective, felt quality of experience. Why does seeing red feel like something? Why is there an inner life at all?",
                    "Materialist accounts argue that consciousness is entirely reducible to brain states. Functionalists go further, suggesting that what matters is not the physical substrate but the pattern of information processing. On this view, sufficiently complex computational systems might be conscious.",
                    "However, critics like John Searle argue that syntax — the formal manipulation of symbols — can never give rise to semantics, to genuine understanding. His famous Chinese Room argument suggests that even a system that perfectly simulates understanding need not actually understand anything.",
                    "Ultimately, the question of consciousness touches on identity, free will, and the nature of reality itself. As artificial systems grow more sophisticated, resolving this question becomes not merely academic but urgently practical.",
                ],
            },
            {
                "passage_key": "p2",
                "label":       "Passage 2",
                "title":       "The Economics of Attention",
                "content": [
                    "In the digital age, attention has become the scarcest and most valuable resource. Unlike traditional commodities, attention cannot be stored, replicated, or transferred — it can only be spent. This has given rise to what economists call the 'attention economy.'",
                    "Platforms like social media companies have built their entire business models around capturing and monetising human attention. The result is an arms race of engagement: algorithms optimised not for user wellbeing but for time-on-platform.",
                    "Psychologists have documented the costs of this economy. Fragmented attention reduces cognitive depth, impairing long-form reasoning and creativity. The dopamine-driven loops of social media mimic the mechanics of addiction, making volitional withdrawal difficult.",
                    "Proponents of the attention economy argue that it democratises content, giving voice to creators who would have been gatekept by traditional media. The economic incentives, they argue, simply reflect what people genuinely want.",
                    "Yet the deeper issue is one of consent and awareness. Users rarely appreciate the extent to which their attention is being harvested. A market in which one party has vastly superior information about the transaction cannot be called truly free.",
                ],
            },
            {
                "passage_key": "p3",
                "label":       "Passage 3",
                "title":       "Urban Planning and Human Behaviour",
                "content": [
                    "The design of cities profoundly shapes the behaviour, wellbeing, and social fabric of their inhabitants. Yet for much of the twentieth century, urban planning prioritised the car over the pedestrian, fragmenting communities and eroding public life.",
                    "Jane Jacobs, writing in the 1960s, argued that vibrant cities require density, mixed uses, and short blocks — conditions that encourage chance encounters and foster informal social networks. Her ideas stood in stark contrast to the modernist planning consensus of her era.",
                    "Contemporary research in environmental psychology supports Jacobs's intuitions. Studies consistently show that walkable neighbourhoods correlate with higher levels of trust, lower rates of depression, and stronger civic engagement.",
                    "Smart city advocates propose a different solution: technology-driven optimisation of urban systems, from traffic flow to waste collection. Critics worry, however, that optimising cities for efficiency reduces them to machines, stripping out the productive inefficiency that generates creativity and spontaneity.",
                    "The challenge facing planners today is to reconcile competing demands — density without overcrowding, efficiency without dehumanisation, connectivity without surveillance — in cities that must also become resilient to climate change.",
                ],
            },
        ],
        "questions": [
            # ── PASSAGE 1: Consciousness (Q1–Q5) ──────────────────────────
            {
                "passage_key":    "p1",
                "number":         1,
                "type":           QuestionType.mcq,
                "text":           "The 'hard problem' of consciousness, as described in the passage, is best understood as the challenge of explaining:",
                "options": [
                    "How the brain processes sensory information",
                    "Why subjective experience exists at all",
                    "The role of memory in conscious awareness",
                    "How artificial systems can simulate consciousness",
                ],
                "correct_option": 1,
                "explanation":    "The passage defines the hard problem as explaining the 'subjective, felt quality of experience' — the why of inner life, not merely cognitive functions.",
                "key_point":      "Hard problem ≠ cognitive functions; it is about qualia and subjective experience.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    0,
            },
            {
                "passage_key":    "p1",
                "number":         2,
                "type":           QuestionType.mcq,
                "text":           "Which of the following best describes the functionalist position on consciousness as presented in the passage?",
                "options": [
                    "Consciousness is entirely a product of the physical brain",
                    "Only biological systems can possess consciousness",
                    "What matters for consciousness is the pattern of information processing, not the substrate",
                    "Consciousness cannot be explained by science",
                ],
                "correct_option": 2,
                "explanation":    "Functionalists argue the substrate is irrelevant — it is the pattern of information processing that determines consciousness. Hence computational systems could in principle be conscious.",
                "key_point":      "Functionalism: substrate-independent; pattern/function is what matters.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    1,
            },
            {
                "passage_key":    "p1",
                "number":         3,
                "type":           QuestionType.mcq,
                "text":           "The Chinese Room argument by Searle is used in the passage to counter which position?",
                "options": [
                    "The hard problem formulation by Chalmers",
                    "The claim that syntax can generate semantics in complex systems",
                    "The materialist view that consciousness reduces to brain states",
                    "The argument that consciousness is practically irrelevant",
                ],
                "correct_option": 1,
                "explanation":    "Searle's Chinese Room specifically targets the claim that formal symbol manipulation (syntax) can produce genuine understanding (semantics) — the functionalist/computationalist position.",
                "key_point":      "Searle vs Functionalism: syntax ≠ semantics.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    2,
            },
            {
                "passage_key":    "p1",
                "number":         4,
                "type":           QuestionType.mcq,
                "text":           "The author's tone in the final paragraph can best be described as:",
                "options": [
                    "Dismissive of philosophical inquiry",
                    "Alarmist about artificial intelligence",
                    "Thoughtfully urgent about the practical stakes of the question",
                    "Optimistic that the hard problem will soon be resolved",
                ],
                "correct_option": 2,
                "explanation":    "The author calls the question 'not merely academic but urgently practical' — conveying measured urgency rather than alarm or dismissal.",
                "key_point":      "Tone: analytically urgent — not alarmist, not dismissive.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    3,
            },
            {
                "passage_key":    "p1",
                "number":         5,
                "type":           QuestionType.mcq,
                "text":           "It can be inferred from the passage that the author considers the question of consciousness to be:",
                "options": [
                    "Essentially resolved by neuroscience",
                    "A purely metaphysical question with no practical relevance",
                    "Both philosophically deep and practically consequential",
                    "Less important than questions about artificial intelligence",
                ],
                "correct_option": 2,
                "explanation":    "The passage discusses both philosophical depth (hard problem, identity, free will) and practical urgency (AI systems), supporting inference C.",
                "key_point":      "Inference questions: synthesise across paragraphs rather than quoting one sentence.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    4,
            },

            # ── PASSAGE 2: Attention Economy (Q6–Q10) ─────────────────────
            {
                "passage_key":    "p2",
                "number":         6,
                "type":           QuestionType.mcq,
                "text":           "According to the passage, what distinguishes attention from traditional commodities?",
                "options": [
                    "Attention has no economic value",
                    "Attention cannot be stored, replicated, or transferred",
                    "Attention is produced in greater quantities by digital platforms",
                    "Attention can be directed by algorithms without user awareness",
                ],
                "correct_option": 1,
                "explanation":    "The passage explicitly states attention 'cannot be stored, replicated, or transferred — it can only be spent.'",
                "key_point":      "Direct retrieval: look for explicit statements before inferring.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    5,
            },
            {
                "passage_key":    "p2",
                "number":         7,
                "type":           QuestionType.mcq,
                "text":           "The passage suggests that proponents of the attention economy would most likely argue that:",
                "options": [
                    "Social media platforms deliberately harm users",
                    "Algorithmic engagement is a form of addiction by design",
                    "The attention economy democratises content and reflects genuine demand",
                    "Attention is a resource that should be publicly regulated",
                ],
                "correct_option": 2,
                "explanation":    "Paragraph 4 directly states the proponent view: democratisation of content and that incentives reflect 'what people genuinely want.'",
                "key_point":      "Always locate the source of an attributed view — the passage clearly labels it.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    6,
            },
            {
                "passage_key":    "p2",
                "number":         8,
                "type":           QuestionType.mcq,
                "text":           "The phrase 'productive inefficiency' in Passage 3 (Urban Planning) is most analogous to which concept in Passage 2 (Attention Economy)?",
                "options": [
                    "Dopamine-driven engagement loops",
                    "The unregulated market for attention",
                    "Serendipitous discovery enabled by unoptimised browsing",
                    "The arms race of algorithmic optimisation",
                ],
                "correct_option": 2,
                "explanation":    "Productive inefficiency = value created from non-optimal, spontaneous interaction. In the attention economy context, unoptimised browsing can lead to serendipitous, creative discovery — similar to the urban spontaneity argument.",
                "key_point":      "Cross-passage inference: identify structural parallels, not surface vocabulary matches.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    7,
            },
            {
                "passage_key":    "p2",
                "number":         9,
                "type":           QuestionType.mcq,
                "text":           "The author's central argument in the final paragraph of Passage 2 is that the attention economy:",
                "options": [
                    "Is fundamentally exploitative because users lack informed awareness",
                    "Is no different from any other advertising-based market",
                    "Benefits users through personalised content recommendations",
                    "Should be regulated using traditional anti-monopoly law",
                ],
                "correct_option": 0,
                "explanation":    "The final paragraph argues that informational asymmetry — users not knowing how their attention is harvested — undermines the freedom of the market. This is a consent/awareness critique, not a competition law argument.",
                "key_point":      "Central argument of a paragraph ≠ a supporting detail. Synthesise the whole paragraph.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    8,
            },
            {
                "passage_key":    "p2",
                "number":         10,
                "type":           QuestionType.mcq,
                "text":           "Which of the following, if true, would most weaken the proponent's argument in Passage 2?",
                "options": [
                    "Social media increases the speed of information dissemination",
                    "Users report higher satisfaction with algorithmically curated content",
                    "Research shows users systematically underestimate time spent on platforms",
                    "Traditional media also relies on advertising revenue",
                ],
                "correct_option": 2,
                "explanation":    "The proponent argues the market reflects genuine demand. If users systematically underestimate their engagement, their revealed preference is a poor signal of genuine want — weakening the 'people genuinely want this' argument.",
                "key_point":      "Weakening arguments: find evidence that undermines a stated premise, not just a tangential fact.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    9,
            },

            # ── PASSAGE 3: Urban Planning (Q11–Q15) ───────────────────────
            {
                "passage_key":    "p3",
                "number":         11,
                "type":           QuestionType.mcq,
                "text":           "Jane Jacobs's argument, as presented in the passage, fundamentally conflicts with which 20th-century planning assumption?",
                "options": [
                    "That cities should be designed for pedestrians",
                    "That car-centric design fragments communities",
                    "That density and mixed-use zones produce vibrant cities",
                    "That planning should optimise for efficiency above all",
                ],
                "correct_option": 3,
                "explanation":    "Jacobs argued for organic urban vitality — density, mixed use, short blocks — against the modernist efficiency consensus that prioritised the car and ordered separation of uses.",
                "key_point":      "Contrast questions: identify what a thinker opposes, not just what they favour.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    10,
            },
            {
                "passage_key":    "p3",
                "number":         12,
                "type":           QuestionType.mcq,
                "text":           "What does the passage imply about the relationship between walkable neighbourhoods and social outcomes?",
                "options": [
                    "Walkability is a consequence of higher social trust, not a cause",
                    "Environmental psychology research supports Jacobs's urban design principles",
                    "Dense neighbourhoods reduce civic engagement due to overcrowding",
                    "Smart city technology replicates the benefits of walkability",
                ],
                "correct_option": 1,
                "explanation":    "The passage states that walkable neighbourhoods 'correlate with' higher trust, lower depression, stronger civic engagement — validating Jacobs's design principles through contemporary research.",
                "key_point":      "Correlation ≠ causation, but the passage does not claim causation — it implies empirical support.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    11,
            },
            {
                "passage_key":    "p3",
                "number":         13,
                "type":           QuestionType.mcq,
                "text":           "The author's concern about 'smart city' approaches is best captured by which of the following?",
                "options": [
                    "Smart cities are technologically unfeasible in developing countries",
                    "Optimising for efficiency may eliminate the spontaneity essential to human urban life",
                    "Smart city data collection violates privacy laws",
                    "Efficiency-driven planning inevitably leads to social inequality",
                ],
                "correct_option": 1,
                "explanation":    "The passage states critics worry optimisation 'reduces [cities] to machines, stripping out the productive inefficiency that generates creativity and spontaneity.'",
                "key_point":      "Author's concern: locate where the author signals their own evaluative stance vs attributed views.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    12,
            },
            {
                "passage_key":    "p3",
                "number":         14,
                "type":           QuestionType.mcq,
                "text":           "The phrase 'productive inefficiency' as used in the passage most nearly means:",
                "options": [
                    "Wasteful allocation of urban resources",
                    "Planned redundancy in city infrastructure",
                    "Unscripted human interactions that generate social and creative value",
                    "The inefficiency of large government planning departments",
                ],
                "correct_option": 2,
                "explanation":    "In context, 'productive inefficiency' refers to the organic, unplanned messiness of city life — chance encounters, spontaneous creativity — that efficient optimisation would eliminate.",
                "key_point":      "Vocabulary in context: the answer must fit both the dictionary meaning and the passage's usage.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    13,
            },
            {
                "passage_key":    "p3",
                "number":         15,
                "type":           QuestionType.mcq,
                "text":           "Which of the following best describes the overall structure of the urban planning passage?",
                "options": [
                    "A problem is identified, a historical solution proposed, empirical evidence cited, a competing solution introduced, and a synthesis offered",
                    "A historical debate is described, resolved, and applied to a contemporary problem",
                    "An argument is presented, attacked, and then definitively refuted",
                    "Two opposing theories are presented with equal weight and no evaluative conclusion",
                ],
                "correct_option": 0,
                "explanation":    "Para 1: problem (car-centric planning). Para 2: Jacobs's solution. Para 3: empirical support. Para 4: smart city alternative. Para 5: synthesis of competing demands.",
                "key_point":      "Structure questions: map each paragraph to its rhetorical function before selecting.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    14,
            },

            # ── VA QUESTIONS (Q16–Q24) — no passage ───────────────────────
            # Para Jumbles (TITA)
            {
                "passage_key":    None,
                "number":         16,
                "type":           QuestionType.tita,
                "text":           "The sentences below, when properly arranged, form a coherent paragraph. Identify the correct sequence.\n\nA. This shift was neither sudden nor without precedent, but its pace exceeded all prior transitions.\nB. Historians debate whether industrialisation was a revolution or a gradual evolution.\nC. What is clear, however, is that by 1850 the world looked fundamentally different from 1750.\nD. Mechanised production, urbanisation, and wage labour reshaped social hierarchies within decades.",
                "options":        None,
                "correct_answer": "BADC",
                "hint":           "Type the sequence as letters, e.g. ABCD",
                "explanation":    "B introduces the debate (opening). A elaborates with qualification. D gives the evidence of transformation. C provides the conclusive observation — classic qualifier-evidence-conclusion structure.",
                "key_point":      "For para jumbles: find the topic sentence (usually a general claim or debate introduction), then build evidence → conclusion.",
                "marks_correct":  3,
                "marks_incorrect": 0,
                "order_index":    15,
            },
            {
                "passage_key":    None,
                "number":         17,
                "type":           QuestionType.tita,
                "text":           "Arrange the following sentences into a coherent paragraph:\n\nA. It is this tension that makes tragedy not merely sad but morally instructive.\nB. Great tragic heroes are undone not by external misfortune but by a flaw within their own character.\nC. Yet the audience watches with full knowledge of the impending catastrophe.\nD. The hero acts in accordance with values they hold to be correct.",
                "options":        None,
                "correct_answer": "BDCA",
                "hint":           "Type the sequence as letters, e.g. ABCD",
                "explanation":    "B is the thesis. D elaborates on the hero's perspective. C introduces dramatic irony (the audience's perspective). A is the concluding reflection on the meaning of this tension.",
                "key_point":      "Look for the pivot sentence that introduces a contrasting perspective — it usually connects two logical halves.",
                "marks_correct":  3,
                "marks_incorrect": 0,
                "order_index":    16,
            },
            {
                "passage_key":    None,
                "number":         18,
                "type":           QuestionType.tita,
                "text":           "Arrange the following sentences into a coherent paragraph:\n\nA. Language, far from being a neutral tool, actively shapes the categories through which we perceive reality.\nB. The Sapir-Whorf hypothesis proposes a strong version of this claim — that language determines thought.\nC. A weaker, more defensible version holds that language influences, but does not fully determine, cognition.\nD. Empirical studies on colour perception across cultures provide partial but inconclusive support.",
                "options":        None,
                "correct_answer": "ABCD",
                "hint":           "Type the sequence as letters, e.g. ABCD",
                "explanation":    "A makes the general claim. B introduces the strong theoretical version. C qualifies with a weaker version. D provides empirical context — classic strong claim → qualification → evidence structure.",
                "key_point":      "Science/theory passages: look for the progression strong claim → qualification → evidence.",
                "marks_correct":  3,
                "marks_incorrect": 0,
                "order_index":    17,
            },

            # Para Summary (MCQ)
            {
                "passage_key":    None,
                "number":         19,
                "type":           QuestionType.para_summary,
                "text":           "The idea that markets are self-correcting mechanisms — that prices signal information efficiently and imbalances are automatically resolved — has been the dominant paradigm in economics for decades. Yet financial crises, persistent inequality, and environmental degradation suggest that markets routinely fail to account for externalities, distribute resources equitably, or incorporate long-term costs. Defenders argue that market failures stem from government interference, not from market logic itself. Critics respond that the empirical record of deregulated markets tells a different story.\n\nChoose the best summary:",
                "options": [
                    "Markets are self-correcting and government intervention always worsens economic outcomes.",
                    "The efficiency of markets is a contested claim, with proponents and critics citing different empirical evidence.",
                    "Financial crises are caused primarily by inadequate government regulation of markets.",
                    "Inequality and environmental damage are inevitable consequences of market economies.",
                ],
                "correct_option": 1,
                "explanation":    "The paragraph presents a contested debate — not a resolution. It neither endorses nor refutes markets; it maps the argument between proponents and critics.",
                "key_point":      "Summary MCQ: the correct option reflects the paragraph's balance, not one side's argument.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    18,
            },
            {
                "passage_key":    None,
                "number":         20,
                "type":           QuestionType.para_summary,
                "text":           "Memory is not a passive recording system but an active process of reconstruction. Every time we recall an event, we subtly alter it — incorporating new information, current emotional states, and the expectations of our social context. This makes memory unreliable as a factual record but uniquely adaptive: we remember what is useful to us now, not necessarily what was true then. The legal system's continued reliance on eyewitness testimony is, given this evidence, troubling.\n\nChoose the best summary:",
                "options": [
                    "Memory is completely unreliable and should never be used as evidence.",
                    "The reconstructive nature of memory has implications for the reliability of eyewitness testimony.",
                    "Human memory functions like a video recording that can be selectively edited.",
                    "The legal system has already accounted for the limitations of human memory.",
                ],
                "correct_option": 1,
                "explanation":    "The paragraph explains reconstruction and ends with a specific implication for eyewitness testimony. Option B captures both — it is neither too narrow nor too absolute.",
                "key_point":      "Avoid extreme options ('never', 'completely') and options that contradict the passage's nuance.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    19,
            },
            {
                "passage_key":    None,
                "number":         21,
                "type":           QuestionType.para_summary,
                "text":           "Nuclear power generates electricity without direct carbon emissions, making it attractive as a low-carbon energy source. Yet it carries risks that are qualitatively different from fossil fuels — the potential for catastrophic accidents, the unresolved problem of long-term waste storage, and the dual-use risk of proliferating weapons-grade material. A rational energy policy must weigh these incommensurable risks rather than pretending a clean calculation is possible.\n\nChoose the best summary:",
                "options": [
                    "Nuclear power is dangerous and should be phased out in favour of renewable energy.",
                    "Carbon emissions from fossil fuels pose a greater risk than nuclear accidents.",
                    "Nuclear energy presents a genuine but complex trade-off between climate and safety risks.",
                    "Rational energy policy requires switching entirely to nuclear power to fight climate change.",
                ],
                "correct_option": 2,
                "explanation":    "The passage argues the trade-off is real and complex — not resolvable by simple calculation. Option C captures this balanced, nuanced position.",
                "key_point":      "When the passage says a 'clean calculation is not possible,' the correct summary reflects complexity, not a definitive recommendation.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    20,
            },

            # Odd One Out (MCQ)
            {
                "passage_key":    None,
                "number":         22,
                "type":           QuestionType.odd_one_out,
                "text":           "Four sentences form a coherent paragraph. Identify the sentence that does NOT belong:\n\nA. The Renaissance marked a revival of interest in classical Greek and Roman learning.\nB. Humanist scholars championed individual reason and secular knowledge over religious dogma.\nC. The printing press accelerated the spread of humanist ideas across Europe.\nD. The Catholic Church retained political authority over most European monarchies throughout the 17th century.",
                "options":        ["A", "B", "C", "D"],
                "correct_option": 3,
                "explanation":    "A, B, C are all about the Renaissance and humanism. D introduces a later period (17th century) and a different theme (church authority) — it disrupts the temporal and thematic unity.",
                "key_point":      "Odd one out: find the sentence that introduces a new time frame, topic, or logical thread not supported by the others.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    21,
            },
            {
                "passage_key":    None,
                "number":         23,
                "type":           QuestionType.odd_one_out,
                "text":           "Four sentences form a coherent paragraph. Identify the sentence that does NOT belong:\n\nA. Biodiversity loss is proceeding at a rate estimated to be 1,000 times the natural background extinction rate.\nB. Habitat destruction, primarily driven by agriculture and urbanisation, is the leading cause.\nC. Some species, however, have shown remarkable adaptability to urban environments.\nD. Climate change and invasive species further compound the pressure on ecosystems.",
                "options":        ["A", "B", "C", "D"],
                "correct_option": 2,
                "explanation":    "A, B, D all support the central claim about biodiversity loss and its causes. C introduces a counterexample (adaptability) that undermines the paragraph's coherence — it belongs to a different, more optimistic discussion.",
                "key_point":      "A sentence that introduces a logical counterpoint (however, yet, although) is often the odd one out.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    22,
            },
            {
                "passage_key":    None,
                "number":         24,
                "type":           QuestionType.odd_one_out,
                "text":           "Four sentences form a coherent paragraph. Identify the sentence that does NOT belong:\n\nA. Behavioural economics has demonstrated that humans are systematically irrational in predictable ways.\nB. Cognitive biases such as loss aversion and anchoring distort financial decision-making.\nC. Traditional economic models assumed rational actors maximising utility under perfect information.\nD. Adam Smith's The Wealth of Nations, published in 1776, is considered the founding text of modern economics.",
                "options":        ["A", "B", "C", "D"],
                "correct_option": 3,
                "explanation":    "A, B, C all relate to the behavioural economics critique of rational actor models. D is a historical fact about Smith that is tangential to the paragraph's argument about irrational behaviour.",
                "key_point":      "Historical trivia inserted into a conceptual argument is a classic odd-one-out pattern.",
                "marks_correct":  3,
                "marks_incorrect": -1,
                "order_index":    23,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MOCK 2: Half Length Mock #1  (Half — 16Q, 30 min, Medium)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "mock": {
            "title":           "Half Length Mock #1",
            "subtitle":        "VARC",
            "description":     "A 30-minute VARC-only mock — great for focused verbal practice.",
            "type":            MockType.half,
            "icon":            "⚡",
            "badge":           BadgeType.hot,
            "difficulty":      DifficultyLevel.medium,
            "total_duration":  "30 Minutes",
            "duration_secs":   1800,
            "total_questions": 16,
            "max_score":       48,
            "attempt_count":   2100,
            "order_index":     2,
        },
        "sections": [
            {
                "section_key":  "varc",
                "label":        "VARC",
                "icon":         "📖",
                "duration":     "30 mins",
                "duration_secs": 1800,
                "questions":    16,
                "breakdown":    "2 RC Passages (10Q) + 6 VA Questions",
                "color":        "#1F3B1F",
                "is_locked":    False,
                "order_index":  0,
            }
        ],
        "marking": {
            "correct_marks":   3,
            "incorrect_marks": -1,
            "tita_marks":      0,
            "correct_sub":     "For every correct answer",
            "wrong_sub":       "For every wrong MCQ answer",
            "tita_sub":        "No negative marking for TITA",
            "has_tita":        True,
        },
        "rules": [
            {"icon": "📖", "label": "2 RC Passages",          "order_index": 0},
            {"icon": "🔀", "label": "Para Jumbles (TITA)",    "order_index": 1},
            {"icon": "⏸️", "label": "Cannot Pause Test",      "order_index": 2},
            {"icon": "📱", "label": "Auto-submit on Timeout", "order_index": 3},
        ],
        "syllabus": [
            {"label": "Reading Comprehension — Inference", "covered": True,  "order_index": 0},
            {"label": "Reading Comprehension — Main Idea", "covered": True,  "order_index": 1},
            {"label": "Para Jumbles (TITA)",               "covered": True,  "order_index": 2},
            {"label": "Para Summary",                      "covered": False, "order_index": 3},
            {"label": "Odd Sentence Out",                  "covered": False, "order_index": 4},
            {"label": "Vocabulary in Context",             "covered": False, "order_index": 5},
        ],
        "instructions": [
            {"text": "Test auto-submits after 30 minutes.",                      "order_index": 0},
            {"text": "RC questions carry negative marking (−1 per wrong).",      "order_index": 1},
            {"text": "TITA questions have NO negative marking.",                 "order_index": 2},
            {"text": "Half-length format — ideal for time-limited practice.",    "order_index": 3},
        ],
        "passages": [
            {
                "passage_key": "p1",
                "label":       "Passage 1",
                "title":       "The Science of Sleep",
                "content": [
                    "Sleep was long considered passive — a mere absence of wakefulness. This view has been overturned by decades of research revealing sleep as a period of intense biological activity crucial for memory consolidation, immune function, and metabolic regulation.",
                    "During slow-wave sleep, the brain replays and consolidates memories formed during waking hours, transferring them from the hippocampus to the cortex for long-term storage. This process underlies the well-documented improvement in learning that follows sleep.",
                    "REM sleep, characterised by rapid eye movements and vivid dreaming, appears to play a role in emotional processing — helping the brain integrate experiences by stripping them of their emotional charge.",
                    "Modern society's chronic sleep deprivation may thus carry cognitive and emotional costs far greater than previously recognised. The glorification of minimal sleep as a mark of productivity is, from a neuroscientific standpoint, profoundly misguided.",
                ],
            },
            {
                "passage_key": "p2",
                "label":       "Passage 2",
                "title":       "Democracy and Its Discontents",
                "content": [
                    "Liberal democracy rests on two commitments that stand in permanent tension: majority rule and minority rights. When these come into conflict, constitutional systems provide mechanisms — judicial review, protected rights, federal structures — to prevent the tyranny of the majority.",
                    "Yet these counter-majoritarian mechanisms are themselves contested. Critics argue that unelected judges overturning democratic legislation is anti-democratic by definition. Defenders respond that democracy is not merely about numbers but about protecting the conditions for democratic participation itself.",
                    "The rise of populist movements across the democratic world has sharpened this tension. Populists claim to speak for 'the people' against self-serving elites — including the judiciary and press. Their electoral successes test whether liberal democratic institutions are robust enough to survive determined majorities.",
                    "The answer, most scholars agree, lies not in any single institutional safeguard but in civic culture: a broad popular commitment to democratic norms that no electoral majority can simply dissolve.",
                ],
            },
        ],
        "questions": [
            # Passage 1 — Sleep (Q1-Q5)
            {
                "passage_key": "p1", "number": 1, "type": QuestionType.mcq,
                "text": "The passage's central argument is that sleep:",
                "options": [
                    "Is primarily a state of physical rest and neural inactivity",
                    "Serves critical biological functions including memory and emotional processing",
                    "Is becoming less important due to modern lifestyle adaptations",
                    "Benefits memory consolidation but has no emotional function",
                ],
                "correct_option": 1,
                "explanation": "The passage refutes the passive view and presents evidence for memory consolidation (para 2) and emotional processing (para 3).",
                "key_point": "Central argument spans the full passage — never take one paragraph's detail as the central claim.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 0,
            },
            {
                "passage_key": "p1", "number": 2, "type": QuestionType.mcq,
                "text": "According to the passage, what distinguishes REM sleep from slow-wave sleep?",
                "options": [
                    "REM sleep consolidates memory; slow-wave sleep processes emotion",
                    "Slow-wave sleep consolidates memory; REM sleep processes emotion",
                    "Both phases perform identical functions but at different times",
                    "REM sleep reduces hippocampal activity; slow-wave sleep increases it",
                ],
                "correct_option": 1,
                "explanation": "Para 2: slow-wave → memory consolidation. Para 3: REM → emotional processing. Direct retrieval.",
                "key_point": "Distinguishing details: slow-wave ≠ REM. Don't reverse them.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 1,
            },
            {
                "passage_key": "p1", "number": 3, "type": QuestionType.mcq,
                "text": "The phrase 'stripping them of their emotional charge' (paragraph 3) most nearly means:",
                "options": [
                    "Erasing the memory of emotional experiences entirely",
                    "Intensifying the emotional impact of dreams",
                    "Processing experiences so they lose their raw emotional intensity",
                    "Converting emotional memories into factual long-term storage",
                ],
                "correct_option": 2,
                "explanation": "The phrase means REM sleep reduces the emotional intensity of memories — not erasing them, but making them less viscerally charged through processing.",
                "key_point": "Vocabulary in context: the correct answer must preserve the passage's meaning without distortion.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 2,
            },
            {
                "passage_key": "p1", "number": 4, "type": QuestionType.mcq,
                "text": "The author's attitude toward the glorification of minimal sleep can best be described as:",
                "options": ["Neutral and scientific", "Mildly curious", "Critically dismissive", "Cautiously supportive"],
                "correct_option": 2,
                "explanation": "'Profoundly misguided' is a strong evaluative judgment — critical and dismissive of the glorification culture.",
                "key_point": "Strong adjectives like 'profoundly misguided' signal a clear authorial stance.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 3,
            },
            {
                "passage_key": "p1", "number": 5, "type": QuestionType.mcq,
                "text": "It can be inferred that the author believes modern society's approach to sleep:",
                "options": [
                    "Is improving as neuroscience findings become mainstream",
                    "Has no measurable effect on cognitive performance",
                    "Contradicts well-established scientific evidence about sleep's importance",
                    "Is a necessary adaptation to contemporary economic demands",
                ],
                "correct_option": 2,
                "explanation": "The passage documents scientific evidence for sleep's importance and then notes modern society's 'chronic sleep deprivation' — implying a contradiction between evidence and practice.",
                "key_point": "Inference: connect the scientific evidence in earlier paragraphs to the evaluative claim in the final paragraph.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 4,
            },
            # Passage 2 — Democracy (Q6-Q10)
            {
                "passage_key": "p2", "number": 6, "type": QuestionType.mcq,
                "text": "The 'permanent tension' in liberal democracy described in the passage is between:",
                "options": [
                    "Judicial review and parliamentary sovereignty",
                    "Majority rule and minority rights",
                    "Populist movements and established elites",
                    "Constitutional rights and elected governments",
                ],
                "correct_option": 1,
                "explanation": "Paragraph 1 explicitly identifies the tension as between majority rule and minority rights.",
                "key_point": "Direct retrieval: the answer is stated, not inferred.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 5,
            },
            {
                "passage_key": "p2", "number": 7, "type": QuestionType.mcq,
                "text": "Defenders of counter-majoritarian mechanisms argue that these mechanisms:",
                "options": [
                    "Represent the will of the majority through indirect representation",
                    "Protect the conditions necessary for democratic participation itself",
                    "Are necessary only in countries with weak political institutions",
                    "Should be controlled by elected governments, not unelected judges",
                ],
                "correct_option": 1,
                "explanation": "Para 2: defenders say democracy is about 'protecting the conditions for democratic participation itself' — not merely about numbers.",
                "key_point": "Attribute arguments correctly: critics vs defenders say opposite things.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 6,
            },
            {
                "passage_key": "p2", "number": 8, "type": QuestionType.mcq,
                "text": "The author's conclusion in the final paragraph suggests that democratic resilience depends primarily on:",
                "options": [
                    "Strong constitutional courts",
                    "Federal political structures",
                    "Civic culture and popular commitment to democratic norms",
                    "Limiting the electoral success of populist parties",
                ],
                "correct_option": 2,
                "explanation": "Para 4 explicitly states the answer lies in 'civic culture: a broad popular commitment to democratic norms.'",
                "key_point": "Conclusion questions: look at the final paragraph for the author's synthesising claim.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 7,
            },
            {
                "passage_key": "p2", "number": 9, "type": QuestionType.mcq,
                "text": "The passage implies that populist movements pose a threat to liberal democracy primarily because:",
                "options": [
                    "They are associated with foreign interference in elections",
                    "They challenge the legitimacy of counter-majoritarian institutions",
                    "They promote economic policies that harm minority groups",
                    "They reduce voter turnout among educated populations",
                ],
                "correct_option": 1,
                "explanation": "Para 3: populists target 'self-serving elites — including the judiciary and press' — institutions that are precisely the counter-majoritarian safeguards described earlier.",
                "key_point": "Inference: connect the specific threat (populist attacks on judiciary/press) to the framework established in Para 1-2.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 8,
            },
            {
                "passage_key": "p2", "number": 10, "type": QuestionType.mcq,
                "text": "Which of the following best describes the overall tone of the passage?",
                "options": [
                    "Alarmist — predicting the imminent collapse of democracy",
                    "Celebratory — affirming the strength of democratic institutions",
                    "Analytically concerned — examining tensions with guarded optimism",
                    "Cynical — dismissing democracy as inherently contradictory",
                ],
                "correct_option": 2,
                "explanation": "The passage maps tensions honestly (concerned), tests them against real threats, but ends with a (guarded) civic-culture solution — not collapse, not celebration, not cynicism.",
                "key_point": "Tone questions: the correct answer often occupies the moderate register, not an extreme one.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 9,
            },
            # VA Questions (Q11-Q16)
            {
                "passage_key": None, "number": 11, "type": QuestionType.tita,
                "text": "Arrange into a coherent paragraph:\nA. The crisis had been building for years, visible to those who chose to look.\nB. No single event can be blamed for the collapse — it was systemic.\nC. When it finally came, it surprised only those who had ignored the warnings.\nD. Analysts later identified at least a dozen moments when intervention could have helped.",
                "options": None,
                "correct_answer": "BACD",
                "hint": "Type as letters e.g. ABCD",
                "explanation": "B is the thesis (systemic, not single event). A provides temporal context (years of building). C is the climactic event. D is the retrospective analysis.",
                "key_point": "Thesis first, then chronology: B (claim) → A (buildup) → C (event) → D (aftermath).",
                "marks_correct": 3, "marks_incorrect": 0, "order_index": 10,
            },
            {
                "passage_key": None, "number": 12, "type": QuestionType.tita,
                "text": "Arrange into a coherent paragraph:\nA. By contrast, synthetic dyes were cheap, consistent, and could be produced at industrial scale.\nB. Natural dyes — derived from plants, insects, and minerals — dominated textile production for millennia.\nC. The discovery of the first synthetic dye in 1856 began a transformation that would reshape global trade.\nD. Within decades, the ancient indigo trade from India had effectively collapsed.",
                "options": None,
                "correct_answer": "BCAD",
                "hint": "Type as letters e.g. ABCD",
                "explanation": "B introduces natural dyes (historical context). C is the turning point (1856). A contrasts synthetic with natural. D is the consequence (indigo trade collapse).",
                "key_point": "Historical passages: look for the turning point sentence — it divides before and after.",
                "marks_correct": 3, "marks_incorrect": 0, "order_index": 11,
            },
            {
                "passage_key": None, "number": 13, "type": QuestionType.para_summary,
                "text": "Creativity is often romanticised as a flash of inspiration — a bolt from the blue that strikes the exceptional individual. Research in cognitive psychology tells a different story. Creative insights typically follow sustained periods of preparation, incubation, and iterative revision. The 'aha moment' is real, but it is the product of invisible cognitive work, not divine visitation.\n\nChoose the best summary:",
                "options": [
                    "Creative individuals are born, not made, and inspiration cannot be taught.",
                    "Research shows creativity is a gradual cognitive process, not a spontaneous flash of genius.",
                    "The 'aha moment' is a myth and should be replaced with systematic problem-solving techniques.",
                    "Cognitive psychology has not yet fully explained the mechanisms of creative insight.",
                ],
                "correct_option": 1,
                "explanation": "The paragraph challenges the romanticised view and presents the cognitive psychology account — preparation, incubation, revision. Option B captures this accurately without overclaiming (it does not say the aha moment is a myth).",
                "key_point": "The summary must match the paragraph's nuance: the aha moment is real, but explained differently.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 12,
            },
            {
                "passage_key": None, "number": 14, "type": QuestionType.para_summary,
                "text": "The concept of 'cultural fit' in hiring has been criticised for entrenching homogeneity in organisations. When hiring managers use intuitive judgments about whether a candidate 'fits,' they often replicate the demographic and social characteristics of existing teams. This reduces cognitive diversity — the range of perspectives, problem-solving approaches, and knowledge backgrounds — which research consistently links to better organisational outcomes.\n\nChoose the best summary:",
                "options": [
                    "Cultural fit assessments are always subjective and therefore invalid.",
                    "Hiring for cultural fit reduces diversity and may harm organisational performance.",
                    "Organisations should abandon personality assessments entirely in favour of skills testing.",
                    "Cognitive diversity is the only meaningful form of diversity in professional environments.",
                ],
                "correct_option": 1,
                "explanation": "The paragraph argues cultural fit hiring leads to homogeneity → less cognitive diversity → worse outcomes. Option B captures this causal chain without overstating.",
                "key_point": "'May harm' is the accurate register — the passage says research links diversity to better outcomes, not that cultural fit always harms.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 13,
            },
            {
                "passage_key": None, "number": 15, "type": QuestionType.odd_one_out,
                "text": "Four sentences form a coherent paragraph. Identify the one that does NOT belong:\n\nA. Vaccines work by introducing a weakened or inactivated pathogen, triggering an immune response.\nB. The resulting antibodies provide protection against future infection by the same pathogen.\nC. Some vaccines require booster doses to maintain immunity over time.\nD. Antibiotics disrupt bacterial cell wall synthesis and are ineffective against viruses.",
                "options": ["A", "B", "C", "D"],
                "correct_option": 3,
                "explanation": "A, B, C are all about how vaccines work and their properties. D introduces antibiotics — a completely different class of treatment with no connection to the vaccine mechanism being described.",
                "key_point": "An odd one out often introduces a different category of object (here: antibiotics vs vaccines).",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 14,
            },
            {
                "passage_key": None, "number": 16, "type": QuestionType.odd_one_out,
                "text": "Four sentences form a coherent paragraph. Identify the one that does NOT belong:\n\nA. Globalisation has accelerated the cross-border flow of goods, capital, and people.\nB. Multinational corporations have expanded their supply chains across multiple continents.\nC. International trade agreements have reduced tariffs and simplified customs procedures.\nD. Many economists argue that comparative advantage theory underlies the case for free trade.",
                "options": ["A", "B", "C", "D"],
                "correct_option": 3,
                "explanation": "A, B, C all describe observable, empirical features of globalisation. D introduces a theoretical/academic argument about the basis of free trade — a shift in register from empirical observation to economic theory.",
                "key_point": "Register shifts (empirical → theoretical) can signal an odd one out even when the topic seems related.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 15,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MOCK 3: Para Jumbles Topic Test  (Topic — 10Q, 20 min, Easy)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "mock": {
            "title":           "Para Jumbles",
            "subtitle":        "Verbal Ability",
            "description":     "CAT-level para jumbles — both MCQ sequences and TITA open-order questions.",
            "type":            MockType.topic,
            "icon":            "🔀",
            "badge":           None,
            "difficulty":      DifficultyLevel.easy,
            "total_duration":  "20 Minutes",
            "duration_secs":   1200,
            "total_questions": 10,
            "max_score":       30,
            "attempt_count":   2800,
            "topics":          ["VA", "Para Jumbles"],
            "order_index":     3,
        },
        "sections": [
            {
                "section_key":  "va",
                "label":        "VA",
                "icon":         "🔤",
                "duration":     "20 mins",
                "duration_secs": 1200,
                "questions":    10,
                "breakdown":    "5 MCQ Sequences + 5 TITA Open Order",
                "color":        "#1F3B1F",
                "is_locked":    False,
                "order_index":  0,
            }
        ],
        "marking": {
            "correct_marks":   3,
            "incorrect_marks": -1,
            "tita_marks":      0,
            "correct_sub":     "For MCQ correct answers",
            "wrong_sub":       "For wrong MCQ answers only",
            "tita_sub":        "TITA questions — no negative marking",
            "has_tita":        True,
        },
        "rules": [
            {"icon": "🔀", "label": "Para Jumbles Only",       "order_index": 0},
            {"icon": "✅", "label": "TITA — No Negatives",     "order_index": 1},
            {"icon": "⏸️", "label": "Cannot Pause Test",       "order_index": 2},
            {"icon": "📱", "label": "Auto-submit on Timeout",  "order_index": 3},
        ],
        "syllabus": [
            {"label": "5-Sentence Para Jumbles (MCQ)",   "covered": True,  "order_index": 0},
            {"label": "TITA Open Order Para Jumbles",    "covered": True,  "order_index": 1},
            {"label": "Odd Sentence Out",                "covered": False, "order_index": 2},
            {"label": "Para Completion",                 "covered": False, "order_index": 3},
        ],
        "instructions": [
            {"text": "Test auto-submits after 20 minutes.",                                             "order_index": 0},
            {"text": "MCQ questions: pick the correct sequence from 4 options.",                       "order_index": 1},
            {"text": "TITA questions: type the sequence (e.g., BCDE) — no negative marking.",         "order_index": 2},
            {"text": "Look for logical connectors and topic continuity.",                              "order_index": 3},
            {"text": "Opening and closing sentences are usually easier to spot.",                     "order_index": 4},
        ],
        "passages": [],
        "questions": [
            # MCQ Para Jumbles (Q1-Q5)
            {
                "passage_key": None, "number": 1, "type": QuestionType.para_jumble,
                "text": "Choose the most logical sequence:\n\nA. However, this does not mean that all ethical frameworks converge on identical conclusions.\nB. Many ethical theories share a commitment to reducing unnecessary suffering.\nC. Utilitarianism calculates suffering in aggregate; deontology prohibits certain acts regardless of outcome.\nD. The overlap is real but partial, and the divergences matter enormously in hard cases.",
                "options": ["BACD", "ABCD", "BCAD", "CABD"],
                "correct_option": 0,
                "explanation": "B makes the convergence claim. A introduces the caveat. C provides the specific divergence example. D synthesises — the overlap is partial.",
                "key_point": "MCQ para jumbles: eliminate obviously wrong sequences first by checking opening and closing sentences.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 0,
            },
            {
                "passage_key": None, "number": 2, "type": QuestionType.para_jumble,
                "text": "Choose the most logical sequence:\n\nA. The ocean absorbs roughly a quarter of the carbon dioxide humans emit each year.\nB. This acidification threatens shellfish, coral reefs, and the marine food chain.\nC. As CO₂ dissolves in seawater, it forms carbonic acid, lowering the ocean's pH.\nD. Ocean acidification is one of the least discussed but most consequential effects of climate change.",
                "options": ["DACB", "ADCB", "ABCD", "CABD"],
                "correct_option": 0,
                "explanation": "D is the topic introduction (least discussed but consequential). A gives the mechanism (absorption). C explains the chemistry. B gives the consequence.",
                "key_point": "Introductory sentences often make a broad evaluative claim before the specific details follow.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 1,
            },
            {
                "passage_key": None, "number": 3, "type": QuestionType.para_jumble,
                "text": "Choose the most logical sequence:\n\nA. Its symptoms — fatigue, poor concentration, emotional volatility — are indistinguishable from those of burnout.\nB. Chronic loneliness is increasingly recognised as a serious public health concern.\nC. This misattribution means loneliness often goes untreated while its real cause remains unaddressed.\nD. Many individuals experiencing loneliness attribute their distress to work-related stress.",
                "options": ["BDAC", "BADC", "ABDC", "DABC"],
                "correct_option": 1,
                "explanation": "B introduces loneliness as a public health concern. A describes its symptoms. D introduces the misattribution. C gives the consequence of misattribution.",
                "key_point": "Look for cause-and-effect chains: symptom → misattribution → consequence.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 2,
            },
            {
                "passage_key": None, "number": 4, "type": QuestionType.para_jumble,
                "text": "Choose the most logical sequence:\n\nA. The result was an unprecedented fusion of African rhythmic traditions and European harmonic structures.\nB. Jazz emerged in New Orleans in the early twentieth century from a confluence of cultural streams.\nC. This fusion would go on to influence virtually every subsequent genre of popular music.\nD. African-American communities brought blues, spirituals, and ragtime into contact with brass band traditions.",
                "options": ["BDAC", "BADC", "ABCD", "BCAD"],
                "correct_option": 0,
                "explanation": "B introduces jazz and its origins. D specifies the cultural contributions. A describes the resulting fusion. C gives the historical impact.",
                "key_point": "Historical sequences: introduction → specific contributing factors → immediate result → broader impact.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 3,
            },
            {
                "passage_key": None, "number": 5, "type": QuestionType.para_jumble,
                "text": "Choose the most logical sequence:\n\nA. Yet the same technologies that enable remote work also blur the boundary between professional and personal life.\nB. The pandemic accelerated the adoption of remote work, initially out of necessity.\nC. The long-term consequences for productivity, creativity, and worker wellbeing remain genuinely uncertain.\nD. For many workers, the flexibility this brought was a significant improvement in quality of life.",
                "options": ["BDAC", "BADC", "ABCD", "BCAD"],
                "correct_option": 1,
                "explanation": "B introduces remote work adoption. A gives the immediate benefit for workers. D introduces the complication. C gives the concluding uncertainty.",
                "key_point": "Contrast transitions ('yet', 'however') signal a pivot — place them after the claim they qualify.",
                "marks_correct": 3, "marks_incorrect": -1, "order_index": 4,
            },
            # TITA Para Jumbles (Q6-Q10)
            {
                "passage_key": None, "number": 6, "type": QuestionType.tita,
                "text": "Arrange into a coherent paragraph:\nA. Psychological research suggests people consistently overestimate how much others notice and judge them.\nB. This phenomenon — known as the spotlight effect — leads to unnecessary social anxiety.\nC. In reality, most people are far too preoccupied with their own concerns to scrutinise others closely.\nD. Awareness of the spotlight effect can be liberating: you are not, in fact, the protagonist of everyone else's story.",
                "options": None, "correct_answer": "ABCD",
                "hint": "Type as letters e.g. ABCD",
                "explanation": "A introduces the research finding. B names the phenomenon. C provides the corrective reality. D gives the practical takeaway.",
                "key_point": "Research claim → name/label → corrective insight → practical implication is a classic structure.",
                "marks_correct": 3, "marks_incorrect": 0, "order_index": 5,
            },
            {
                "passage_key": None, "number": 7, "type": QuestionType.tita,
                "text": "Arrange into a coherent paragraph:\nA. This asymmetry — where losses feel roughly twice as painful as equivalent gains feel pleasurable — distorts economic decision-making.\nB. Loss aversion is among the most robust findings in behavioural economics.\nC. It explains why people hold losing investments too long and sell winning ones too soon.\nD. Kahneman and Tversky demonstrated it empirically through a series of elegant experiments.",
                "options": None, "correct_answer": "BDAC",
                "hint": "Type as letters e.g. ABCD",
                "explanation": "B introduces the concept. D provides empirical backing. A describes the asymmetry finding. C gives the practical manifestation.",
                "key_point": "Concept → evidence → elaboration → application is a standard academic structure.",
                "marks_correct": 3, "marks_incorrect": 0, "order_index": 6,
            },
            {
                "passage_key": None, "number": 8, "type": QuestionType.tita,
                "text": "Arrange into a coherent paragraph:\nA. The domestication of fire gave early humans access to cooked food, which is easier to digest and more calorically dense.\nB. This caloric surplus may have supported the expansion of the brain over evolutionary time.\nC. Richard Wrangham's cooking hypothesis proposes that fire was the pivotal technology in human evolution.\nD. The reduction in gut size that followed freed energy for neural tissue — a costly organ to maintain.",
                "options": None, "correct_answer": "CABD",
                "hint": "Type as letters e.g. ABCD",
                "explanation": "C introduces the hypothesis. A explains the immediate benefit (cooked food). B explains the evolutionary consequence (brain expansion). D adds the mechanism (gut reduction freeing energy).",
                "key_point": "Hypothesis first, then causal chain: C (hypothesis) → A (proximate effect) → B (ultimate consequence) → D (mechanism).",
                "marks_correct": 3, "marks_incorrect": 0, "order_index": 7,
            },
            {
                "passage_key": None, "number": 9, "type": QuestionType.tita,
                "text": "Arrange into a coherent paragraph:\nA. The printing press democratised access to information, breaking the Church's near-monopoly on literacy.\nB. Yet it also enabled the rapid spread of misinformation, including inflammatory pamphlets that fuelled religious wars.\nC. The internet has replicated this double-edged dynamic at vastly greater speed and scale.\nD. Technologies that distribute information power tend to be simultaneously liberating and destabilising.",
                "options": None, "correct_answer": "ABCD",
                "hint": "Type as letters e.g. ABCD",
                "explanation": "A gives the benefit of the printing press. B introduces the cost. C makes the analogy to the internet. D is the generalising conclusion — a classic specific-to-general structure.",
                "key_point": "When a sentence generalises the pattern of all previous sentences, it is the conclusion.",
                "marks_correct": 3, "marks_incorrect": 0, "order_index": 8,
            },
            {
                "passage_key": None, "number": 10, "type": QuestionType.tita,
                "text": "Arrange into a coherent paragraph:\nA. A species survives not because it is the strongest but because it responds most effectively to change.\nB. Darwin's insight was subtler than the popular caricature of 'survival of the fittest' suggests.\nC. Fitness, in evolutionary biology, is not strength or intelligence but reproductive success in a given environment.\nD. An organism perfectly adapted to a stable environment may be catastrophically vulnerable to disruption.",
                "options": None, "correct_answer": "BCAD",
                "hint": "Type as letters e.g. ABCD",
                "explanation": "B corrects the popular misconception. C defines fitness precisely. A extends with the implication (responds to change, not strongest). D gives the corollary (disruption vulnerability).",
                "key_point": "Misconception → precise definition → implication → corollary is a classic analytical structure.",
                "marks_correct": 3, "marks_incorrect": 0, "order_index": 9,
            },
        ],
    },
]


# ─── SEED RUNNER ──────────────────────────────────────────────────────────────

async def seed():
    async with AsyncSessionLocal() as db:
        added   = 0
        skipped = 0

        for data in MOCKS:
            mock_data   = data["mock"]
            title       = mock_data["title"]

            # Skip if already exists
            result = await db.execute(select(MockTest).where(MockTest.title == title))
            if result.scalar_one_or_none():
                print(f"⏭️  Skipped: {title}")
                skipped += 1
                continue

            # ── Create MockTest ──
            mock = MockTest(**mock_data)
            db.add(mock)
            await db.flush()
            print(f"✅ Mock: {title}")

            # ── Marking Scheme ──
            scheme = MarkingScheme(mock_id=mock.id, **data["marking"])
            db.add(scheme)

            # ── Rules ──
            for r in data["rules"]:
                db.add(MockRule(mock_id=mock.id, **r))

            # ── Syllabus ──
            for s in data["syllabus"]:
                db.add(MockSyllabus(mock_id=mock.id, **s))

            # ── Instructions ──
            for i in data["instructions"]:
                db.add(MockInstruction(mock_id=mock.id, **i))

            await db.flush()

            # ── Sections ──
            for section_data in data["sections"]:
                section = MockSection(mock_id=mock.id, **section_data)
                db.add(section)
                await db.flush()
                print(f"   📂 Section: {section.label}")

                # ── Passages for this section ──
                passage_key_to_id: dict[str, object] = {}

                for p_data in data.get("passages", []):
                    passage = Passage(
                        section_id  = section.id,
                        passage_key = p_data["passage_key"],
                        label       = p_data.get("label"),
                        title       = p_data.get("title"),
                        content     = p_data.get("content", []),
                    )
                    db.add(passage)
                    await db.flush()
                    passage_key_to_id[p_data["passage_key"]] = passage.id
                    print(f"      📄 Passage: {p_data['passage_key']}")

                # ── Questions for this section ──
                for q_data in data.get("questions", []):
                    pk  = q_data.pop("passage_key", None)
                    pid = passage_key_to_id.get(pk) if pk else None

                    question = MockQuestion(
                        section_id   = section.id,
                        passage_id   = pid,
                        **{k: v for k, v in q_data.items()},
                    )
                    db.add(question)

                print(f"      ❓ {len(data.get('questions', []))} questions added")

            await db.flush()
            added += 1

        await db.commit()
        print(f"\n🎉 Done! Added: {added}, Skipped: {skipped}")


if __name__ == "__main__":
    asyncio.run(seed())