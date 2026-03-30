"""
Enhanced AI Evaluation System - Unified Interface
Combines prompt and decision evaluation with advanced analysis features
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from utils.ollama_client import OllamaClient
from utils.file_handler import save_uploaded_file, extract_file_content, get_file_metadata
from utils.token_tracker import TokenTracker
from utils.prompt_analyzer import (
    extract_prompts_from_file,
    split_into_lines,
    detect_decision_points,
    calculate_hallucination_risk,
    get_risk_level
)
from config import EVALUATORS, OLLAMA_DEFAULT_MODEL
import re

# Page config
st.set_page_config(page_title="AI Evaluator", page_icon="🎯", layout="wide")

# Initialize session state
if 'token_tracker' not in st.session_state:
    st.session_state.token_tracker = TokenTracker()

# Initialize client
client = OllamaClient()

# Title
st.title("🎯 AI Prompt & Decision Evaluator")
st.caption("Advanced evaluation with line-by-line analysis and hallucination detection")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model selection
    st.subheader("🤖 Model Selection")
    
    # Try to get available models from Ollama
    available_models = client.list_models()
    if not available_models:
        # Fallback to default model if Ollama is not reachable
        available_models = [OLLAMA_DEFAULT_MODEL]
    
    selected_model = st.selectbox(
        "Select Model",
        available_models,
        index=0 if available_models else 0,
        help="Choose the model for evaluation"
    )
    
    # Token tracker display
    st.header("🔢 Token Usage")
    tracker = st.session_state.token_tracker
    summary = tracker.get_summary()
    
    if summary['total_requests'] > 0:
        st.metric("Total Tokens", f"{summary['total_tokens']:,}")
        st.metric("Total Requests", summary['total_requests'])
        st.metric("Avg per Request", f"{summary['avg_tokens_per_request']:,.0f}")
        
        if st.button("Reset Tracker"):
            tracker.reset()
            st.rerun()
    else:
        st.info("No evaluations yet")
    
    st.divider()
    st.caption("💡 Models optimized for evaluation tasks")

# Main content
tab1, tab2 = st.tabs(["📝 Evaluate", "📊 Batch Process"])

with tab1:
    # Mode selection
    eval_mode = st.radio(
        "What to evaluate?",
        ["✍️ Text Prompt", "📄 Document/File"],
        horizontal=True
    )
    

    
    st.divider()
    
    # Input section
    prompt_text = None
    uploaded_file = None
    file_content = None
    
    if eval_mode == "✍️ Text Prompt":
        prompt_text = st.text_area(
            "Enter your prompt or decision",
            placeholder="Example: Write a marketing email for our new AI product...",
            height=150
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload document (.txt, .docx, .pdf)",
            type=["txt", "docx", "pdf"]
        )
        
        if uploaded_file:
            # Save and extract
            saved_path = save_uploaded_file(uploaded_file)
            if saved_path and not saved_path.startswith("Error"):
                file_content = extract_file_content(saved_path)
                
                # Show metadata
                metadata = get_file_metadata(saved_path)
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📄 **{metadata['name']}**")
                with col2:
                    st.info(f"📏 {metadata['size_readable']}")
    
    # Evaluate button
    if st.button("🚀 Evaluate", type="primary", use_container_width=True):
        # Get content to evaluate
        content = prompt_text if eval_mode == "✍️ Text Prompt" else file_content
        
        if not content or (isinstance(content, str) and content.startswith("Error")):
            st.error("Please provide valid input to evaluate")
        else:
            # Detect multiple prompts
            prompts = extract_prompts_from_file(content)
            
            st.success(f"✅ Detected {len(prompts)} prompt(s)")
            
            # Process each prompt
            for idx, single_prompt in enumerate(prompts, 1):
                if len(prompts) > 1:
                    st.subheader(f"Prompt #{idx}")
                
                # Show prompt preview
                with st.expander(f"📝 Prompt Text ({len(single_prompt.split())} words)"):
                    st.text(single_prompt[:500] + ("..." if len(single_prompt) > 500 else ""))
                
                # Line-by-line analysis
                lines = split_into_lines(single_prompt)
                line_analyses = [analyze_line(line, i) for i, line in enumerate(lines, 1)]
                
                # Decision points
                decision_points = detect_decision_points(single_prompt)
                
                # Hallucination risk
                risk_score, risk_reasons = calculate_hallucination_risk(single_prompt, decision_points)
                risk_level = get_risk_level(risk_score)
                
                # Perform analysis with BOTH evaluators
                with st.spinner(f"Analyzing with {selected_model}..."):
                    combined_output = ""
                    total_prompt_tokens = 0
                    total_completion_tokens = 0
                    
                    # Run BOTH evaluators
                    for eval_key, evaluator in EVALUATORS.items():
                        # Build evaluation request
                        criteria_text = "\n".join([
                            f"- {c['name']} ({c['weight']}%): {c['description']}"
                            for c in evaluator['criteria']
                        ])
                        
                        eval_type_label = "Prompt Quality" if eval_key == "prompt" else "Decision Analysis"
                        
                        eval_request = f"""Evaluate this {eval_type_label.lower()} using these criteria:

