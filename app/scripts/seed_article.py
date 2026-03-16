import asyncio
import sys
sys.path.insert(0, r"D:\Verbify\backend")

from app.db.database import AsyncSessionLocal
from app.account.models import User
from app.models.article import Article, ArticleAnalysis
from sqlalchemy import select

ARTICLES = [
    {
        "article": {
            "title": "Artificial Intelligence & Ethics",
            "tag": "Technology",
            "meta": "8 min read • Medium",
            "level": "Medium",
            "order_index": 1,
            "content": [
                "Artificial Intelligence is no longer a speculative idea confined to science fiction. It has become a structural force shaping economic, political, and ethical landscapes across the globe.",
                "The ethical dimension of AI revolves around accountability, transparency, and the distribution of power. As decision-making systems become automated, the locus of responsibility shifts from individuals to algorithms — raising profound philosophical questions.",
                "Furthermore, the geopolitical race for AI dominance reflects a deeper struggle for technological sovereignty. Nations investing in AI are not merely advancing innovation but redefining global hierarchies.",
                "Ultimately, the future of AI ethics will depend on interdisciplinary collaboration — where philosophers, policymakers, engineers, and citizens collectively shape frameworks that balance innovation with human dignity.",
            ]
        },
        "analysis": {
            "score": 88,
            "difficulty": "Hard",
            "central_idea": "The passage argues that Artificial Intelligence is not merely a technological advancement but a transformative geopolitical and ethical force that reshapes power structures, accountability, and global hierarchies.",
            "tone": {
                "main": "Analytical",
                "options": ["Objective", "Speculative"],
                "explanation": "The author dissects the ethical and geopolitical implications of AI using structured reasoning and layered argumentation rather than emotional persuasion."
            },
            "structure": [
                {"heading": "INTRODUCTION", "text": "Establishes AI as a structural force impacting economic and political systems."},
                {"heading": "ETHICAL DIMENSION", "text": "Examines accountability, transparency, and the philosophical dilemma of algorithmic responsibility."},
                {"heading": "GEOPOLITICAL CONTEXT", "text": "Discusses the global race for AI dominance as a struggle for technological sovereignty."},
                {"heading": "CONCLUSION", "text": "Advocates interdisciplinary collaboration to balance innovation with human dignity."}
            ],
            "arguments": [
                {"claim": "Shift of Accountability", "evidence": "The author highlights how automated decision systems transfer responsibility from individuals to algorithms."},
                {"claim": "Technological Sovereignty", "evidence": "AI investment is framed as redefining global hierarchies rather than merely promoting innovation."}
            ],
            "cat_tip": "In analytical passages, identify how the author moves from concept to implication. Track the logical progression between ethics and geopolitics."
        }
    },
    {
        "article": {
            "title": "The Global Inflation Crisis",
            "tag": "Economics",
            "meta": "7 min read • Easy",
            "level": "Easy",
            "order_index": 2,
            "content": [
                "Inflation has emerged as one of the most pressing economic challenges of the modern era. Rising prices reduce purchasing power and disproportionately affect lower-income households.",
                "Central banks attempt to manage inflation through interest rate adjustments. However, monetary tightening often slows economic growth and increases unemployment.",
                "The post-pandemic supply chain disruptions, combined with geopolitical tensions, have intensified price instability across global markets.",
                "Understanding inflation requires examining both structural economic policies and behavioral consumer dynamics."
            ]
        },
        "analysis": {
            "score": 82,
            "difficulty": "Medium",
            "central_idea": "The passage explores inflation as a multifaceted economic challenge shaped by monetary policy, supply disruptions, and geopolitical instability.",
            "tone": {
                "main": "Objective",
                "options": ["Analytical", "Critical"],
                "explanation": "The author presents economic mechanisms neutrally, focusing on cause-and-effect relationships without emotional or ideological bias."
            },
            "structure": [
                {"heading": "INTRODUCTION", "text": "Introduces inflation as a major economic issue affecting purchasing power."},
                {"heading": "MONETARY RESPONSE", "text": "Explains how central banks use interest rate adjustments to control inflation."},
                {"heading": "EXTERNAL FACTORS", "text": "Analyzes supply chain disruptions and geopolitical tensions."},
                {"heading": "CONCLUSION", "text": "Emphasizes the need to understand both policy and behavioral factors."}
            ],
            "arguments": [
                {"claim": "Monetary Tightening Trade-off", "evidence": "Raising interest rates can slow economic growth and increase unemployment."},
                {"claim": "Supply Shock Contribution", "evidence": "Post-pandemic disruptions intensified global price instability."}
            ],
            "cat_tip": "For economy-based RCs, separate structural causes from policy responses. Questions often test this distinction."
        }
    },
    {
        "article": {
            "title": "Existentialism in the Modern World",
            "tag": "Philosophy",
            "meta": "6 min read • Medium",
            "level": "Medium",
            "order_index": 3,
            "content": [
                "Existentialism emphasizes individual freedom, responsibility, and the search for meaning in an indifferent universe.",
                "Modern society, shaped by rapid technological change and social fragmentation, has intensified existential anxiety among individuals.",
                "Thinkers like Jean-Paul Sartre and Albert Camus argued that meaning is not discovered but created through conscious choice.",
                "In a digital age dominated by algorithms and conformity, existential philosophy remains profoundly relevant."
            ]
        },
        "analysis": {
            "score": 90,
            "difficulty": "Hard",
            "central_idea": "The passage argues that existentialist philosophy remains deeply relevant in the digital age as individuals confront freedom, anxiety, and meaning in rapidly changing societies.",
            "tone": {
                "main": "Reflective",
                "options": ["Analytical", "Persuasive"],
                "explanation": "The author contemplates existential ideas thoughtfully, connecting classical philosophy with modern realities."
            },
            "structure": [
                {"heading": "INTRODUCTION", "text": "Defines existentialism and its focus on freedom and responsibility."},
                {"heading": "MODERN CONTEXT", "text": "Explores how technological change intensifies existential anxiety."},
                {"heading": "PHILOSOPHICAL SUPPORT", "text": "References Sartre and Camus to explain meaning as constructed."},
                {"heading": "CONCLUSION", "text": "Reaffirms existentialism's relevance in an algorithm-driven world."}
            ],
            "arguments": [
                {"claim": "Meaning is Created", "evidence": "Sartre and Camus argue that individuals construct meaning through conscious choice."},
                {"claim": "Digital Conformity Risk", "evidence": "Algorithmic systems risk diminishing authentic individual freedom."}
            ],
            "cat_tip": "Philosophy passages often test inference questions. Focus on implied ideas rather than explicit statements."
        }
    },
]

async def seed():
    async with AsyncSessionLocal() as db:
        added = 0
        skipped = 0

        for data in ARTICLES:
            article_data = data["article"]
            analysis_data = data["analysis"]

            # Already exists?
            result = await db.execute(
                select(Article).where(Article.title == article_data["title"])
            )
            if result.scalar_one_or_none():
                print(f"⏭️  Skipped: {article_data['title']}")
                skipped += 1
                continue

            # Add article
            article = Article(**article_data)
            db.add(article)
            await db.flush()

            # Add analysis
            analysis = ArticleAnalysis(article_id=article.id, **analysis_data)
            db.add(analysis)

            added += 1
            print(f"✅ Added: {article_data['title']}")

        await db.commit()
        print(f"\n🎉 Done! Added: {added}, Skipped: {skipped}")

if __name__ == "__main__":
    asyncio.run(seed())