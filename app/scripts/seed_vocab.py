import asyncio
import sys
import os

# Ye line fix karo
sys.path.insert(0, r"D:\Verbify\backend")

from app.db.database import AsyncSessionLocal
from app.account.models import User          # ← YE ADD KARO
from app.models.vocab import VocabWord
from sqlalchemy import select

WORDS = [
    {
        "word": "Anachronism",
        "phonetic": "/əˈnækrəˌnɪzəm/",
        "tag": "HIGH FREQUENCY",
        "definition": "A thing belonging to a period other than that in which it exists.",
        "synonyms": ["Misplacement", "Solecism", "Prochronism"],
        "antonyms": ["Contemporary", "Synchrony"],
        "context": "In an era of instant global communication, the concept of a nation-state with strictly guarded physical borders might increasingly be viewed as a geopolitical anachronism.",
        "source": "THE ECONOMIST",
        "article_url": "https://www.economist.com",
        "tip": "Commonly used in RC passages discussing history, technology, or societal evolution.",
        "order_index": 1
    },
    {
        "word": "Bellicose",
        "phonetic": "/ˈbɛlɪˌkoʊs/",
        "tag": "HIGH FREQUENCY",
        "definition": "Demonstrating aggression and willingness to fight; warlike.",
        "synonyms": ["Aggressive", "Pugnacious", "Hostile"],
        "antonyms": ["Peaceful", "Calm", "Pacifist"],
        "context": "The leader's bellicose rhetoric heightened tensions between the two nations.",
        "source": "THE HINDU",
        "article_url": "https://www.thehindu.com",
        "tip": "Often used to describe tone, attitude, or rhetoric in political passages.",
        "order_index": 2
    },
    {
        "word": "Capricious",
        "phonetic": "/kəˈprɪʃəs/",
        "tag": "HIGH FREQUENCY",
        "definition": "Given to sudden and unaccountable changes in mood or behavior.",
        "synonyms": ["Unpredictable", "Whimsical", "Erratic"],
        "antonyms": ["Consistent", "Stable", "Predictable"],
        "context": "The manager's capricious decisions made it difficult for the team to plan effectively.",
        "source": "THE HINDU",
        "article_url": "https://www.thehindu.com",
        "tip": "Often used in passages describing unstable leadership or erratic policy decisions.",
        "order_index": 3
    },
    {
        "word": "Didactic",
        "phonetic": "/daɪˈdæktɪk/",
        "tag": "HIGH FREQUENCY",
        "definition": "Intended to teach, particularly in a moralizing or instructive way.",
        "synonyms": ["Instructional", "Moralizing", "Preachy"],
        "antonyms": ["Entertaining", "Informal", "Casual"],
        "context": "The novel adopts a didactic tone to emphasize the importance of ethical governance.",
        "source": "THE HINDU",
        "article_url": "https://www.thehindu.com",
        "tip": "Commonly appears in RC passages discussing literature, philosophy, or ideology.",
        "order_index": 4
    },
    {
        "word": "Equanimity",
        "phonetic": "/ˌekwəˈnɪməti/",
        "tag": "HIGH FREQUENCY",
        "definition": "Mental calmness and composure, especially in difficult situations.",
        "synonyms": ["Composure", "Serenity", "Poise"],
        "antonyms": ["Agitation", "Anxiety", "Distress"],
        "context": "She handled the crisis with remarkable equanimity despite mounting pressure.",
        "source": "THE HINDU",
        "article_url": "https://www.thehindu.com",
        "tip": "Useful in RC passages involving leadership, crisis management, or psychology.",
        "order_index": 5
    },
    {
        "word": "Obfuscate",
        "phonetic": "/ˈɒbfʌskeɪt/",
        "tag": "HIGH FREQUENCY",
        "definition": "To deliberately make something unclear or difficult to understand.",
        "synonyms": ["Confuse", "Blur", "Muddle"],
        "antonyms": ["Clarify", "Explain", "Illuminate"],
        "context": "The spokesperson attempted to obfuscate the issue rather than provide a direct answer.",
        "source": "THE HINDU",
        "article_url": "https://www.thehindu.com",
        "tip": "Frequently used in political or economic editorials where clarity is intentionally avoided.",
        "order_index": 6
    },
    {
        "word": "Pragmatic",
        "phonetic": "/præɡˈmætɪk/",
        "tag": "HIGH FREQUENCY",
        "definition": "Dealing with things sensibly and realistically in a practical way.",
        "synonyms": ["Practical", "Realistic", "Sensible"],
        "antonyms": ["Idealistic", "Impractical", "Unrealistic"],
        "context": "The government adopted a pragmatic approach to address the fiscal deficit.",
        "source": "THE HINDU",
        "article_url": "https://www.thehindu.com",
        "tip": "Extremely common in CAT RC passages related to economics, governance, and policy.",
        "order_index": 7
    },
]

async def seed():
    async with AsyncSessionLocal() as db:
        added = 0
        skipped = 0
        
        for word_data in WORDS:
            # Already exists?
            result = await db.execute(
                select(VocabWord).where(VocabWord.word == word_data["word"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⏭️  Skipped (already exists): {word_data['word']}")
                skipped += 1
                continue
            
            word = VocabWord(**word_data)
            db.add(word)
            added += 1
            print(f"✅ Added: {word_data['word']}")
        
        await db.commit()
        print(f"\n🎉 Done! Added: {added}, Skipped: {skipped}")

if __name__ == "__main__":
    asyncio.run(seed())