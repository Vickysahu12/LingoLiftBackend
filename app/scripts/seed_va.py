import asyncio
import sys
sys.path.insert(0, r"D:\Verbify\backend")

from app.db.database import AsyncSessionLocal
from app.account.models import User
from app.models.va import VAQuestion, VAAttempt, VAProgress
from sqlalchemy import select

VA_QUESTIONS = [
    # ─── Para Jumble ──────────────────────────────────────────
    {
        "question_type": "para_jumble",
        "question": "Arrange the sentences to form a coherent paragraph.",
        "options": [
            {"id": "A", "text": "BDCA"},
            {"id": "B", "text": "ABDC"},
            {"id": "C", "text": "DBCA"},
            {"id": "D", "text": "BDAC"},
        ],
        "correct": "A",
        "explanation": {
            "correct": "A",
            "why": "B introduces the topic, D adds supporting evidence, C provides contrast with 'However', and A concludes with implications."
        },
        "strategy": {"icon": "🔍", "label": "Opening Sentence Strategy"},
        "difficulty": "Medium",
        "order_index": 1
    },
    {
        "question_type": "para_jumble",
        "question": "Choose the correct order of sentences A, B, C, D to make a meaningful paragraph.",
        "options": [
            {"id": "A", "text": "CABD"},
            {"id": "B", "text": "ABCD"},
            {"id": "C", "text": "CDAB"},
            {"id": "D", "text": "BCAD"},
        ],
        "correct": "C",
        "explanation": {
            "correct": "C",
            "why": "C sets the broad context, D narrows it down, A provides an example, and B concludes with a result."
        },
        "strategy": {"icon": "🔗", "label": "Transition Word Strategy"},
        "difficulty": "Hard",
        "order_index": 2
    },
    # ─── Odd One Out ──────────────────────────────────────────
    {
        "question_type": "odd_one_out",
        "question": "Five sentences are given. Four form a coherent paragraph. Identify the odd sentence.",
        "options": [
            {"id": "A", "text": "Globalization has accelerated the flow of capital across borders."},
            {"id": "B", "text": "Digital currencies are reshaping payment infrastructure globally."},
            {"id": "C", "text": "Ancient barter systems predate modern monetary exchange."},
            {"id": "D", "text": "Multinational corporations benefit from reduced trade barriers."},
        ],
        "correct": "C",
        "explanation": {
            "correct": "C",
            "why": "A, B, and D discuss contemporary economic phenomena. C introduces ancient history which is thematically disconnected from the modern economic focus."
        },
        "strategy": {"icon": "🎯", "label": "Theme Identification Strategy"},
        "difficulty": "Medium",
        "order_index": 1
    },
    {
        "question_type": "odd_one_out",
        "question": "Identify the sentence that does not fit with the others.",
        "options": [
            {"id": "A", "text": "Climate change poses an existential risk to coastal cities worldwide."},
            {"id": "B", "text": "Renewable energy adoption has accelerated in the past decade."},
            {"id": "C", "text": "The Amazon rainforest produces 20% of the world's oxygen."},
            {"id": "D", "text": "The stock market witnessed unprecedented volatility last quarter."},
        ],
        "correct": "D",
        "explanation": {
            "correct": "D",
            "why": "A, B, and C all relate to environmental themes. D introduces financial market volatility which is unrelated to the environmental context."
        },
        "strategy": {"icon": "🎯", "label": "Theme Identification Strategy"},
        "difficulty": "Easy",
        "order_index": 2
    },
    # ─── Para Summary ─────────────────────────────────────────
    {
        "question_type": "para_summary",
        "question": "The rise of artificial intelligence has prompted widespread debate about the future of employment. While optimists argue that AI will create new categories of jobs, skeptics warn of mass displacement. Historical precedents suggest that technological revolutions do disrupt labor markets, but societies eventually adapt. The net outcome depends heavily on policy responses and educational investments.",
        "options": [
            {"id": "A", "text": "AI will definitely cause mass unemployment globally."},
            {"id": "B", "text": "The impact of AI on employment is debated, with outcomes depending on policy and education."},
            {"id": "C", "text": "Historical precedents prove AI cannot harm employment."},
            {"id": "D", "text": "Optimists believe AI will only create new jobs without any displacement."},
        ],
        "correct": "B",
        "explanation": {
            "correct": "B",
            "why": "B correctly captures the balanced perspective — acknowledging the debate, historical context, and the role of policy. Other options are either too extreme or partially correct."
        },
        "strategy": {"icon": "📝", "label": "Central Idea Strategy"},
        "difficulty": "Medium",
        "order_index": 1
    },
    {
        "question_type": "para_summary",
        "question": "Democratic institutions are increasingly under strain globally. Rising populism, erosion of judicial independence, and media consolidation have weakened checks and balances in several nations. Scholars argue that democracy requires active civic participation to survive. Without informed citizens and strong institutions, democratic backsliding becomes inevitable.",
        "options": [
            {"id": "A", "text": "Populism is the sole cause of democratic decline worldwide."},
            {"id": "B", "text": "Democracy is failing in all countries due to media consolidation."},
            {"id": "C", "text": "Democratic institutions face threats from multiple factors and require civic engagement to survive."},
            {"id": "D", "text": "Strong judicial systems alone can prevent democratic backsliding."},
        ],
        "correct": "C",
        "explanation": {
            "correct": "C",
            "why": "C best summarizes the passage — it identifies multiple threats (populism, judicial erosion, media) and the solution (civic participation). Others are either too narrow or distort the meaning."
        },
        "strategy": {"icon": "📝", "label": "Central Idea Strategy"},
        "difficulty": "Hard",
        "order_index": 2
    },
]

async def seed():
    async with AsyncSessionLocal() as db:
        added = 0
        skipped = 0

        for q_data in VA_QUESTIONS:
            result = await db.execute(
                select(VAQuestion).where(
                    VAQuestion.question == q_data["question"]
                )
            )
            if result.scalar_one_or_none():
                print(f"⏭️  Skipped: {q_data['question_type']} - {q_data['question'][:40]}...")
                skipped += 1
                continue

            question = VAQuestion(**q_data)
            db.add(question)
            added += 1
            print(f"✅ Added: {q_data['question_type']} - {q_data['question'][:40]}...")

        await db.commit()
        print(f"\n🎉 Done! Added: {added}, Skipped: {skipped}")

if __name__ == "__main__":
    asyncio.run(seed())