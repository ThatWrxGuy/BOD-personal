"""Fitness Domain Data Models.

Canonical models for fitness domain data including:
- Exercise libraries
- Workout templates
- Fitness guidance
- Activity data
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class ExerciseRecord(BaseModel):
    """Exercise record from exercise library."""
    record_id: UUID = Field(default_factory=uuid4)
    exercise_name: str = Field(..., description="Exercise name")
    
    # Classification
    category: str = Field(..., description="Exercise category (strength, cardio, etc.)")
    muscle_groups: List[str] = Field(default_factory=list, description="Primary muscle groups")
    equipment: List[str] = Field(default_factory=list, description="Equipment needed")
    difficulty: str = Field(..., description="Difficulty level (beginner, intermediate, advanced)")
    
    # Details
    description: str = Field(..., description="Exercise description")
    instructions: List[str] = Field(default_factory=list, description="Step-by-step instructions")
    tips: Optional[List[str]] = Field(None, description="Tips for proper form")
    variations: Optional[List[str]] = Field(None, description="Exercise variations")
    
    # Metrics
    primary_metric: str = Field(..., description="Primary metric (reps, time, distance, etc.)")
    recommended_sets: Optional[int] = Field(None, description="Recommended sets")
    recommended_reps: Optional[int] = Field(None, description="Recommended reps")
    recommended_duration_seconds: Optional[int] = Field(None, description="Recommended duration")
    
    source_id: str = Field("fitness_exercise_lib", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkoutTemplate(BaseModel):
    """Pre-defined workout template."""
    template_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    
    # Classification
    workout_type: str = Field(..., description="Workout type")
    target_goal: str = Field(..., description="Target fitness goal")
    difficulty: str = Field(..., description="Difficulty level")
    estimated_duration_minutes: int = Field(..., description="Estimated duration")
    
    # Structure
    exercises: List[dict] = Field(default_factory=list, description="Exercises in workout")
    warmup: Optional[List[dict]] = Field(None, description="Warmup exercises")
    cooldown: Optional[List[dict]] = Field(None, description="Cooldown exercises")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Workout tags")
    created_by: Optional[str] = Field(None, description="Creator")
    source_id: str = Field("fitness_templates", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FitnessGuidanceDocument(BaseModel):
    """Fitness guidance document."""
    document_id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    category: str = Field(..., description="Guidance category")
    topic: str = Field(..., description="Specific topic")
    
    # Classification
    target_audience: str = Field(..., description="Target audience")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    
    # Evidence
    evidence_based: bool = Field(True, description="Whether evidence-based")
    sources: Optional[List[str]] = Field(None, description="Source references")
    
    source_id: str = Field("fitness_guidance", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ActivityDataRecord(BaseModel):
    """Physical activity tracking data."""
    record_id: UUID = Field(default_factory=uuid4)
    activity_type: str = Field(..., description="Type of activity")
    
    # Timing
    start_time: datetime = Field(..., description="Activity start time")
    end_time: datetime = Field(..., description="Activity end time")
    duration_minutes: int = Field(..., description="Duration in minutes")
    
    # Metrics
    calories_burned: Optional[float] = Field(None, description="Estimated calories burned")
    distance_km: Optional[float] = Field(None, description="Distance in km")
    heart_rate_avg: Optional[int] = Field(None, description="Average heart rate")
    heart_rate_max: Optional[int] = Field(None, description="Max heart rate")
    steps: Optional[int] = Field(None, description="Steps taken")
    
    # Notes
    notes: Optional[str] = Field(None, description="Activity notes")
    
    source_id: str = Field("fitness_activity_data", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
