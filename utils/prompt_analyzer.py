"""Prompt analysis utilities for enhanced evaluation"""

import re
from typing import List, Dict, Tuple

def split_into_lines(text: str) -> List[str]:
    """Split text into meaningful lines/sections"""
    # Remove empty lines and strip
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return lines

def extract_prompts_from_file(content: str) -> List[str]:
    """
    Extract multiple prompts from a file.
    Only splits when there's CLEAR evidence of multiple distinct prompts.
    
    Detects patterns like:
    - Clear numbered lists (1., 2., 3.) with "Prompt" keyword
    - Explicit separators (----, ====, etc.)
    
    Otherwise treats entire content as ONE prompt.
    """
    prompts = []
    
    # Look for explicit numbered prompts with "Prompt" keyword
    # Pattern: "1. Prompt:" or "Prompt 1:" or "1) Prompt:"
    explicit_prompt_pattern = r'(?:^|\n)(?:Prompt\s*\d+|[\d]+[\.\)]\s*Prompt)\s*:?\s*(.+?)(?=(?:\n(?:Prompt\s*\d+|[\d]+[\.\)]\s*Prompt))|$)'
    matches = re.findall(explicit_prompt_pattern, content, re.IGNORECASE | re.DOTALL)
    if matches and len(matches) > 1:
        prompts = [m.strip() for m in matches if len(m.strip()) > 10]
        return prompts
    
    # Look for explicit separators (at least 3 dashes or equals)
    separator_pattern = r'(?:^|\n)[-=]{3,}\s*$'
    if re.search(separator_pattern, content, re.MULTILINE):
        sections = re.split(separator_pattern, content, flags=re.MULTILINE)
        prompts = [s.strip() for s in sections if s.strip() and len(s.strip()) > 20]
        if len(prompts) > 1:
            return prompts
    
    # Default: treat entire content as ONE single prompt
    # This is the conservative approach - better to have one long prompt
    # than to incorrectly split a single prompt into multiple pieces
    return [content.strip()]

def analyze_line(line: str, line_number: int) -> Dict:
    """Analyze a single line of the prompt"""
    analysis = {
        'line_number': line_number,
        'text': line,
        'length': len(line.split()),
        'clarity_score': 0,
        'action_type': 'unknown',
        'issues': [],
        'suggestions': []
    }
    
    # Detect action type
    if any(word in line.lower() for word in ['write', 'create', 'generate', 'compose']):
        analysis['action_type'] = 'Content Generation'
    elif any(word in line.lower() for word in ['analyze', 'evaluate', 'assess', 'review']):
        analysis['action_type'] = 'Analysis'
    elif any(word in line.lower() for word in ['for', 'about', 'regarding', 'on']):
        analysis['action_type'] = 'Context/Topic'
    elif any(word in line.lower() for word in ['in', 'using', 'with', 'style']):
        analysis['action_type'] = 'Format/Style'
    
    # Calculate clarity score
    clarity = 50  # Base score
    
    # Boost for specifics
    if any(char.isupper() for char in line):  # Has proper nouns
        clarity += 10
    if any(char.isdigit() for char in line):  # Has numbers
        clarity += 10
    if len(line.split()) > 5:  # Detailed
        clarity += 15
    if any(word in line.lower() for word in ['specific', 'exactly', 'precisely']):
        clarity += 15
    
    # Penalties for vagueness
    vague_words = ['something', 'anything', 'some', 'any', 'general', 'basic', 'simple']
    if any(word in line.lower() for word in vague_words):
        clarity -= 20
        analysis['issues'].append(f"Contains vague word: '{[w for w in vague_words if w in line.lower()][0]}'")
        analysis['suggestions'].append("Replace vague terms with specific details")
    
    # Check for missing context
    if analysis['action_type'] == 'Content Generation' and len(line.split()) < 6:
        clarity -= 15
        analysis['issues'].append("Too brief - lacks context")
        analysis['suggestions'].append("Add more details (audience, tone, purpose)")
    
    analysis['clarity_score'] = max(0, min(100, clarity))
    
    return analysis

def detect_decision_points(prompt: str) -> List[Dict]:
    """Detect places where AI needs to make decisions"""
    decision_points = []
    
    lines = split_into_lines(prompt)
    
    for i, line in enumerate(lines, 1):
        points = []
        
        # Check for missing specifications
        if 'write' in line.lower() or 'create' in line.lower():
            # Content generation without specifics
            if not any(word in line.lower() for word in ['formal', 'casual', 'professional', 'friendly']):
                points.append({
                    'line': i,
                    'decision': 'Tone selection',
                    'issue': 'Tone not specified (formal/casual?)',
                    'risk': 'medium'
                })
            
            if not any(word in line.lower() for word in ['short', 'long', 'brief', 'detailed', 'words', 'sentences']):
                points.append({
                    'line': i,
                    'decision': 'Length/detail level',
                    'issue': 'Output length not defined',
                    'risk': 'low'
                })
        
        # Check for facts without sources
        if any(word in line.lower() for word in ['about', 'regarding', 'on the topic']):
            if 'product' in line.lower() and not any(word in prompt.lower() for word in ['named', 'called', 'specifically']):
                points.append({
                    'line': i,
                    'decision': 'Product details',
                    'issue': 'Product not named - AI may invent details',
                    'risk': 'high'
                })
        
        decision_points.extend(points)
    
    return decision_points

def calculate_hallucination_risk(prompt: str, decision_points: List[Dict]) -> Tuple[int, List[str]]:
    """Calculate overall hallucination risk score"""
    risk_score = 0
    reasons = []
    
    # Base risk from decision points
    high_risk_count = sum(1 for dp in decision_points if dp['risk'] == 'high')
    medium_risk_count = sum(1 for dp in decision_points if dp['risk'] == 'medium')
    low_risk_count = sum(1 for dp in decision_points if dp['risk'] == 'low')
    
    risk_score += high_risk_count * 25
    risk_score += medium_risk_count * 15
    risk_score += low_risk_count * 5
    
    # Check prompt length
    word_count = len(prompt.split())
    if word_count < 10:
        risk_score += 20
        reasons.append("Very brief prompt - lots of ambiguity")
    elif word_count < 20:
        risk_score += 10
        reasons.append("Brief prompt - some assumptions needed")
    
    # Check for vague language
    vague_indicators = ['something', 'anything', 'general', 'basic', 'simple', 'some', 'any']
    vague_count = sum(1 for word in vague_indicators if word in prompt.lower())
    if vague_count > 0:
        risk_score += vague_count * 10
        reasons.append(f"Contains {vague_count} vague term(s)")
    
    # Check for missing constraints
    constraint_words = ['must', 'should', 'include', 'format', 'length', 'style', 'tone']
    constraint_count = sum(1 for word in constraint_words if word in prompt.lower())
    if constraint_count == 0:
        risk_score += 15
        reasons.append("No explicit constraints → unpredictable output")
    
    # Add reasons from decision points
    for dp in decision_points:
        if dp['risk'] == 'high':
            reasons.append(f"Line {dp['line']}: {dp['issue']}")
    
    risk_score = min(100, risk_score)
    
    return risk_score, reasons

def get_risk_level(score: int) -> str:
    """Get risk level label"""
    if score <= 30:
        return "🟢 LOW"
    elif score <= 70:
        return "🟡 MEDIUM"
    else:
        return "🔴 HIGH"
