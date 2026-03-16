import asyncio
import sys
sys.path.insert(0, r"D:\Verbify\backend")

from app.db.database import AsyncSessionLocal
from app.account.models import User
from app.models.rc import RCPassage, RCQuestion, RCOption
from sqlalchemy import select

RC_DATA = [
    {
        "title": "The Evolution of Economic Thought",
        "body": "Classical economists believed that markets function best when left alone. They emphasized free markets, division of labor, and the invisible hand as self-regulating forces. [HOWEVER] later schools questioned this assumption, arguing that markets were not always efficient.\n\nKeynesian economists, for instance, believed that government intervention was necessary during recessions. Meanwhile, monetarists focused on controlling the money supply. Each school represented a response to the perceived failures of its predecessor.",
        "subject": "Reading Comprehension",
        "difficulty": "Medium",
        "source": "CAT 2023",
        "order_index": 1,
        "questions": [
            {
                "question": "According to the passage, what was the primary focus of the classical school of economic thought?",
                "difficulty": "Easy",
                "analysis": "The passage clearly states that classical economists emphasized free markets, division of labor, and the invisible hand as self-regulating forces of the economy.",
                "order_index": 0,
                "options": [
                    {"option_text": "The necessity of government intervention during recessions.", "is_correct": False, "order_index": 0},
                    {"option_text": "Free markets, division of labor, and the invisible hand.", "is_correct": True,  "order_index": 1},
                    {"option_text": "The management of money supply to control national output.", "is_correct": False, "order_index": 2},
                    {"option_text": "The implementation of rational expectations in decision making.", "is_correct": False, "order_index": 3},
                ]
            },
            {
                "question": "Why did later schools of thought challenge classical economics?",
                "difficulty": "Medium",
                "analysis": "The passage states that later schools believed markets were not always efficient, implying that real-world economic downturns exposed the limitations of the free-market model.",
                "order_index": 1,
                "options": [
                    {"option_text": "Markets failed to generate employment.", "is_correct": False, "order_index": 0},
                    {"option_text": "Government intervention proved ineffective.", "is_correct": False, "order_index": 1},
                    {"option_text": "Economic downturns exposed limitations of free markets.", "is_correct": True,  "order_index": 2},
                    {"option_text": "Division of labor reduced productivity.", "is_correct": False, "order_index": 3},
                ]
            },
            {
                "question": "What does the passage suggest about the relationship between economic schools of thought?",
                "difficulty": "Hard",
                "analysis": "The final sentence explicitly states that each school represented a response to the perceived failures of its predecessor, indicating an evolutionary, reactive relationship.",
                "order_index": 2,
                "options": [
                    {"option_text": "They developed independently of one another.", "is_correct": False, "order_index": 0},
                    {"option_text": "Each school built upon and agreed with prior theories.", "is_correct": False, "order_index": 1},
                    {"option_text": "Each school emerged as a response to its predecessor's perceived failures.", "is_correct": True,  "order_index": 2},
                    {"option_text": "Classical economics remained dominant throughout history.", "is_correct": False, "order_index": 3},
                ]
            },
        ]
    },
    {
        "title": "The Digital Divide",
        "body": "The rapid proliferation of digital technology has created an unprecedented divide between those who have access to the internet and those who do not. This digital divide is not merely a technical issue but a profound social and economic challenge.\n\nIn developing nations, lack of infrastructure, affordability, and digital literacy compound the problem. [FURTHERMORE] even within developed economies, marginalized communities often remain excluded from the digital revolution.\n\nExperts argue that bridging this divide requires coordinated efforts from governments, private sectors, and civil society to ensure equitable access to information and opportunity.",
        "subject": "Reading Comprehension",
        "difficulty": "Hard",
        "source": "CAT 2022",
        "order_index": 2,
        "questions": [
            {
                "question": "According to the passage, the digital divide is best described as:",
                "difficulty": "Easy",
                "analysis": "The passage explicitly states it is 'not merely a technical issue but a profound social and economic challenge'.",
                "order_index": 0,
                "options": [
                    {"option_text": "Purely a technological infrastructure problem.", "is_correct": False, "order_index": 0},
                    {"option_text": "A social and economic challenge beyond just technology.", "is_correct": True,  "order_index": 1},
                    {"option_text": "A problem limited to developing nations.", "is_correct": False, "order_index": 2},
                    {"option_text": "An issue only affecting marginalized communities.", "is_correct": False, "order_index": 3},
                ]
            },
            {
                "question": "The word [FURTHERMORE] in the passage serves to:",
                "difficulty": "Medium",
                "analysis": "FURTHERMORE adds an additional point — extending the problem from developing nations to developed economies as well.",
                "order_index": 1,
                "options": [
                    {"option_text": "Contradict the previous statement.", "is_correct": False, "order_index": 0},
                    {"option_text": "Introduce a new unrelated argument.", "is_correct": False, "order_index": 1},
                    {"option_text": "Add a supporting point to the existing argument.", "is_correct": True,  "order_index": 2},
                    {"option_text": "Summarize the passage's central idea.", "is_correct": False, "order_index": 3},
                ]
            },
            {
                "question": "What solution does the passage propose for the digital divide?",
                "difficulty": "Easy",
                "analysis": "The passage clearly states that coordinated efforts from governments, private sectors, and civil society are required.",
                "order_index": 2,
                "options": [
                    {"option_text": "Governments alone should fund digital infrastructure.", "is_correct": False, "order_index": 0},
                    {"option_text": "Private companies should lead the effort.", "is_correct": False, "order_index": 1},
                    {"option_text": "Coordinated efforts from multiple stakeholders are needed.", "is_correct": True,  "order_index": 2},
                    {"option_text": "Digital literacy programs are sufficient.", "is_correct": False, "order_index": 3},
                ]
            },
        ]
    },
]

async def seed():
    async with AsyncSessionLocal() as db:
        added = 0
        skipped = 0

        for passage_data in RC_DATA:
            # Already exists?
            result = await db.execute(
                select(RCPassage).where(RCPassage.title == passage_data["title"])
            )
            if result.scalar_one_or_none():
                print(f"⏭️  Skipped: {passage_data['title']}")
                skipped += 1
                continue

            # Add passage
            questions = passage_data.pop("questions")
            passage = RCPassage(**passage_data)
            db.add(passage)
            await db.flush()

            # Add questions + options
            for q_data in questions:
                options = q_data.pop("options")
                question = RCQuestion(passage_id=passage.id, **q_data)
                db.add(question)
                await db.flush()

                for opt_data in options:
                    option = RCOption(question_id=question.id, **opt_data)
                    db.add(option)

            added += 1
            print(f"✅ Added: {passage_data['title']}")

        await db.commit()
        print(f"\n🎉 Done! Added: {added}, Skipped: {skipped}")

if __name__ == "__main__":
    asyncio.run(seed())