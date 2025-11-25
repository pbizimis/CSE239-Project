from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


class BrandIdentity(BaseModel):
    """Core facts that identify the brand/store entity."""

    store_name: Optional[str] = Field(
        None,
        description="Official brand or store name as shown in header, footer, or logo alt text.",
    )
    brand_aliases: List[str] = Field(
        default_factory=list,
        description="Any alternative names, abbreviations, or short forms used on the site.",
    )
    parent_company: Optional[str] = Field(
        None, description="Parent company if stated (leave null if not stated)."
    )
    founding_year: Optional[int] = Field(
        None, description="Four-digit year if explicitly mentioned (do NOT guess)."
    )
    hq_country: Optional[str] = Field(
        None, description="Country of headquarters if explicitly mentioned."
    )
    locales: List[str] = Field(
        default_factory=list,
        description="IETF language tags detected (e.g., 'en-US', 'de-DE').",
    )


class Positioning(BaseModel):
    """High-level category and niche the brand claims."""

    primary_category: Optional[str] = Field(
        None,
        description="The single best high-level category (e.g., 'athleisure', 'skincare', 'SaaS').",
    )
    subcategories: List[str] = Field(
        default_factory=list,
        description="Secondary categories or collections named in nav/hero.",
    )
    niche: Optional[str] = Field(
        None,
        description="Niche or specialization claimed (e.g., 'clean beauty', 'performance merino').",
    )
    competitors: List[str] = Field(
        default_factory=list,
        description="Competitors explicitly named or implied via comparison blocks.",
    )


class AudienceSignals(BaseModel):
    """Who the store speaks to and where."""

    b2b_b2c: Optional[Literal["B2B", "B2C", "Both"]] = Field(
        None, description="Target market based on site copy (B2B, B2C, or Both)."
    )
    personas: List[str] = Field(
        default_factory=list,
        description="Short descriptors of target personas if the site hints them.",
    )
    regions_served: List[str] = Field(
        default_factory=list,
        description="Countries/regions explicitly served, if mentioned.",
    )
    use_cases: List[str] = Field(
        default_factory=list,
        description="Use-cases or situations mentioned in copy (e.g., 'daily commute').",
    )


class Messaging(BaseModel):
    """Promise, benefits, and brand voice signals from visible copy."""

    headline: Optional[str] = Field(
        None, description="Main hero headline or most prominent H1 on the homepage."
    )
    subheadline: Optional[str] = Field(
        None, description="Supporting line under the headline if present."
    )
    key_benefits: List[str] = Field(
        default_factory=list,
        description="3–5 benefit bullets or short phrases quoted from the site.",
    )
    differentiators: List[str] = Field(
        default_factory=list,
        description="Unique value claims vs. market (e.g., 'lifetime warranty', 'patented foam').",
    )
    pain_points: List[str] = Field(
        default_factory=list, description="Customer pains the brand says it solves."
    )
    brand_voice_traits: List[str] = Field(
        default_factory=list,
        description="Tone-of-voice adjectives inferred from copy (e.g., 'playful', 'clinical').",
    )


class Policies(BaseModel):
    """Purchase, shipping, returns, and warranty summaries visible or linked from the homepage."""

    shipping_summary: Optional[str] = Field(
        None, description="Short paraphrase of shipping policy or headline promise."
    )
    free_shipping_threshold: Optional[str] = Field(
        None, description="Threshold text if shown (e.g., 'Free shipping over $50')."
    )
    delivery_speeds: List[str] = Field(
        default_factory=list, description="Explicit delivery timeframes quoted."
    )
    returns_summary: Optional[str] = Field(
        None, description="Short paraphrase of returns window/conditions."
    )
    warranty_summary: Optional[str] = Field(
        None, description="Warranty length/terms if stated."
    )
    sustainability_statements: List[str] = Field(
        default_factory=list,
        description="Any environmental/ethical claims or badges (quote or paraphrase).",
    )


class ProofLayer(BaseModel):
    """Trust markers shown on the homepage."""

    payment_badges: List[str] = Field(
        default_factory=list,
        description="Logos like Visa, PayPal, Apple Pay if rendered.",
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="Certifications or seals (e.g., USDA Organic, Leaping Bunny).",
    )
    sitewide_rating: Optional[str] = Field(
        None,
        description="Any overall rating displayed (format as shown, e.g., '4.8/5 from 12,000+ reviews').",
    )
    testimonial_quotes: List[str] = Field(
        default_factory=list,
        description="Short quotes from customers/press shown on homepage.",
    )
    press_logos: List[str] = Field(
        default_factory=list,
        description="Press outlets shown as logos (e.g., 'Forbes', 'Vogue').",
    )
    influencer_mentions: List[str] = Field(
        default_factory=list, description="Ambassadors/creators named on homepage."
    )


class SocialPresence(BaseModel):
    """Where the brand is active on social, as linked from the homepage/footer."""

    instagram: Optional[HttpUrl] = Field(
        None, description="Instagram profile URL if linked."
    )
    tiktok: Optional[HttpUrl] = Field(None, description="TikTok profile URL if linked.")
    youtube: Optional[HttpUrl] = Field(
        None, description="YouTube channel URL if linked."
    )
    pinterest: Optional[HttpUrl] = Field(
        None, description="Pinterest profile URL if linked."
    )
    facebook: Optional[HttpUrl] = Field(
        None, description="Facebook page URL if linked."
    )
    x_twitter: Optional[HttpUrl] = Field(
        None, description="X/Twitter profile URL if linked."
    )
    hashtags: List[str] = Field(
        default_factory=list, description="Campaign or community hashtags if shown."
    )


class StoreMetaData(BaseModel):
    """Minimum homepage metadata required to drive marketing content & routing."""

    brand: BrandIdentity = Field(..., description="Identity facts for the brand/store.")
    positioning: Positioning = Field(
        ..., description="Category, niche, and competitor context."
    )
    audience: AudienceSignals = Field(
        ..., description="Who the brand targets and where it sells."
    )
    messaging: Messaging = Field(
        ..., description="Homepage promise, benefits, and tone cues."
    )
    policies: Policies = Field(
        ..., description="Shipping/returns/warranty/sustainability summaries."
    )
    proof: ProofLayer = Field(
        ..., description="Badges, certifications, reviews, press, influencers."
    )
    social: SocialPresence = Field(
        ..., description="Linked social profiles and hashtags."
    )
