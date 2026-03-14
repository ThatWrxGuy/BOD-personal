"""Health & Nutrition Domain Data Models.

Canonical models for health domain data including:
- Food nutrition data
- Supplement information
- Health evidence literature
- Wellness guidance
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class FoodNutrientRecord(BaseModel):
    """Food nutrient composition record."""
    record_id: UUID = Field(default_factory=uuid4)
    fdc_id: str = Field(..., description="FoodData Central ID")
    food_name: str = Field(..., description="Food name")
    category: str = Field(..., description="Food category")
    
    # Serving information
    serving_size: float = Field(..., description="Serving size")
    serving_unit: str = Field(..., description="Serving unit")
    
    # Macros
    calories: float = Field(0, description="Calories per serving")
    protein: float = Field(0, description="Protein (g)")
    carbohydrates: float = Field(0, description="Carbohydrates (g)")
    fat_total: float = Field(0, description="Total fat (g)")
    fat_saturated: float = Field(0, description="Saturated fat (g)")
    fiber: float = Field(0, description="Fiber (g)")
    sugar: float = Field(0, description="Sugar (g)")
    sodium: float = Field(0, description="Sodium (mg)")
    
    # Micronutrients
    vitamin_a_mcg: Optional[float] = Field(None, description="Vitamin A (mcg)")
    vitamin_c_mg: Optional[float] = Field(None, description="Vitamin C (mg)")
    vitamin_d_mcg: Optional[float] = Field(None, description="Vitamin D (mcg)")
    calcium_mg: Optional[float] = Field(None, description="Calcium (mg)")
    iron_mg: Optional[float] = Field(None, description="Iron (mg)")
    potassium_mg: Optional[float] = Field(None, description="Potassium (mg)")
    
    source_id: str = Field("health_nutrition_usda", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SupplementFactRecord(BaseModel):
    """Supplement facts record."""
    record_id: UUID = Field(default_factory=uuid4)
    supplement_name: str = Field(..., description="Supplement name")
    brand: Optional[str] = Field(None, description="Brand name")
    
    # Serving
    serving_size: float = Field(..., description="Serving size")
    serving_unit: str = Field(..., description="Serving unit")
    servings_per_container: int = Field(..., description="Servings per container")
    
    # Active ingredients
    ingredients: List[dict] = Field(default_factory=list, description="Active ingredients")
    
    # Warnings
    warnings: Optional[str] = Field(None, description="Warning labels")
    interactions: Optional[str] = Field(None, description="Known interactions")
    
    source_id: str = Field("health_supplements_db", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealthEvidenceDocument(BaseModel):
    """Health evidence literature document."""
    document_id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Article title")
    abstract: str = Field(..., description="Article abstract")
    authors: List[str] = Field(default_factory=list, description="Authors")
    journal: str = Field(..., description="Journal name")
    pub_date: datetime = Field(..., description="Publication date")
    pmid: Optional[str] = Field(None, description="PubMed ID")
    doi: Optional[str] = Field(None, description="DOI")
    url: str = Field(..., description="Article URL")
    
    # Content classification
    topics: List[str] = Field(default_factory=list, description="Health topics")
    evidence_level: str = Field(..., description="Evidence level (systematic review, RCT, etc.)")
    
    # Summary
    key_findings: Optional[str] = Field(None, description="Key findings summary")
    
    source_id: str = Field("health_literature_pubmed", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WellnessGuidanceDocument(BaseModel):
    """Evidence-based wellness guidance document."""
    document_id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Guidance title")
    content: str = Field(..., description="Guidance content")
    category: str = Field(..., description="Guidance category")
    topic: str = Field(..., description="Specific topic")
    
    # Source information
    evidence_sources: List[str] = Field(default_factory=list, description="Evidence sources")
    last_reviewed: datetime = Field(..., description="Last review date")
    next_review: Optional[datetime] = Field(None, description="Next review date")
    
    # Applicability
    target_audience: str = Field(..., description="Target audience")
    applicability_notes: Optional[str] = Field(None, description="Notes on applicability")
    
    source_id: str = Field("health_wellness_guidance", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
