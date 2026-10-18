
import io
import html

import streamlit as st
import plotly.graph_objects as go

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)

from career_generator import generate_career_package


st.set_page_config(
    page_title="Personalized Career Content Generator",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 AI-Based Personalized Career Content Generator")
st.write(
    "Generate a career report, understand your skill profile, "
    "and track your weekly learning progress."
)


# --------------------------------------------------
# CAREER READINESS SCORE + SKILL RADAR
# --------------------------------------------------

SKILL_CATEGORIES = {
    "Programming": [
        "python", "java", "c++", "c", "javascript", "programming",
        "coding", "typescript",
    ],
    "Problem Solving": [
        "dsa", "data structures", "algorithms", "leetcode",
        "problem solving", "competitive programming",
    ],
    "Web Development": [
        "html", "css", "react", "angular", "node.js", "nodejs",
        "javascript", "web development", "frontend", "backend",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "mongodb", "database",
        "sqlite", "oracle",
    ],
    "Tools & Version Control": [
        "git", "github", "docker", "linux", "aws", "azure",
        "cloud", "vscode",
    ],
    "Communication": [
        "communication", "presentation", "teamwork",
        "leadership", "collaboration", "public speaking",
    ],
}


def calculate_readiness_score(skills):
    """
    Produce a simple profile-coverage score.
    This is not a validated measure of employability.
    """
    text = skills.lower()
    scores = {}

    for category, keywords in SKILL_CATEGORIES.items():
        matched = sum(
            1 for keyword in keywords
            if keyword in text
        )

        # Each category gets a transparent coverage score.
        scores[category] = round(
            (matched / len(keywords)) * 100
        )

    overall = round(sum(scores.values()) / len(scores))
    return overall, scores


def show_skill_radar(scores):
    categories = list(scores.keys())
    values = list(scores.values())

    # Close the radar shape.
    categories = categories + categories[:1]
    values = values + values[:1]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name="Skill profile",
                hovertemplate="%{theta}: %{r}%<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix="%",
            )
        ),
        showlegend=False,
        margin=dict(l=45, r=45, t=30, b=30),
        height=420,
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# INTERACTIVE ROADMAP TRACKER
# --------------------------------------------------

ROADMAP_TASKS = {
    "Week 1 — Strengthen fundamentals": [
        "Revise core programming concepts",
        "Solve five beginner coding problems",
        "Write down three topics to improve",
    ],
    "Week 2 — Practise problem solving": [
        "Practise arrays and strings",
        "Solve five additional coding problems",
        "Review and correct previous mistakes",
    ],
    "Week 3 — Build a project": [
        "Choose a small project idea",
        "Implement the main functionality",
        "Upload the project to GitHub",
    ],
    "Week 4 — Prepare for opportunities": [
        "Practise common interview questions",
        "Update your resume and GitHub README",
        "Explain your project aloud as interview practice",
    ],
}


def show_roadmap_tracker():
    st.subheader("🗓️ Your Learning Roadmap")
    st.write(
        "Complete tasks as you finish them. Your progress is maintained "
        "while this Streamlit session is active."
    )

    total_tasks = sum(len(tasks) for tasks in ROADMAP_TASKS.values())
    completed_tasks = 0

    for week, tasks in ROADMAP_TASKS.items():
        with st.expander(week, expanded=(week.startswith("Week 1"))):
            for index, task in enumerate(tasks):
                key = f"roadmap_{week}_{index}"

                st.checkbox(
                    task,
                    key=key,
                )

                if st.session_state.get(key, False):
                    completed_tasks += 1

    progress = completed_tasks / total_tasks if total_tasks else 0

    st.progress(progress)
    st.write(
        f"**Roadmap progress: {completed_tasks}/{total_tasks} tasks "
        f"completed ({round(progress * 100)}%)**"
    )

    if completed_tasks == total_tasks:
        st.success("Amazing work! You completed the entire roadmap.")

    if st.button("Reset roadmap progress"):
        for week, tasks in ROADMAP_TASKS.items():
            for index, _ in enumerate(tasks):
                key = f"roadmap_{week}_{index}"
                st.session_state[key] = False

        st.rerun()


# --------------------------------------------------
# DEMO REPORT
# --------------------------------------------------

