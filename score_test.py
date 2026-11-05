import pandas as pd
import json

creators = pd.read_csv('creators.csv', encoding='latin1')

# Sample creator data for manual scoring
# We'll score: drgarima_mehta, hello_ps8, parentingtips_surat, foodies_by_neha, storiesbyvihaa

selected_handles = ['drgarima_mehta', 'hello_ps8', 'parentingtips_surat', 'foodies_by_neha', 'storiesbyvihaa']

creators_dict = creators.set_index('handle').to_dict('index')

def score_theme_alignment(themes):
    """Score 0-8: theme alignment with Little Joys (infant health, pediatric nutrition, parenting, feeding)"""
    if not isinstance(themes, str):
        return 0
    themes_lower = themes.lower()
    score = 0
    # Direct nutrition/health themes
    if any(kw in themes_lower for kw in ['nutrition', 'pediatric', 'infant health', 'medical product safety', 'baby health']):
        score += 8
    # Parenting themes
    elif any(kw in themes_lower for kw in ['parenting', 'child development', 'myth-busting']):
        score += 5
    # General family/child themes
    elif any(kw in themes_lower for kw in ['family', 'motherhood', 'child']):
        score += 3
    else:
        score += 1
    return min(score, 8)

def score_voice_match(voice):
    """Score 0-5: voice match with Little Joys trust signal"""
    if not isinstance(voice, str):
        return 0
    voice_lower = voice.lower()
    if any(kw in voice_lower for kw in ['reassuring', 'clinical', 'calm', 'authoritative', 'professional']):
        if any(kw in voice_lower for kw in ['warm', 'accessible', 'approachable']):
            return 5  # reassuring + warm
        return 4  # clinical/professional
    elif any(kw in voice_lower for kw in ['conversational', 'warm', 'enthusiastic', 'reflective']):
        return 3  # parent-to-parent
    elif any(kw in voice_lower for kw in ['entertainment', 'sales-focused', 'promotional']):
        return 2
    else:
        return 1

def score_format_compatibility(format_habits):
    """Score 0-5: format compatibility with top ad formats"""
    if not isinstance(format_habits, str):
        return 0
    fmt_lower = format_habits.lower()
    if any(kw in fmt_lower for kw in ['voiceover_montage', 'split-screen', 'direct-to-camera', 'text overlays']):
        return 5
    elif any(kw in fmt_lower for kw in ['skit', 'comedic', 'story-based']):
        return 3
    else:
        return 1

def score_native_alignment(what_feels_native):
    """Score 0-4: alignment with Indian parenting context"""
    if not isinstance(what_feels_native, str):
        return 0
    wfn_lower = what_feels_native.lower()
    if any(kw in wfn_lower for kw in ['clinical', 'science', 'doctors', 'medical setting']):
        return 4  # clinical Indian setting
    elif any(kw in wfn_lower for kw in ['Indian', 'Indian parent', 'relatable domestic']):
        return 3
    elif any(kw in wfn_lower for kw in ['modern', 'urban', 'casual']):
        return 2
    else:
        return 1

def score_language_fit(handle):
    """Score 0-8: language fit - check voice and catchphrases"""
    creator = creators_dict[handle]
    voice = creator.get('voice', '')
    catchphrases = creator.get('catchphrases', '')
    combined = (voice + ' ' + catchphrases).lower()
    
    if 'hinglish' in combined or ('hindi' in combined and 'english' in combined):
        return 8  # Hinglish-capable
    elif 'english' in combined and not any(kw in combined for kw in ['hindi', 'hunglish']):
        return 5  # English-only
    elif any(kw in combined for kw in ['hindi', 'hindi with']):
        return 6  # Hindi-primary with English terms
    else:
        return 3

def score_catchphrase_compatibility(catchphrases):
    """Score 0-4: catchphrase compatibility"""
    if not isinstance(catchphrases, str):
        return 0
    cp_lower = catchphrases.lower()
    if any(kw in cp_lower for kw in ['aap', 'beta', 'child address', 'kid']):
        return 4  # child-addressing catchphrases
    elif any(kw in cp_lower for kw in ['save this', 'product', 'promotion']):
        return 3  # promotion-friendly
    else:
        return 1

