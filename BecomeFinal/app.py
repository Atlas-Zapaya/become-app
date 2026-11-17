import streamlit as st
import pandas as pd
import json
import time
import urllib.parse
from datetime import datetime

# Safe optional imports so the app runs cleanly even if a dependency is missing
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None

# ==============================================================================
# 1. PAGE CONFIG & ENTERPRISE DESIGN SYSTEM (GLASSMORPHISM UI)
# ==============================================================================
st.set_page_config(
    page_title="BECOME | Career & Workforce Intelligence OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
        color: #f3f4f6;
    }
    .hero-card {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 18px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
        transition: transform 0.25s ease, border-color 0.25s ease;
    }
    .hero-card:hover {
        transform: translateY(-4px);
        border-color: #818cf8;
    }
    .metric-badge {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid rgba(99, 102, 241, 0.45);
        letter-spacing: 0.05em;
    }
    .easy-apply-banner {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        padding: 20px 28px;
        border-radius: 14px;
        color: white;
        font-weight: 600;
        margin-bottom: 24px;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. BACKEND & CLIENT INITIALIZATION (OPENAI + SUPABASE)
# ==============================================================================
@st.cache_resource
def init_backend():
    try:
        openai_key = st.secrets.get("OPENAI_API_KEY", "")
        supa_url = st.secrets.get("SUPABASE_URL", "")
        supa_key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        openai_key, supa_url, supa_key = "", "", ""

    ai_client = OpenAI(api_key=openai_key) if (OpenAI and openai_key) else None
    supa_client = create_client(supa_url, supa_key) if (create_client and supa_url and supa_key) else None
    return ai_client, supa_client

ai_client, supabase = init_backend()

def _smart_fallback_response(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    """Provides realistic, domain-aware structured data when API key is offline so every button works."""
    if json_mode:
        if "questions" in user_prompt.lower() and "mock interview" in user_prompt.lower():
            return json.dumps({
                "questions": [
                    {
                        "q_num": 1,
                        "question": "Walk me through a high-stakes problem you solved from root-cause diagnosis to final execution.",
                        "what_they_look_for": "Structured problem-solving, ownership, and measurable impact.",
                        "delivery_tip": "Use the STAR framework and quantify your final outcome within 90 seconds."
                    },
                    {
                        "q_num": 2,
                        "question": "How do you adapt your workflow when critical requirements or priorities shift unexpectedly?",
                        "what_they_look_for": "Agility, calm under pressure, and stakeholder alignment.",
                        "delivery_tip": "Highlight proactive communication and trade-off analysis."
                    },
                    {
                        "q_num": 3,
                        "question": "Describe a time you had to master a completely unfamiliar tool, protocol, or domain quickly.",
                        "what_they_look_for": "Learning velocity and self-directed execution.",
                        "delivery_tip": "Detail your exact learning system and how quickly you delivered value."
                    },
                    {
                        "q_num": 4,
                        "question": "Tell me about a disagreement with a teammate or manager. How did you resolve it?",
                        "what_they_look_for": "Empathy, objectivity, and collaborative maturity.",
                        "delivery_tip": "Focus on shared goals and data rather than personal friction."
                    },
                    {
                        "q_num": 5,
                        "question": "What emerging trends or AI/automation tools are reshaping this profession over the next 2 years?",
                        "what_they_look_for": "Forward-thinking industry awareness and strategic foresight.",
                        "delivery_tip": "Connect industry trends directly to how you improve team productivity."
                    }
                ]
            })
        return json.dumps({
            "optimized_cv": (
                "# ATS-OPTIMIZED CURRICULUM VITAE\n\n"
                "## Executive Summary\n"
                "Results-driven, adaptable professional with proven execution across cross-functional initiatives, "
                "process optimization, and strategic problem-solving.\n\n"
                "## Core Competencies\n"
                "- **Strategic Execution:** End-to-end project delivery, KPI tracking, stakeholder management\n"
                "- **Domain Excellence:** Rapid onboarding, quality assurance, modern digital & AI tooling\n"
                "- **Collaboration:** Cross-team leadership, clear documentation, agile iteration\n\n"
                "## Highlighted Impact\n"
                "- Streamlined core operational workflows, reducing turnaround time by **32%**\n"
                "- Led cross-functional deliverables from concept to production with **100% on-time completion**"
            ),
            "motivational_letter": (
                "Dear Hiring Team,\n\n"
                "I am excited to submit my application for this position. Having closely followed your organization's "
                "commitment to excellence and innovation, I am eager to contribute my hands-on problem-solving background "
                "and high-ownership mindset to your team.\n\n"
                "Throughout my career, I have focused on turning complex challenges into clear, measurable outcomes—"
                "bridging strategic planning with rapid, reliable execution. I welcome the opportunity to discuss how "
                "my background and the attached proof-of-work mini-projects can immediately support your team's goals.\n\n"
                "Warm regards,\nCandidate"
            ),
            "interview_questions": [
                "**Q1:** What motivated you to apply to our organization specifically? *(Tip: Tie their recent mission/product to your core strengths.)*",
                "**Q2:** Describe a project where you exceeded expectations under tight constraints. *(Tip: Quantify the exact business or operational impact.)*",
                "**Q3:** How do you ensure quality and accuracy when handling multiple deliverables? *(Tip: Share your personal checklist/QA system.)*",
                "**Q4:** How would you approach your first 30 days in this role? *(Tip: Emphasize listening, rapid learning, and shipping an early win.)*",
                "**Q5:** Tell us about a complex concept you had to explain to a non-specialist. *(Tip: Demonstrate empathy and clarity.)*"
            ],
            "mini_projects": [
                {
                    "title": "30-Day Opportunity & Workflow Diagnostic",
                    "objective": "Demonstrate deep domain understanding before your first interview.",
                    "deliverable": "A crisp 1-page executive brief outlining 3 high-leverage improvements for the team's core workflow."
                },
                {
                    "title": "Practical Role Simulation Deliverable",
                    "objective": "Prove hands-on capability with a tangible work sample.",
                    "deliverable": "A working prototype, SOP checklist, or case study analysis directly mirroring the job description."
                }
            ],
            "autofill_payload": {
                "full_name": "Candidate Name",
                "headline": "High-Impact Specialist & Strategic Problem Solver",
                "summary": "Results-oriented professional experienced in end-to-end execution, cross-functional collaboration, and continuous optimization.",
                "top_skills": "Project Execution, Stakeholder Alignment, Analytical Problem Solving, Process Automation",
                "cover_letter_short": "Excited to bring proven execution, adaptability, and domain passion to your team."
            }
        })

    return (
        "### ⚡ Simulation Output (Add `OPENAI_API_KEY` in `.streamlit/secrets.toml` for Live GPT-4o Generation)\n\n"
        "**1. Strategic Assessment & Roadmap:**\n"
        "- **Stage 1 (Days 1–30):** Core domain audit, foundational skill calibration, and baseline portfolio setup.\n"
        "- **Stage 2 (Days 31–60):** Hands-on applied projects, workflow mastery, and cross-functional mentorship.\n"
        "- **Stage 3 (Days 61–90):** High-visibility deliverable execution, KPI benchmarking, and leadership readiness.\n\n"
        "**2. Key Action Items:**\n"
        "- Focus on measurable proof-of-work deliverables over passive consumption.\n"
        "- Calibrate weekly feedback loops to accelerate competency mastery."
    )

def call_ai(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """Production-grade AI execution helper with safe fallback simulation."""
    if not ai_client:
        return _smart_fallback_response(system_prompt, user_prompt, json_mode)

    try:
        kwargs = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.4
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        res = ai_client.chat.completions.create(**kwargs)
        return res.choices[0].message.content
    except Exception as e:
        st.warning(f"Live API fallback triggered ({str(e)}).")
        return _smart_fallback_response(system_prompt, user_prompt, json_mode)

def persist_state(table: str, payload: dict):
    if supabase:
        try:
            supabase.table(table).upsert(payload).execute()
        except Exception:
            pass

# ==============================================================================
# 3. SESSION STATE & URL QUERY PARAM HOOKS
# ==============================================================================
if "app_mode" not in st.session_state:
    st.session_state.app_mode = None

if "user_cv" not in st.session_state:
    st.session_state.user_cv = ""

if "app_base_url" not in st.session_state:
    st.session_state.app_base_url = "https://become-app.streamlit.app"

if "easy_apply_jobs" not in st.session_state:
    st.session_state.easy_apply_jobs = [
        {
            "id": "job_default_01",
            "title": "Principal AI & Systems Architect",
            "company": "NeuralScale Systems",
            "url": "https://www.linkedin.com/jobs/",
            "jd": "Lead architecture, define cross-functional technical strategies, and manage enterprise deployment pipelines.",
            "status": "Ready for Package Generation",
            "package": None
        }
    ]

# External Browser Bookmarklet Handler via Query Params
qp = st.query_params
if "easy_apply_title" in qp:
    inc_title = qp.get("easy_apply_title", "Captured Role")
    inc_comp = qp.get("easy_apply_company", "Target Organization")
    inc_url = qp.get("easy_apply_url", "https://linkedin.com/jobs")
    inc_jd = qp.get("easy_apply_jd", "Captured from external browser job posting.")

    existing_urls = [j["url"] for j in st.session_state.easy_apply_jobs]
    if inc_url not in existing_urls or inc_url == "https://linkedin.com/jobs":
        new_captured = {
            "id": f"job_{int(time.time())}",
            "title": inc_title,
            "company": inc_comp,
            "url": inc_url,
            "jd": inc_jd,
            "status": "Captured via Easy Apply",
            "package": None
        }
        st.session_state.easy_apply_jobs.insert(0, new_captured)
        st.session_state.app_mode = "individual"
        st.session_state.ind_active_tab = "🚀 Easy Apply Dashboard"
        st.toast(f"⚡ Captured '{inc_title}' directly into Easy Apply!", icon="🚀")

# ==============================================================================
# 4. DUAL-MODE STARTUP GATEWAY VIEW
# ==============================================================================
def render_startup_gateway():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem; font-weight: 900; letter-spacing: -0.02em;'>⚡ BECOME OS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.25rem; color: #9ca3af; max-width: 750px; margin: 0 auto 45px auto;'>Universal Career Navigation, Multi-Format Mock Interview Studio, Autonomous Easy Apply Engine & Enterprise Workforce Intelligence.</p>", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("""
        <div class="hero-card">
            <span class="metric-badge">INDIVIDUAL & GRADUATES</span>
            <h2 style="margin-top: 16px; font-size: 1.8rem;">👤 Individual Career Navigator</h2>
            <p style="color: #cbd5e1; line-height: 1.7; font-size: 1.05rem;">
                • <b>Universal 5-Stage Roadmaps:</b> Any profession on Earth.<br>
                • <b>Multi-Format Mock Interviews:</b> Written, Audio Simulation & Video Prompts.<br>
                • <b>Easy Apply Ecosystem:</b> Grammarly-style bookmarklet capture, tailored CVs, cover letters, custom mini-projects & auto-fill.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Individual Navigator →", key="btn_ind_gate", type="primary", use_container_width=True):
            st.session_state.app_mode = "individual"
            st.rerun()

    with c2:
        st.markdown("""
        <div class="hero-card">
            <span class="metric-badge">ENTERPRISE & HR LEADERS</span>
            <h2 style="margin-top: 16px; font-size: 1.8rem;">🏢 Organization & Workforce Hub</h2>
            <p style="color: #cbd5e1; line-height: 1.7; font-size: 1.05rem;">
                • <b>Workforce Skill Mapping Matrix:</b> Real-time capability DNA & gap heatmaps.<br>
                • <b>Internal Mobility Engine:</b> Career lattice bridges for talent retention.<br>
                • <b>Graduate Ramp-Up Accelerator:</b> 30-60-90 day onboarding & Macro Labor Analytics.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Workforce Intelligence Hub →", key="btn_org_gate", use_container_width=True):
            st.session_state.app_mode = "organization"
            st.rerun()

# ==============================================================================
# 5. MODULE A: INDIVIDUAL NAVIGATOR, MOCK INTERVIEWS & EASY APPLY DASHBOARD
# ==============================================================================
def render_mock_interview_studio():
    st.header("🎯 Universal Multi-Format Mock Interview Studio")
    st.caption("Engineered for every career possible with real-time AI scoring, coaching tips, and model answers.")

    col1, col2 = st.columns([2, 1])
    with col1:
        target_role = st.text_input("Target Career / Role", placeholder="e.g., Lead AI Engineer, Registered Nurse, Electrician, Financial Analyst")
    with col2:
        format_type = st.selectbox("Interview Format", ["✍️ Written Deep-Dive", "🎙️ Audio Simulation", "🎥 Video Presence & Behavioral"])

    if st.button("Generate Interview Session", type="primary"):
        if not target_role:
            st.warning("Please specify a target role first.")
        else:
            with st.spinner(f"Calibrating {format_type} questions for {target_role}..."):
                sys_p = "You are an elite global hiring director and executive interview coach."
                usr_p = f"""
                Generate a 5-question {format_type} mock interview for: '{target_role}'.
                Candidate background: {st.session_state.user_cv[:1500] if st.session_state.user_cv else 'General professional candidate'}

                Return a JSON object with key 'questions' containing a list of objects with:
                - 'q_num': int
                - 'question': str
                - 'what_they_look_for': str
                - 'delivery_tip': str
                """
                raw = call_ai(sys_p, usr_p, json_mode=True)
                try:
                    st.session_state.active_mock_questions = json.loads(raw).get("questions", [])
                    st.session_state.active_mock_role = target_role
                except Exception:
                    st.error("Failed to parse AI response. Please try again.")

    if "active_mock_questions" in st.session_state and st.session_state.active_mock_questions:
        st.divider()
        active_role = st.session_state.get("active_mock_role", target_role or "Target Role")
        for q in st.session_state.active_mock_questions:
            with st.expander(f"Question {q['q_num']}: {q['question']}", expanded=(q['q_num'] == 1)):
                st.info(f"**Competency Focus:** {q['what_they_look_for']}  \n**Coaching Tip:** {q['delivery_tip']}")

                if "🎙️ Audio" in format_type:
                    if hasattr(st, "audio_input"):
                        st.audio_input(f"Record Spoken Answer for Q{q['q_num']}", key=f"aud_{q['q_num']}")
                    user_ans = st.text_area("Paste or type your spoken response transcript:", key=f"aud_txt_{q['q_num']}")
                elif "🎥 Video" in format_type:
                    if hasattr(st, "camera_input"):
                        st.camera_input(f"Posture & Framing Check for Q{q['q_num']}", key=f"cam_{q['q_num']}")
                    user_ans = st.text_area("Enter your spoken response summary:", key=f"vid_txt_{q['q_num']}")
                else:
                    user_ans = st.text_area("Write your structured response:", key=f"wrt_{q['q_num']}")

                if st.button(f"Evaluate Response #{q['q_num']}", key=f"eval_btn_{q['q_num']}"):
                    if user_ans:
                        with st.spinner("Analyzing performance & generating 10/10 model answer..."):
                            feedback = call_ai(
                                "You are an empathetic, expert executive career coach.",
                                f"Role: {active_role}\nQuestion: {q['question']}\nCandidate Answer: {user_ans}\nProvide: 1) Score /10, 2) Strengths, 3) Areas for improvement, 4) A 10/10 rewritten model answer."
                            )
                            st.success("Evaluation Generated")
                            st.markdown(feedback)
                    else:
                        st.warning("Provide your response above before evaluating.")

def render_easy_apply_dashboard():
    st.markdown("""
    <div class="easy-apply-banner">
        🚀 BECOME EASY APPLY ECOSYSTEM — Capture jobs from LinkedIn, Google Jobs, or Indeed with 1-click, auto-generate tailored CVs, cover letters, mock tasks, and execute auto-fill job applications.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔌 Install Floating 'Easy Apply' Browser Bookmarklet", expanded=False):
        st.session_state.app_base_url = st.text_input(
            "Your Deployed Streamlit App URL:",
            value=st.session_state.app_base_url,
            help="Set this to your live Streamlit Cloud URL so the bookmarklet sends captured jobs straight here."
        )
        st.markdown("""
        **How to use Easy Apply on any external job site:**
        1. Copy the script below and save it as a bookmark in Chrome/Edge/Brave (`⚡ BECOME Easy Apply`).
        2. When viewing any job on **LinkedIn, Google Jobs, or Indeed**, highlight the job description (optional) and click your bookmark.
        3. It instantly captures the job details and opens your dashboard right here!
        """)
        base_url = st.session_state.app_base_url.rstrip("/")
        bookmarklet_code = f"""javascript:(function(){{var t=document.title;var u=window.location.href;var s=window.getSelection().toString()||document.body.innerText.substring(0,1500);window.open('{base_url}/?easy_apply_title='+encodeURIComponent(t)+'&easy_apply_url='+encodeURIComponent(u)+'&easy_apply_jd='+encodeURIComponent(s),'_blank');}})();"""
        st.code(bookmarklet_code, language="javascript")

    col_cv, col_add = st.columns([1, 1], gap="large")
    with col_cv:
        st.subheader("📄 Your Master Profile / Base CV")
        st.session_state.user_cv = st.text_area(
            "Paste your core professional experience and skills once:",
            value=st.session_state.user_cv,
            height=160,
            placeholder="Used dynamically by Easy Apply to tailor every job package..."
        )
    with col_add:
        st.subheader("➕ Add Job Manually")
        with st.form("manual_job_form", clear_on_submit=True):
            m_title = st.text_input("Job Title", placeholder="e.g., Senior Operations Manager")
            m_comp = st.text_input("Company Name", placeholder="e.g., Stripe / Siemens")
            m_url = st.text_input("Application URL", placeholder="https://...")
            m_jd = st.text_area("Job Description", height=70, placeholder="Paste requirements...")
            if st.form_submit_button("Add Job to Pipeline", use_container_width=True):
                if m_title:
                    new_job = {
                        "id": f"job_{int(time.time())}",
                        "title": m_title,
                        "company": m_comp or "Target Corp",
                        "url": m_url or f"https://www.google.com/search?q={urllib.parse.quote(m_title + ' apply')}",
                        "jd": m_jd,
                        "status": "Queued",
                        "package": None
                    }
                    st.session_state.easy_apply_jobs.insert(0, new_job)
                    persist_state("become_journeys_v1", {"id": new_job["id"], "data": new_job})
                    st.success(f"Added {m_title}!")
                    st.rerun()

    st.divider()
    st.subheader(f"📋 Active Easy Apply Pipeline ({len(st.session_state.easy_apply_jobs)} Jobs)")

    for idx, job in enumerate(st.session_state.easy_apply_jobs):
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([3, 1.8, 1.4, 1.2, 0.6])
            c1.markdown(f"### {job['title']} \n**{job['company']}**")
            c2.markdown(f"**Status:** `{job['status']}`")

            show_pkg = c3.button("📂 Show Package", key=f"show_pkg_{job['id']}", use_container_width=True)
            c4.link_button("Apply ↗", url=job["url"], use_container_width=True)
            if c5.button("🗑️", key=f"del_job_{job['id']}", help="Remove job"):
                st.session_state.easy_apply_jobs.pop(idx)
                st.rerun()

            if show_pkg or st.session_state.get(f"open_pkg_{job['id']}", False):
                st.session_state[f"open_pkg_{job['id']}"] = True

                if not job["package"]:
                    with st.spinner("🤖 Crafting Optimized CV, Cover Letter, Interview Prep & 2 Proof-of-Work Mini-Projects..."):
                        sys_p = "You are an elite career strategist and technical assessor."
                        usr_p = f"""
                        Job Title: {job['title']}
                        Company: {job['company']}
                        JD: {job['jd']}
                        Candidate CV: {st.session_state.user_cv if st.session_state.user_cv else 'Experienced professional'}

                        Return a JSON object with exact keys:
                        - 'optimized_cv': Full Markdown ATS-optimized CV.
                        - 'motivational_letter': Compelling cover letter.
                        - 'interview_questions': List of 5 target questions with answer guidance.
                        - 'mini_projects': List of 2 practical 1-2 hour mock tasks (each with title, objective, deliverable).
                        - 'autofill_payload': Dictionary with keys (full_name, headline, summary, top_skills, cover_letter_short).
                        """
                        res = call_ai(sys_p, usr_p, json_mode=True)
                        try:
                            job["package"] = json.loads(res)
                            job["status"] = "✅ Package Ready"
                            st.session_state.easy_apply_jobs[idx] = job
                        except Exception:
                            st.error("Generation error. Try clicking Show Package again.")

                if job["package"]:
                    pkg = job["package"]
                    t_cv, t_cl, t_pr, t_in, t_af = st.tabs([
                        "📄 Optimized CV",
                        "✉️ Cover Letter",
                        "🛠️ 2 Mini-Projects",
                        "🎯 Interview Prep",
                        "⚡ Auto-Fill & Apply"
                    ])

                    with t_cv:
                        edited_cv = st.text_area(
                            "Review & Edit Tailored CV before downloading:",
                            value=pkg.get("optimized_cv", ""),
                            height=260,
                            key=f"edit_cv_{job['id']}"
                        )
                        pkg["optimized_cv"] = edited_cv
                        st.download_button("⬇️ Download Tailored CV (.md)", edited_cv, file_name=f"CV_{job['company']}.md", key=f"dl_cv_{job['id']}")

                    with t_cl:
                        edited_cl = st.text_area(
                            "Review & Edit Cover Letter before downloading:",
                            value=pkg.get("motivational_letter", ""),
                            height=240,
                            key=f"edit_cl_{job['id']}"
                        )
                        pkg["motivational_letter"] = edited_cl
                        st.download_button("⬇️ Download Cover Letter (.md)", edited_cl, file_name=f"CoverLetter_{job['company']}.md", key=f"dl_cl_{job['id']}")

                    with t_pr:
                        st.info("💡 Complete 1 or both proof-of-work mini-projects to attach during your application and stand out from 99% of applicants.")
                        for p_idx, proj in enumerate(pkg.get("mini_projects", []), 1):
                            if isinstance(proj, dict):
                                st.markdown(f"#### Task {p_idx}: {proj.get('title', 'Case Study')}")
                                st.write(f"**Objective:** {proj.get('objective', '')}")
                                st.write(f"**Deliverable:** {proj.get('deliverable', '')}")
                            else:
                                st.markdown(f"- {proj}")

                    with t_in:
                        for q in pkg.get("interview_questions", []):
                            st.markdown(f"- {q}")

                    with t_af:
                        st.success("✅ Review your materials above, then use the Auto-Fill Injector below.")
                        af_json = json.dumps(pkg.get("autofill_payload", {}))
                        safe_af = urllib.parse.quote(af_json)
                        af_script = f"""javascript:(function(){{var data=JSON.parse(decodeURIComponent('{safe_af}'));var inputs=document.querySelectorAll('input[type="text"], textarea');inputs.forEach(function(el){{var n=(el.name+el.id+el.placeholder).toLowerCase();if(n.includes('summary')||n.includes('about'))el.value=data.summary||'';if(n.includes('cover')||n.includes('letter')||n.includes('message'))el.value=data.cover_letter_short||'';if(n.includes('skill'))el.value=data.top_skills||'';}});alert('⚡ BECOME Easy Apply: Fields auto-filled!');}})();"""
                        st.code(af_script, language="javascript")

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            st.link_button(f"🌐 Open {job['company']} Portal ↗", url=job["url"], use_container_width=True, type="primary")
                        with col_btn2:
                            if st.button("🎉 Mark as Applied", key=f"marked_applied_{job['id']}", use_container_width=True):
                                job["status"] = "🎉 Applied!"
                                st.balloons()
                                st.rerun()

def render_individual_mode():
    with st.sidebar:
        st.markdown("## 👤 Individual Mode")
        if st.button("⇄ Switch to Organization Hub", use_container_width=True):
            st.session_state.app_mode = "organization"
            st.rerun()
        st.divider()
        default_idx = 1 if st.session_state.get("ind_active_tab") == "🚀 Easy Apply Dashboard" else 0
        nav = st.radio(
            "Navigation",
            ["🧭 Universal Career Roadmap", "🚀 Easy Apply Dashboard", "🎯 Mock Interview Studio"],
            index=default_idx
        )
        st.session_state.ind_active_tab = nav

    if nav == "🧭 Universal Career Roadmap":
        st.header("🧭 Universal 5-Stage Career Navigator")
        st.caption("Engineered for every career path on Earth.")
        c1, c2 = st.columns(2)
        bg = c1.text_input("Current Background / Role", placeholder="e.g., Software Engineering Student, Marketing Associate")
        target = c2.text_input("Target Career Goal", placeholder="e.g., Principal AI Engineer, Clinical Specialist, Creative Director")

        if st.button("Generate Master Roadmap", type="primary"):
            if target:
                with st.spinner("Architecting your 5-stage career trajectory..."):
                    res = call_ai(
                        "You are BECOME, an empathetic world-class career architect.",
                        f"Build a concrete 5-stage career roadmap from '{bg}' to '{target}'. Include milestone stages, required technical/soft skills, salary progression, and weekly habits."
                    )
                    st.markdown(res)
            else:
                st.warning("Please enter a target career.")

    elif nav == "🚀 Easy Apply Dashboard":
        render_easy_apply_dashboard()

    elif nav == "🎯 Mock Interview Studio":
        render_mock_interview_studio()

# ==============================================================================
# 6. MODULE B: ENTERPRISE WORKFORCE INTELLIGENCE HUB
# ==============================================================================
def render_organization_mode():
    with st.sidebar:
        st.markdown("## 🏢 Organization Hub")
        if st.button("⇄ Switch to Individual Mode", use_container_width=True):
            st.session_state.app_mode = "individual"
            st.rerun()
        st.divider()
        org_nav = st.radio(
            "Workforce Suite",
            [
                "🗺️ Workforce Skill Mapping",
                "🔄 Internal Mobility Engine",
                "🎓 Graduate & New Hire Ramp-Up",
                "📊 Macro Labor & AI Disruption Index"
            ]
        )

    st.title("🏢 BECOME Enterprise Workforce Intelligence")

    if org_nav == "🗺️ Workforce Skill Mapping":
        st.header("🗺️ Workforce Skill Mapping Matrix")
        c1, c2 = st.columns(2)
        dept = c1.text_input("Department / Division", value="Engineering & Product")
        goal = c2.text_input("Strategic Objective", placeholder="e.g., Shift architecture to autonomous AI systems")
        roster = st.text_area("Team Roster & Skills", value="Alex (Python, SQL) | Maya (Agile, Product) | Liam (React, UI)")

        if st.button("Generate Skill Matrix & Gap Heatmap", type="primary"):
            with st.spinner("Analyzing workforce capability DNA..."):
                res = call_ai("You are an enterprise Chief People Officer.", f"Analyze team '{dept}' with objective '{goal}' based on roster:\n{roster}\n\nProvide Capability Matrix, Skill Gaps, and Upskilling Plan.")
                st.markdown(res)

    elif org_nav == "🔄 Internal Mobility Engine":
        st.header("🔄 Internal Mobility & Career Lattice Engine")
        c1, c2 = st.columns(2)
        profile = c1.text_area("Employee Profile & Aspirations", placeholder="e.g., Customer Success (3 yrs), wants to move into Product Management.")
        roles = c2.text_area("Open Internal Roles", placeholder="e.g., Associate Product Manager, Solutions Architect")

        if st.button("Calculate Internal Mobility Matches", type="primary"):
            with st.spinner("Computing career lattice bridges..."):
                res = call_ai("You are an internal talent strategist.", f"Match employee:\n{profile}\n\nAgainst roles:\n{roles}\n\nProvide match scores and a 60-day transition bridge plan.")
                st.markdown(res)

    elif org_nav == "🎓 Graduate & New Hire Ramp-Up":
        st.header("🎓 Graduate & New Hire Ramp-Up Accelerator")
        c1, c2, c3 = st.columns(3)
        role = c1.text_input("New Hire Role", placeholder="Graduate Data Analyst")
        level = c2.selectbox("Cohort Type", ["University Graduate", "Lateral Hire", "Executive Onboarding"])
        ind = c3.text_input("Industry", placeholder="FinTech / SaaS")

        if st.button("Build 30-60-90 Day Ramp-Up Plan", type="primary"):
            with st.spinner("Generating onboarding milestones..."):
                res = call_ai("You are an L&D Director.", f"Create 30-60-90 day plan for '{level}' in role '{role}' within '{ind}'. Include weekly KPIs and first-win deliverables.")
                st.markdown(res)

    elif org_nav == "📊 Macro Labor & AI Disruption Index":
        st.header("📊 Macro Labor Market & AI Augmentation Index")
        sector = st.text_input("Industry / Job Family", placeholder="Supply Chain, Corporate Law, Software Engineering")

        if st.button("Run Macro Intelligence Report", type="primary"):
            with st.spinner("Analyzing global labor demand and AI shifts..."):
                res = call_ai("You are a global labor economist.", f"Provide 2026-2027 report for '{sector}': demand/salaries, automated vs human-critical tasks, and top emerging roles.")
                st.markdown(res)

# ==============================================================================
# 7. MAIN ROUTER EXECUTION
# ==============================================================================
if st.session_state.app_mode is None:
    render_startup_gateway()
elif st.session_state.app_mode == "individual":
    render_individual_mode()
elif st.session_state.app_mode == "organization":
    render_organization_mode()