def create_demo_report(skills, interests, education, target_role):
    return {
        "professional_summary": (
            f"DEMO CONTENT: This is a sample report, not a live AI assessment. "
            f"The candidate is studying {education} and is interested in "
            f"{interests}. Their reported skills include {skills}. Their "
            f"target role is {target_role}. Strengthening core concepts, "
            f"building projects, and practising problem-solving can help "
            f"them prepare for relevant opportunities."
        ),
        "skill_gap_report": {
            "Skills to strengthen": [
                "Problem-solving and data structures",
                "Programming fundamentals and debugging",
                "Git, GitHub, and project documentation",
            ],
            "Suggested projects": [
                f"Build a small project related to {interests}.",
                f"Create a portfolio project relevant to {target_role}.",
            ],
            "Note": (
                "These are general demo suggestions, not an AI assessment "
                "of your actual skill gaps."
            ),
        },
        "learning_roadmap": {
            "Week 1": {
                "Goal": "Review programming fundamentals.",
                "Task": "Revise key concepts and solve beginner problems.",
            },
            "Week 2": {
                "Goal": "Build problem-solving skills.",
                "Task": "Practise arrays, strings, and basic data structures.",
            },
            "Week 3": {
                "Goal": "Build a practical project.",
                "Task": "Create a small application and track it using Git.",
            },
            "Week 4": {
                "Goal": "Prepare for interviews.",
                "Task": "Polish your resume, README, and project explanation.",
            },
        },
        "interview_preparation": {
            "Sample questions": [
                {
                    "Question": f"Why do you want to become a {target_role}?",
                    "Sample answer": (
                        f"I am interested in {interests} and want to apply "
                        "my skills to practical problems. I am improving "
                        "my fundamentals and building projects."
                    ),
                },
                {
                    "Question": "How do you approach a difficult problem?",
                    "Sample answer": (
                        "I break it into smaller parts, test possible "
                        "solutions, and review mistakes to improve."
                    ),
                },
                {
                    "Question": "How do you demonstrate your technical skills?",
                    "Sample answer": (
                        "I practise coding, build projects, and explain "
                        "my implementation and design decisions."
                    ),
                },
            ],
            "Preparation tips": [
                "Practise explaining your projects clearly.",
                "Review fundamentals and solve problems consistently.",
            ],
        },
    }


# --------------------------------------------------
# REPORT DISPLAY + PDF
# --------------------------------------------------

def display_content(content):
    if isinstance(content, dict):
        for key, value in content.items():
            st.markdown(f"**{key.replace('_', ' ').title()}**")
            display_content(value)

    elif isinstance(content, list):
        for item in content:
            if isinstance(item, (dict, list)):
                display_content(item)
            else:
                st.markdown(f"- {item}")

    else:
        st.write(str(content))


def pdf_text(value):
    if isinstance(value, dict):
        return "\n".join(
            f"{key.replace('_', ' ').title()}: {pdf_text(item)}"
            for key, item in value.items()
        )

    if isinstance(value, list):
        return "\n".join(f"- {pdf_text(item)}" for item in value)

    text = str(value)

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u2026": "...",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", errors="replace").decode("latin-1")


def create_pdf(report, profile, is_demo, score, skill_scores):
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Personalized Career Report",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CareerTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=19,
        leading=24,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "CareerHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor("#234E70"),
    )

    body_style = ParagraphStyle(
        "CareerBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5,
        wordWrap="CJK",
    )

    story = [Paragraph("Personalized Career Report", title_style)]

    if is_demo:
        story.append(
            Paragraph(
                "<b>DEMO REPORT - SAMPLE CONTENT, NOT LIVE AI-GENERATED</b>",
                body_style,
            )
        )

    story.append(Paragraph("Candidate Profile", heading_style))

    for label, value in profile.items():
        story.append(
            Paragraph(
                f"<b>{html.escape(label)}:</b> "
                f"{html.escape(pdf_text(value))}",
                body_style,
            )
        )

    story.append(Paragraph("Career Readiness Snapshot", heading_style))
    story.append(
        Paragraph(
            f"Rule-based skill profile coverage score: {score}/100",
            body_style,
        )
    )

    for category, value in skill_scores.items():
        story.append(
            Paragraph(
                f"{html.escape(category)}: {value}%",
                body_style,
            )
        )

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.7))

    sections = [
        ("professional_summary", "Professional Summary"),
        ("skill_gap_report", "Skill Gap Report"),
        ("learning_roadmap", "Learning Roadmap"),
        ("interview_preparation", "Interview Preparation"),
    ]

    for key, heading in sections:
        story.append(Paragraph(html.escape(heading), heading_style))
        content = pdf_text(report.get(key, "Not available."))

        for line in content.splitlines():
            if line.strip():
                story.append(
                    Paragraph(html.escape(line.strip()), body_style)
                )
            else:
                story.append(Spacer(1, 4))

    document.build(story)
    buffer.seek(0)
    return buffer