def compute_risk_deduct(handle):
    """Compute risk deductions consistently for both individual and summary scoring.
    Returns total deduction (0-15).
    
    Data note: The 'authenticity_concerns' key appears in audience_read for ALL creators
    as a system-generated label. The value (not the key) indicates whether there are actual
    concerns. We only deduct if the value explicitly indicates real concerns (not "None observed"
    or similar negation phrases).
    """
    creator = creators_dict[handle]
    risk_deduct = 0
    persona_desc = creator.get('persona_description', '')
    audience_read = creator.get('audience_read', '')
    wfn = creator.get('what_would_foreign', '')
    
    # Check for safety concerns in persona_description (only if actual concerns mentioned)
    if persona_desc and isinstance(persona_desc, str):
        concern_keywords = ['safety concern', 'controversial', 'unsafe', 'harm', 'danger']
        if any(kw in persona_desc.lower() for kw in concern_keywords):
            # Only deduct 5 if actual safety concerns are present (not 10, to avoid double-counting)
            risk_deduct += 5
    
    # Check authenticity concerns in audience_read JSON
    # Note: 'authenticity_concerns' key appears for ALL creators as system label.
    # Only deduct if value indicates real concerns (not "None observed"/negation phrases).
    if audience_read and isinstance(audience_read, str):
        try:
            audience_data = json.loads(audience_read)
            if isinstance(audience_data, dict):
                concerns_val = audience_data.get('authenticity_concerns', '')
                # Only deduct if value is a non-empty string that isn't a negation phrase
                negation_phrases = ['none', 'none observed', 'not observed', 'none noted']
                if concerns_val and isinstance(concerns_val, str) and concerns_val.lower().strip() not in negation_phrases:
                    risk_deduct += 5
        except json.JSONDecodeError:
            # Fallback: check raw text but only if it's not a negation phrase
            if audience_read and isinstance(audience_read, str):
                negation_phrases = ['none', 'none observed', 'not observed', 'none noted']
                if not any(p in audience_read.lower() for p in negation_phrases):
                    risk_deduct += 5
    
    # Check what_would_foreign for scripted sales / medical without local context (legitimate risk)
    if wfn and isinstance(wfn, str):
        if any(kw in wfn.lower() for kw in ['scripted sales', 'lacks context', 'medical without local']):
            risk_deduct += 5
    
    # Cap at 15
    risk_deduct = min(risk_deduct, 15)
    return risk_deduct

def score_language_fit_v2(handle):
    """Deprecated: use score_language_fit instead. Kept for reference."""
    ...

# Score each creator
print("=" * 60)
print("CREATOR SCORING ANALYSIS")
print("=" * 60)

