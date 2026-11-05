import pandas as pd
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'little-joys-data')
creators = pd.read_csv(os.path.join(DATA_DIR, 'creators.csv'), encoding='latin1')

# All 20 creator handles from the CSV
all_handles = creators['handle'].tolist()

creators_dict = creators.set_index('handle').to_dict('index')

def score_theme_alignment(themes):
    """Score 0-8: theme alignment with Little Joys (infant health, pediatric nutrition, parenting, feeding)"""
    if not isinstance(themes, str):
        return 0
    themes_lower = themes.lower()
    score = 0
    if any(kw in themes_lower for kw in ['nutrition', 'pediatric', 'infant health', 'medical product safety', 'baby health']):
        score += 8
    elif any(kw in themes_lower for kw in ['parenting', 'child development', 'myth-busting']):
        score += 5
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
            return 5
        return 4
    elif any(kw in voice_lower for kw in ['conversational', 'warm', 'enthusiastic', 'reflective']):
        return 3
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
        return 4
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
        return 8
    elif 'english' in combined and not any(kw in combined for kw in ['hindi', 'hunglish']):
        return 5
    elif any(kw in combined for kw in ['hindi', 'hindi with']):
        return 6
    else:
        return 3

def score_catchphrase_compatibility(catchphrases):
    """Score 0-4: catchphrase compatibility"""
    if not isinstance(catchphrases, str):
        return 0
    cp_lower = catchphrases.lower()
    if any(kw in cp_lower for kw in ['aap', 'beta', 'child address', 'kid']):
        return 4
    elif any(kw in cp_lower for kw in ['save this', 'product', 'promotion']):
        return 3
    else:
        return 1

def compute_risk_deduct(handle):
    """Compute risk deductions consistently.
    Returns total deduction (0-15).
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
            risk_deduct += 5
    
    # Check authenticity concerns in audience_read JSON
    # Only deduct if value indicates real concerns (not "None observed"/negation phrases)
    if audience_read and isinstance(audience_read, str):
        negation_phrases = ['none', 'none observed', 'not observed', 'none noted']
        try:
            audience_data = json.loads(audience_read)
            if isinstance(audience_data, dict):
                concerns_val = audience_data.get('authenticity_concerns', '')
                if concerns_val and isinstance(concerns_val, str) and concerns_val.lower().strip() not in negation_phrases:
                    risk_deduct += 5
        except json.JSONDecodeError:
            if audience_read and isinstance(audience_read, str):
                if not any(p in audience_read.lower() for p in negation_phrases):
                    risk_deduct += 5
    
    # Check what_would_foreign for scripted sales / medical without local context
    if wfn and isinstance(wfn, str):
        if any(kw in wfn.lower() for kw in ['scripted sales', 'lacks context', 'medical without local']):
            risk_deduct += 5
    
    risk_deduct = min(risk_deduct, 15)
    return risk_deduct

# Score ALL creators
print("=" * 60)
print("ALL CREATORS SCORING ANALYSIS")
print("=" * 60)

results = []

for handle in all_handles:
    creator = creators_dict[handle]
    name = creator.get('name', 'N/A')
    followers = creator.get('followers', 0)
    verified = creator.get('verified', 'N/A')
    
    # Dimension 1: Brand-Fit Score (0-25)
    theme_score = score_theme_alignment(creator.get('themes', ''))
    voice_score = score_voice_match(creator.get('voice', ''))
    format_score = score_format_compatibility(creator.get('format_habits', ''))
    native_score = score_native_alignment(creator.get('what_feels_native', ''))
    brand_fit = theme_score + voice_score + format_score + native_score
    
    # Dimension 2: Engagement (qualitative)
    engagement = 'large' if followers > 200000 else 'medium' if followers > 50000 else 'small'
    
    # Dimension 3: Audience Targeting (note limitation)
    
    # Dimension 4: Language & Cultural Fit (0-15)
    language_score = score_language_fit(handle)
    catchphrase_score = score_catchphrase_compatibility(creator.get('catchphrases', ''))
    lang_total = language_score + catchphrase_score
    
    # Dimension 5: Risk Subtractors
    risk_deduct = compute_risk_deduct(handle)
    
    # Total score
    total = brand_fit + lang_total + 20 - risk_deduct
    total = min(total, 85)
    total = max(total, 0)
    
    # Tier classification (adjusted for actual range)
    if total >= 50:
        tier = "RECOMMENDED - strong fit, proceed with selection"
    elif total >= 40:
        tier = "STRONG CANDIDATE - good fit with minor adjustments, reliable contingency"
    elif total >= 30:
        tier = "MODERATE FIT - works only with messaging adjustments, contingency only"
    else:
        tier = "RECONSIDER - significant misalignment, not recommended"
    
    results.append({
        'handle': handle,
        'name': name,
        'followers': followers,
        'theme_score': theme_score,
        'voice_score': voice_score,
        'format_score': format_score,
        'native_score': native_score,
        'brand_fit': brand_fit,
        'language_score': language_score,
        'catchphrase_score': catchphrase_score,
        'lang_total': lang_total,
        'risk_deduct': risk_deduct,
        'total': total,
        'tier': tier,
        'engagement': engagement
    })
    
    # Handle Unicode names safely
    name_safe = str(name).encode('ascii', errors='replace').decode('ascii') if name else handle
    print(f"\n{'='*60}")
    print(f"CREATOR: {handle} ({name_safe[:60]})")
    print(f"Followers: {followers} ({engagement})")
    print(f"Brand-Fit: {brand_fit}/25 (Theme: {theme_score}/8, Voice: {voice_score}/5, Format: {format_score}/5, Native: {native_score}/4)")
    print(f"Language/Culture: {lang_total}/15 (Lang: {language_score}/8, Catchphrase: {catchphrase_score}/4)")
    print(f"Risk Deduction: {risk_deduct}/15")
    print(f"TOTAL SCORE: {total}/85")
    print(f"  TIER: {tier}")

# Summary ranking
print("\n" + "=" * 60)
print("SUMMARY RANKING - ALL 20 CREATORS")
print("=" * 60)
print("Ranking by total score (higher is better):")

results_sorted = sorted(results, key=lambda x: -x['total'])
for i, r in enumerate(results_sorted):
    name_safe = str(r['name']).encode('ascii', errors='replace').decode('ascii') if r['name'] else r['handle']
    print(f"  {i+1}. {r['handle']} ({name_safe}): {r['total']}/85 - {r['tier']}")

# Also print by tier
print("\nBy Tier:")
for tier in ["RECOMMENDED", "STRONG CANDIDATE", "MODERATE FIT", "RECONSIDER"]:
    print(f"\n  {tier}:")
    for r in results_sorted:
        if r['tier'].startswith(tier):
            name_safe = str(r['name']).encode('ascii', errors='replace').decode('ascii') if r['name'] else r['handle']
            print(f"    {r['handle']} ({name_safe}): {r['total']}/85")