# --------------------------------------------------
# MAIN USER FORM
# --------------------------------------------------

with st.form("career_form"):
    st.subheader("Tell us about yourself")

    skills = st.text_area(
        "Your current skills",
        placeholder="Example: Java, Python, HTML, CSS, SQL, Git and GitHub",
    )

    interests = st.text_area(
        "Your interests",
        placeholder="Example: AI, web development, problem-solving",
    )

    education = st.text_input(
        "Education",
        placeholder="Example: 3rd-year Computer Science student",
    )

    target_role = st.text_input(
        "Target job role",
        placeholder="Example: Software Developer",
    )

    generation_mode = st.radio(
        "Report generation mode",
        [
            "Demo report (no API calls)",
            "Live AI report (Gemini API)",
        ],
        index=0,
    )

    submitted = st.form_submit_button(
        "Generate My Career Report",
        type="primary",
        use_container_width=True,
    )


if submitted:
    if not all(
        value.strip()
        for value in (skills, interests, education, target_role)
    ):
        st.warning("Please fill in all four fields.")

    else:
        is_demo = generation_mode == "Demo report (no API calls)"

        profile = {
            "Skills": skills.strip(),
            "Interests": interests.strip(),
            "Education": education.strip(),
            "Target Role": target_role.strip(),
        }

        try:
            with st.spinner(
                "Preparing your demo report..."
                if is_demo
                else "Generating your report with Gemini..."
            ):
                if is_demo:
                    report = create_demo_report(
                        skills.strip(),
                        interests.strip(),
                        education.strip(),
                        target_role.strip(),
                    )
                else:
                    report = generate_career_package(
                        skills=skills.strip(),
                        interests=interests.strip(),
                        education=education.strip(),
                        target_role=target_role.strip(),
                    )

                score, skill_scores = calculate_readiness_score(skills)

                pdf_buffer = create_pdf(
                    report,
                    profile,
                    is_demo,
                    score,
                    skill_scores,
                )

            # Store the result so it remains available during reruns.
            st.session_state["career_report"] = report
            st.session_state["career_profile"] = profile
            st.session_state["career_is_demo"] = is_demo
            st.session_state["career_pdf"] = pdf_buffer.getvalue()
            st.session_state["career_score"] = score
            st.session_state["career_skill_scores"] = skill_scores

        except Exception as error:
            st.error(str(error))


# Show the last generated report after Streamlit reruns.
if "career_report" in st.session_state:
    report = st.session_state["career_report"]
    is_demo = st.session_state["career_is_demo"]
    score = st.session_state["career_score"]
    skill_scores = st.session_state["career_skill_scores"]

    if is_demo:
        st.warning(
            "DEMO MODE: Sample report content. No Gemini API call was made."
        )
    else:
        st.success("Your live AI-generated career report is ready!")

    st.divider()
    st.header("📊 Career Readiness Snapshot")

    st.caption(
        "This is an estimated, rule-based skill-profile coverage score, "
        "not a validated measure of employability. It checks for selected "
        "keywords in the skills you entered."
    )

    metric_col, detail_col = st.columns([1, 2])

    with metric_col:
        st.metric("Profile coverage score", f"{score}/100")
        st.progress(score / 100)

    with detail_col:
        show_skill_radar(skill_scores)

    with st.expander("See the category breakdown"):
        for category, value in skill_scores.items():
            st.write(f"**{category}: {value}%**")
            st.progress(value / 100)

    st.divider()
    st.header("📄 Your Career Report")

    tab_summary, tab_skills, tab_roadmap, tab_interview = st.tabs([
        "Professional Summary",
        "Skill Gap Report",
        "Learning Roadmap",
        "Interview Preparation",
    ])

    with tab_summary:
        display_content(report["professional_summary"])

    with tab_skills:
        display_content(report["skill_gap_report"])

    with tab_roadmap:
        display_content(report["learning_roadmap"])

    with tab_interview:
        display_content(report["interview_preparation"])

    st.download_button(
        label="📄 Download Career Report (PDF)",
        data=st.session_state["career_pdf"],
        file_name=(
            "demo_career_report.pdf"
            if is_demo
            else "personalized_career_report.pdf"
        ),
        mime="application/pdf",
        use_container_width=True,
    )

st.divider()
show_roadmap_tracker()