for handle in selected_handles:
    creator = creators_dict[handle]
    print(f"\n{'='*60}")
    print(f"CREATOR: {handle} ({creator.get('name', 'N/A')})")
    print(f"Followers: {creator.get('followers', 'N/A')}")
    print(f"Verified: {creator.get('verified', 'N/A')}")
    
    # Dimension 1: Brand-Fit Score (0-25)
    theme_score = score_theme_alignment(creator.get('themes', ''))
    voice_score = score_voice_match(creator.get('voice', ''))
    format_score = score_format_compatibility(creator.get('format_habits', ''))
    native_score = score_native_alignment(creator.get('what_feels_native', ''))
    
    brand_fit = theme_score + voice_score + format_score + native_score
    print(f"\n--- Brand-Fit Sub-Scores ---")
    print(f"  Theme alignment: {theme_score}/8")
    print(f"  Voice match: {voice_score}/5")
    print(f"  Format compatibility: {format_score}/5")
    print(f"  Native alignment: {native_score}/4")
    print(f"  SUB-TOTAL Brand-Fit: {brand_fit}/25")
    
    # Dimension 2: Engagement Efficiency (qualitative)
    print(f"\n--- Engagement Assessment ---")
    print(f"  Followers: {creator.get('followers', 'N/A')} (qualitative: {'large' if creator.get('followers', 0) > 200000 else 'medium' if creator.get('followers', 0) > 50000 else 'small'})")
    
    # Dimension 3: Audience Targeting (limited data - only 3 creators have audience data)
    print(f"\n--- Audience Targeting ---")
    
    # Dimension 4: Language & Cultural Fit (0-15)
    language_score = score_language_fit(handle)
    catchphrase_score = score_catchphrase_compatibility(creator.get('catchphrases', ''))
    lang_total = language_score + catchphrase_score
    print(f"\n--- Language & Cultural Fit ---")
    print(f"  Language fit: {language_score}/8")
    print(f"  Catchphrase compatibility: {catchphrase_score}/4")
    print(f"  SUB-TOTAL Language/Culture: {lang_total}/15")
    
    # Dimension 5: Risk Subtractors (0-15 deduction) - USING SHARED FUNCTION
    risk_deduct = compute_risk_deduct(handle)
    print(f"\n--- Risk Subtractors ---")
    print(f"  Deduction: {risk_deduct}/15")
    
    # Total score
    total = brand_fit + lang_total + 20 - risk_deduct  # 20 is placeholder for engagement/audience
    # Cap at 85
    total = min(total, 85)
    total = max(total, 0)
    
    print(f"\n{'='*60}")
    print(f"TOTAL SCORE: {total}/85")
    # Revised tier thresholds adjusted for actual score range (30-60 with 4 measured dims + 20 placeholder):
    # 50-60: Recommended - strong fit across key dimensions, proceed with selection
    # 40-49: Strong candidate - good fit with minor messaging adjustments, reliable contingency
    # 30-39: Moderate fit - works only with messaging adjustments, use as contingency only
    # below 30: Reconsider - significant misalignment, not recommended
    if total >= 50:
        tier = "RECOMMENDED - strong fit across key dimensions, proceed with selection"
    elif total >= 40:
        tier = "STRONG CANDIDATE - good fit with minor messaging adjustments, reliable contingency"
    elif total >= 30:
        tier = "MODERATE FIT - works only with messaging adjustments, use as contingency only"
    else:
        tier = "RECONSIDER - significant misalignment, not recommended"
    print(f"  TIER: {tier}")
    print(f"  Key strengths: ", end="")
    strengths = []
    if theme_score >= 6: strengths.append("strong theme fit")
    if voice_score >= 4: strengths.append("good voice match")
    if format_score >= 4: strengths.append("format compatible")
    if native_score >= 3: strengths.append("cultural alignment")
    if language_score >= 6: strengths.append("language fit")
    if catchphrase_score >= 3: strengths.append("catchphrase compatibility")
    print(", ".join(strengths) if strengths else "none identified clearly")
    print(f"  Key risks: ", end="")
    risks = []
    if risk_deduct >= 5: risks.append(f"risk deduct={risk_deduct}")
    if theme_score <= 2: risks.append("weak theme fit")
    print(", ".join(risks) if risks else "none identified")
    print()

# Summary comparison - NOW USES SAME compute_risk_dect FUNCTION
print("=" * 60)
print("SUMMARY RANKING")
print("=" * 60)
print("Ranking by total score (higher is better):")
scores = []
for handle in selected_handles:
    creator = creators_dict[handle]
    theme_score = score_theme_alignment(creator.get('themes', ''))
    voice_score = score_voice_match(creator.get('voice', ''))
    format_score = score_format_compatibility(creator.get('format_habits', ''))
    native_score = score_native_alignment(creator.get('what_feels_native', ''))
    language_score = score_language_fit(handle)
    catchphrase_score = score_catchphrase_compatibility(creator.get('catchphrases', ''))
    brand_fit = theme_score + voice_score + format_score + native_score
    lang_total = language_score + catchphrase_score
    risk_deduct = compute_risk_deduct(handle)  # SAME function as individual display
    total = min(brand_fit + lang_total + 20 - risk_deduct, 85)
    scores.append((handle, total))
    print(f"  {handle}: {total:.0f}/85")

scores.sort(key=lambda x: -x[1])
for i, (handle, score) in enumerate(scores):
    print(f"  {i+1}. {handle}: {score:.0f}")