{criteria_text}

Text to evaluate:
{single_prompt}

Provide:
1. Score for each criterion (0-100)
2. Overall weighted score
3. Brief analysis (2-3 sentences)
4. Top 2 improvement suggestions

Format as:
SCORES:
- Criterion1: XX
- Criterion2: XX
...
OVERALL: XX
ANALYSIS: ...
SUGGESTIONS:
1. ...
2. ...
"""
                        
                        # Get response with tokens
                        result = client.generate_with_tokens(
                            prompt=eval_request,
                            model=selected_model,
                            temperature=0.5
                        )
                        
                        eval_output = result.get('response', '')
                        prompt_tokens = result.get('prompt_tokens', 0)
                        completion_tokens = result.get('completion_tokens', 0)
                        
                        total_prompt_tokens += prompt_tokens
                        total_completion_tokens += completion_tokens
                        
                        # Append to combined output with header
                        combined_output += f"\n\n=== {eval_type_label} ===\n{eval_output}"
                        
                        # Track tokens for each evaluation
                        tracker.add_usage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            model=selected_model,
                            request_type="text"
                        )
                
                # Display results
                st.divider()
                st.markdown(f"### 🤖 Model: {selected_model}")
                    
                # Token breakdown
                st.subheader("🔢 Token Breakdown")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Your Input", f"{total_prompt_tokens:,} tokens")
                with col2:
                    st.metric("AI Analysis", f"{total_completion_tokens:,} tokens")
                with col3:
                    st.metric("Total Used", f"{total_prompt_tokens + total_completion_tokens:,} tokens", 
                             delta=f"+{total_prompt_tokens + total_completion_tokens:,}")
                
                # Analysis Results
                st.subheader("📊 Evaluation Results")
                # Parse scores
                try:
                    scores_section = re.search(r'SCORES?:(.*?)(?:OVERALL|$)', combined_output, re.DOTALL)
                    overall_match = re.search(r'OVERALL:\s*(\d+)', combined_output)
                    
                    if scores_section:
                        scores_text = scores_section.group(1)
                        score_lines = [line.strip() for line in scores_text.split('\n') if ':' in line]
                        
                        for score_line in score_lines:
                            if ':' in score_line:
                                name, score = score_line.split(':', 1)
                                name = name.strip().replace('-', '').strip()
                                score_match = re.search(r'\d+', score)
                                if score_match:
                                    score_num = int(score_match.group())
                                    
                                    # Progress bar
                                    color = "🟢" if score_num >= 80 else "🟡" if score_num >= 60 else "🔴"
                                    st.write(f"{color} **{name}**: {score_num}/100")
                                    st.progress(score_num / 100)
                    
                    if overall_match:
                        overall_score = int(overall_match.group(1))
                        st.metric("📈 Overall Score", f"{overall_score}/100")
                
                except Exception as e:
                    st.write(combined_output)
                
                # Line-by-line breakdown
                with st.expander("🔍 Line-by-Line Analysis"):
                    for line_analysis in line_analyses:
                        clarity_color = "🟢" if line_analysis['clarity_score'] >= 70 else "🟡" if line_analysis['clarity_score'] >= 50 else "🔴"
                        
                        st.write(f"**Line {line_analysis['line_number']}:** `{line_analysis['text'][:80]}...`")
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.write(f"{clarity_color} Clarity: {line_analysis['clarity_score']}/100")
                        with col2:
                            st.write(f"Action: {line_analysis['action_type']}")
                        
                        if line_analysis['issues']:
                            st.warning(f"⚠️ {', '.join(line_analysis['issues'])}")
                        if line_analysis['suggestions']:
                            st.info(f"💡 {', '.join(line_analysis['suggestions'])}")
                        st.divider()
                
                # Decision points
                if decision_points:
                    with st.expander(f"🎯 Decision Points ({len(decision_points)} found)"):
                        for dp in decision_points:
                            risk_icon = "🔴" if dp['risk'] == 'high' else "🟡" if dp['risk'] == 'medium' else "🟢"
                            st.write(f"{risk_icon} **Line {dp['line']}**: {dp['decision']}")
                            st.write(f"  ⚠️ {dp['issue']}")
                
                # Hallucination risk
                st.subheader("🚨 Hallucination Risk Assessment")
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric("Risk Score", f"{risk_score}/100")
                    st.write(f"**{risk_level}**")
                with col2:
                    st.write("**Why:**")
                    for reason in risk_reasons:
                        st.write(f"• {reason}")
                
                if len(prompts) > 1 and idx < len(prompts):
                    st.divider()
                    st.divider()


with tab2:
    st.subheader("📊 Batch Processing")
    st.info("Upload a CSV file with a 'prompt' column for batch evaluation")
    
    batch_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if batch_file and st.button("Process Batch"):
        st.success("Batch processing feature coming soon!")

# Footer
st.divider()
st.caption("🎯 Enhanced AI Evaluator | Line-by-line analysis | Hallucination detection | Token tracking")
