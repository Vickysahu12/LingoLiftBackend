from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer,
    Text, ForeignKey, JSON, Float, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.database import Base


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class MockType(str, enum.Enum):
    full  = "full"
    half  = "half"
    topic = "topic"

class DifficultyLevel(str, enum.Enum):
    easy   = "Easy"
    medium = "Medium"
    hard   = "Hard"

class BadgeType(str, enum.Enum):
    hot    = "hot"
    new    = "new"
    locked = "locked"

class QuestionType(str, enum.Enum):
    mcq          = "mcq"
    tita         = "tita"
    para_jumble  = "para_jumble"
    para_summary = "para_summary"
    odd_one_out  = "odd_one_out"

class AttemptStatus(str, enum.Enum):
    in_progress = "in_progress"
    submitted   = "submitted"
    timed_out   = "timed_out"

class QuestionStatus(str, enum.Enum):
    not_visited          = "not_visited"
    visited_not_answered = "visited_not_answered"
    answered             = "answered"
    marked_review        = "marked_review"
    answered_marked      = "answered_marked"


# ─── MOCK TEST ────────────────────────────────────────────────────────────────

class MockTest(Base):
    """
    Top-level mock test card shown in MockListScreen.
    Maps to: MOCK_DATA in MockListScreen.jsx
    """
    __tablename__ = "mock_tests"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title          = Column(String(255), nullable=False)           # "CAT Full Mock #1"
    subtitle       = Column(String(100), nullable=True)            # "VARC"
    description    = Column(Text, nullable=True)                   # shown on detail screen
    type           = Column(SAEnum(MockType), nullable=False)      # full / half / topic
    icon           = Column(String(10), default="📋")              # emoji
    badge          = Column(SAEnum(BadgeType), nullable=True)      # hot / new / locked / null
    difficulty     = Column(SAEnum(DifficultyLevel), default=DifficultyLevel.medium)
    total_duration = Column(String(30), default="40 Minutes")      # "40 Minutes"
    duration_secs  = Column(Integer, default=2400)                 # for countdown timer
    total_questions= Column(Integer, default=0)
    max_score      = Column(Integer, default=0)
    attempt_count  = Column(Integer, default=0)                    # total platform attempts
    topics         = Column(JSON, default=[])                      # ["RC", "Inference"]
    order_index    = Column(Integer, default=0)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sections   = relationship("MockSection",    back_populates="mock", cascade="all, delete", order_by="MockSection.order_index")
    marking    = relationship("MarkingScheme",  back_populates="mock", uselist=False, cascade="all, delete")
    rules      = relationship("MockRule",       back_populates="mock", cascade="all, delete", order_by="MockRule.order_index")
    syllabus   = relationship("MockSyllabus",   back_populates="mock", cascade="all, delete", order_by="MockSyllabus.order_index")
    instructions = relationship("MockInstruction", back_populates="mock", cascade="all, delete", order_by="MockInstruction.order_index")
    attempts   = relationship("TestAttempt",    back_populates="mock", cascade="all, delete")

    def __repr__(self):
        return f"<MockTest {self.title}>"


# ─── MOCK SECTION ─────────────────────────────────────────────────────────────

class MockSection(Base):
    """
    Section within a mock (currently only VARC, DILR/QA locked for v2).
    Maps to: sections[] in MockDetailScreen MOCK_DETAILS
    """
    __tablename__ = "mock_sections"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mock_id     = Column(UUID(as_uuid=True), ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False)
    section_key = Column(String(20), nullable=False)    # "varc", "dilr", "qa"
    label       = Column(String(50), nullable=False)    # "VARC"
    icon        = Column(String(10), default="📖")
    duration    = Column(String(20), default="40 mins")
    duration_secs = Column(Integer, default=2400)
    questions   = Column(Integer, default=0)
    breakdown   = Column(String(200), nullable=True)    # "3 RC Passages (15Q) + 9 VA Questions"
    color       = Column(String(20), default="#1F3B1F")
    is_locked   = Column(Boolean, default=False)        # DILR/QA locked in v1
    order_index = Column(Integer, default=0)

    # Relationships
    mock       = relationship("MockTest", back_populates="sections")
    passages   = relationship("Passage",  back_populates="section", cascade="all, delete")
    mock_questions = relationship("MockQuestion", back_populates="section", cascade="all, delete", order_by="MockQuestion.number")

    def __repr__(self):
        return f"<MockSection {self.label}>"


# ─── MARKING SCHEME ───────────────────────────────────────────────────────────

class MarkingScheme(Base):
    """
    Maps to: marking{} in MockDetailScreen
    """
    __tablename__ = "marking_schemes"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mock_id      = Column(UUID(as_uuid=True), ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False, unique=True)
    correct_marks   = Column(Integer, default=3)         # +3
    incorrect_marks = Column(Integer, default=-1)        # -1  (store as negative int)
    tita_marks      = Column(Integer, default=0)         # 0
    correct_sub     = Column(String(100), default="For every correct answer")
    wrong_sub       = Column(String(100), default="For every wrong MCQ answer")
    tita_sub        = Column(String(100), default="No negative marking for TITA")
    has_tita        = Column(Boolean, default=True)

    mock = relationship("MockTest", back_populates="marking")


# ─── MOCK RULES ───────────────────────────────────────────────────────────────

class MockRule(Base):
    """
    Maps to: rules[] chips in MockDetailScreen
    """
    __tablename__ = "mock_rules"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mock_id     = Column(UUID(as_uuid=True), ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False)
    icon        = Column(String(10), default="📋")
    label       = Column(String(100), nullable=False)
    order_index = Column(Integer, default=0)

    mock = relationship("MockTest", back_populates="rules")


# ─── MOCK SYLLABUS ────────────────────────────────────────────────────────────

class MockSyllabus(Base):
    """
    Maps to: syllabus[] checkboxes in MockDetailScreen
    """
    __tablename__ = "mock_syllabus"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mock_id     = Column(UUID(as_uuid=True), ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False)
    label       = Column(String(200), nullable=False)
    covered     = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)

    mock = relationship("MockTest", back_populates="syllabus")


# ─── MOCK INSTRUCTIONS ────────────────────────────────────────────────────────

class MockInstruction(Base):
    """
    Maps to: instructions[] in MockDetailScreen
    """
    __tablename__ = "mock_instructions"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mock_id     = Column(UUID(as_uuid=True), ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False)
    text        = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)

    mock = relationship("MockTest", back_populates="instructions")


# ─── PASSAGE ──────────────────────────────────────────────────────────────────

class Passage(Base):
    """
    RC passage — shared across questions within a section.
    Maps to: getPassage() in examData.js
    """
    __tablename__ = "passages"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("mock_sections.id", ondelete="CASCADE"), nullable=False)
    passage_key= Column(String(50), nullable=False)     # "p1", "p2" — used as passageId in frontend
    label      = Column(String(100), nullable=True)     # "Passage 1"
    title      = Column(String(200), nullable=True)     # optional passage title
    content    = Column(JSON, default=[])               # list of paragraph strings

    section    = relationship("MockSection", back_populates="passages")
    questions  = relationship("MockQuestion", back_populates="passage")


# ─── MOCK QUESTION ────────────────────────────────────────────────────────────

class MockQuestion(Base):
    """
    Individual question within a mock section.
    Maps to: questions[] in examData.js
    """
    __tablename__ = "mock_questions"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id    = Column(UUID(as_uuid=True), ForeignKey("mock_sections.id", ondelete="CASCADE"), nullable=False)
    passage_id    = Column(UUID(as_uuid=True), ForeignKey("passages.id", ondelete="SET NULL"), nullable=True)

    number        = Column(Integer, nullable=False)          # Q1, Q2... (display number)
    type          = Column(SAEnum(QuestionType), nullable=False)
    text          = Column(Text, nullable=False)
    options       = Column(JSON, nullable=True)              # list of option strings (null for TITA)
    correct_option= Column(Integer, nullable=True)          # 0-indexed (for MCQ types)
    correct_answer= Column(String(200), nullable=True)      # for TITA (e.g. "BCDA")
    hint          = Column(String(200), nullable=True)      # TITA format hint
    explanation   = Column(Text, nullable=True)             # solution explanation
    key_point     = Column(String(500), nullable=True)      # key point for solution screen
    marks_correct = Column(Integer, default=3)
    marks_incorrect = Column(Integer, default=-1)           # 0 for TITA
    order_index   = Column(Integer, default=0)

    section  = relationship("MockSection", back_populates="mock_questions")
    passage  = relationship("Passage",     back_populates="questions")
    responses= relationship("QuestionResponse", back_populates="question", cascade="all, delete")


# ─── TEST ATTEMPT ─────────────────────────────────────────────────────────────

class TestAttempt(Base):
    """
    One attempt by a user on a mock test.
    Created when user presses 'Begin Test', updated on submit.
    """
    __tablename__ = "test_attempts"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mock_id      = Column(UUID(as_uuid=True), ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False)

    status       = Column(SAEnum(AttemptStatus), default=AttemptStatus.in_progress)
    attempt_number = Column(Integer, default=1)          # 1st, 2nd reattempt etc.

    # Timing
    started_at   = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    time_taken_secs = Column(Integer, default=0)

    # Scores (computed on submit, cached here)
    score        = Column(Integer, default=0)
    max_score    = Column(Integer, default=0)
    correct      = Column(Integer, default=0)
    wrong        = Column(Integer, default=0)
    unattempted  = Column(Integer, default=0)
    accuracy     = Column(Float, default=0.0)            # 0-100

    # RC/VA breakdown (JSON for flexibility)
    section_breakdown = Column(JSON, default={})         # {rc: {...}, va: {...}}

    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user         = relationship("User", backref="test_attempts")
    mock         = relationship("MockTest", back_populates="attempts")
    responses    = relationship("QuestionResponse", back_populates="attempt", cascade="all, delete")


# ─── QUESTION RESPONSE ────────────────────────────────────────────────────────

class QuestionResponse(Base):
    """
    Per-question state during/after an attempt.
    Maps to: questionMeta{} object passed around in TestInterface/Result/Solution screens.
    """
    __tablename__ = "question_responses"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id  = Column(UUID(as_uuid=True), ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("mock_questions.id", ondelete="CASCADE"), nullable=False)

    status       = Column(SAEnum(QuestionStatus), default=QuestionStatus.not_visited)
    selected     = Column(Integer, nullable=True)        # selected option index (MCQ)
    tita_answer  = Column(String(200), nullable=True)    # typed answer (TITA)
    is_correct   = Column(Boolean, nullable=True)        # computed on submit
    time_spent_secs = Column(Integer, default=0)         # per-question time tracking

    # Relationships
    attempt  = relationship("TestAttempt",   back_populates="responses")
    question = relationship("MockQuestion",  back_populates="responses")