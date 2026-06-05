from pathlib import Path
import sqlite3
import sys
from typing import Optional

import altair as alt
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from careeriq.analysis.repository import save_analysis_result
from careeriq.analysis.roadmap import generate_career_roadmap
from careeriq.analysis.scoring import score_candidate_profile
from careeriq.dashboard.market_dashboard import (
    job_postings_exist,
    load_employment_type_mix,
    load_experience_requirements,
    load_market_overview,
    load_role_categories,
    load_role_category_demand,
    load_top_cities,
    load_top_skills,
)
from careeriq.jobs.load_job_postings import load_job_postings
from careeriq.resume.profile_parser import parse_resume_profile
from careeriq.resume.profile_repository import save_candidate_profile
from careeriq.resume.text_extraction import extract_text_from_pdf


DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "careeriq_dev.sqlite"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
SAMPLE_JOBS_PATH = PROJECT_ROOT / "data" / "raw" / "sample_canadian_job_postings.csv"

TARGET_ROLES = [
    "Data Analyst",
    "Business Analyst",
    "Software Engineer",
    "Software Developer",
    "Full Stack Engineer",
    "Frontend Developer",
    "Backend Developer",
    "IT Support Technician",
    "User Support Technician",
    "Project Manager",
    "Product Manager",
    "HR Specialist",
    "Recruiter",
    "Marketing Coordinator",
    "Sales Representative",
    "Operations Coordinator",
    "Entry-level Tech Professional",
    "General Career Explorer",
]


def record_site_visit(database_path: Path) -> int:
    """Record one site visit per Streamlit session and return total visits."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS site_visits (
                visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        if "site_visit_recorded" not in st.session_state:
            connection.execute("INSERT INTO site_visits DEFAULT VALUES;")
            connection.commit()
            st.session_state["site_visit_recorded"] = True
        total_visits = connection.execute("SELECT COUNT(*) FROM site_visits;").fetchone()[0]
        return int(total_visits)
    finally:
        connection.close()


def candidate_initials(candidate_name: Optional[str]) -> str:
    """Return initials for the candidate avatar."""

    if not candidate_name:
        return "CI"
    words = [word for word in candidate_name.split() if word]
    return "".join(word[0].upper() for word in words[:2]) or "CI"


def render_candidate_avatar(candidate_name: Optional[str], profile_photo) -> None:
    """Render a profile image when supplied, otherwise render an initials avatar."""

    if profile_photo is not None:
        st.image(profile_photo, width=96)
        return

    initials = candidate_initials(candidate_name)
    st.markdown(
        f"""
        <div class="avatar-circle">{initials}</div>
        """,
        unsafe_allow_html=True,
    )


def highlighted_bar_chart(dataframe, label_column: str, value_column: str, height: int = 320) -> None:
    """Render a bar chart with distinct highest and lowest bar colors."""

    if dataframe.empty:
        st.info("No data available for this chart.")
        return

    chart_data = dataframe.copy()
    max_value = chart_data[value_column].max()
    min_value = chart_data[value_column].min()
    chart_data["bar_status"] = "Other"
    if max_value != min_value:
        chart_data.loc[chart_data[value_column] == max_value, "bar_status"] = "Highest"
        chart_data.loc[chart_data[value_column] == min_value, "bar_status"] = "Lowest"

    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            x=alt.X(f"{value_column}:Q", title="Postings"),
            y=alt.Y(f"{label_column}:N", title=None, sort="-x"),
            color=alt.Color(
                "bar_status:N",
                scale=alt.Scale(
                    domain=["Highest", "Lowest", "Other"],
                    range=["#2A9D8F", "#E9A6A6", "#8FB3C8"],
                ),
                legend=None,
            ),
            tooltip=[label_column, value_column],
        )
        .properties(height=height)
    )
    st.altair_chart(chart, use_container_width=True)


st.set_page_config(
    page_title="CareerIQ",
    page_icon=":material/analytics:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; }
    .avatar-circle {
        width: 96px;
        height: 96px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563EB 0%, #2A9D8F 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 700;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18);
    }
    .section-note {
        color: #475569;
        font-size: 0.95rem;
        margin-top: -0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

site_visits = record_site_visit(DATABASE_PATH)
header_columns = st.columns([3, 1])
with header_columns[0]:
    st.title("CareerIQ")
    st.caption("AI-powered career intelligence for technical and non-technical roles.")
with header_columns[1]:
    st.metric("Site visits", f"{site_visits:,}")

main_tab, dashboard_tab = st.tabs(["Resume intelligence", "Job market dashboard"])

with main_tab:
    target_role = st.selectbox(
        "Target role",
        TARGET_ROLES,
    )

    profile_photo = st.file_uploader("Optional profile image", type=["png", "jpg", "jpeg"])
    uploaded_resume = st.file_uploader("Upload your resume PDF", type=["pdf"])

    if uploaded_resume is None:
        st.info("Upload a PDF resume to extract clean text for the next analysis step.")
    else:
        try:
            result = extract_text_from_pdf(uploaded_resume, file_name=uploaded_resume.name)
        except Exception as exc:
            st.error(str(exc))
        else:
            if result.word_count < 20:
                st.error(
                    "CareerIQ could not extract enough readable text from this PDF. "
                    "Please upload a text-based resume PDF instead of a scanned image, or export your resume again from Word or Google Docs."
                )
                st.text_area("Raw extraction preview", value=result.raw_text, height=180)
                st.stop()

            profile = parse_resume_profile(result.cleaned_text)
            display_name = profile.candidate_name or "CareerIQ user"

            candidate_header = st.columns([1, 4])
            with candidate_header[0]:
                render_candidate_avatar(profile.candidate_name, profile_photo)
            with candidate_header[1]:
                st.subheader(f"Welcome, {display_name}")
                st.markdown(
                    f"""
                    <div class="section-note">
                    CareerIQ analyzed your resume for <strong>{target_role}</strong> and compared it with the current sample job market.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if result.embedded_image_count > 0 and profile_photo is None:
                    st.info(
                        "This PDF appears to contain an embedded image. For privacy and reliability, CareerIQ shows an initials avatar unless you upload a separate profile image."
                    )

            st.success("Resume text extracted successfully.")

            metric_columns = st.columns(4)
            metric_columns[0].metric("File", result.file_name)
            metric_columns[1].metric("Target role", target_role)
            metric_columns[2].metric("Pages", result.page_count)
            metric_columns[3].metric("Words", result.word_count)

            profile_tab, preview_tab, raw_tab = st.tabs(["Parsed profile", "Cleaned text", "Raw extraction"])

            with profile_tab:
                overview_columns = st.columns(5)
                overview_columns[0].metric("Skills", len(profile.skills))
                overview_columns[1].metric("Education", len(profile.education))
                overview_columns[2].metric("Certifications", len(profile.certifications))
                overview_columns[3].metric("Experience lines", len(profile.experience))
                overview_columns[4].metric("Projects", len(profile.projects))

                st.header("Career Scores")
                if not job_postings_exist(DATABASE_PATH):
                    st.warning("Load job market data before scoring this resume.")
                    if st.button("Load sample data for scoring"):
                        summary = load_job_postings(
                            csv_path=SAMPLE_JOBS_PATH,
                            database_path=DATABASE_PATH,
                            schema_path=SCHEMA_PATH,
                            replace=True,
                        )
                        st.success(f"Loaded {summary.job_postings_loaded} job postings.")
                        st.rerun()
                else:
                    score_result = score_candidate_profile(
                        profile=profile,
                        target_role=target_role,
                        database_path=DATABASE_PATH,
                    )

                    score_columns = st.columns(4)
                    score_columns[0].metric(
                        "Market competitiveness",
                        f"{score_result.market_competitiveness_score}/100",
                    )
                    score_columns[1].metric("Employability", f"{score_result.employability_score}/100")
                    score_columns[2].metric("Best job match", f"{score_result.best_job_match_score}/100")
                    score_columns[3].metric("Avg top matches", f"{score_result.average_job_match_score}/100")

                    st.caption(f"Scored against: {score_result.role_category}")

                    insight_columns = st.columns(2)
                    with insight_columns[0]:
                        st.subheader("Missing high-demand skills")
                        if score_result.missing_skills:
                            st.dataframe(
                                [
                                    {
                                        "Skill": gap.skill_name,
                                        "Category": gap.skill_category,
                                        "Demand count": gap.demand_count,
                                        "Demand %": gap.demand_percentage,
                                        "Priority": gap.priority_level,
                                        "Reason": gap.recommendation_reason,
                                    }
                                    for gap in score_result.missing_skills
                                ],
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.success("No major missing skills found for the selected market slice.")

                    with insight_columns[1]:
                        st.subheader("Matched market skills")
                        if score_result.matched_market_skills:
                            st.write(", ".join(score_result.matched_market_skills))
                        else:
                            st.write("No market skills matched yet.")

                    st.header("Top Matching Postings")
                    if score_result.top_job_matches:
                        st.dataframe(
                            [
                                {
                                    "Job": match.job_title,
                                    "Company": match.company,
                                    "Location": match.location,
                                    "Score": match.job_match_score,
                                    "Matched skills": ", ".join(match.matched_skills),
                                    "Missing skills": ", ".join(match.missing_skills),
                                }
                                for match in score_result.top_job_matches
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.write("No job matches available.")

                    roadmap = generate_career_roadmap(profile, score_result)
                    st.header("Career Roadmap")
                    st.metric("Readiness", roadmap.readiness_label)
                    st.write(roadmap.summary)

                    roadmap_columns = st.columns(2)
                    with roadmap_columns[0]:
                        st.markdown("**Learning path**")
                        st.dataframe(
                            [
                                {
                                    "Priority": step.priority,
                                    "Focus": step.title,
                                    "Action": step.action,
                                    "Reason": step.reason,
                                }
                                for step in roadmap.learning_path
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )

                        st.markdown("**Recommended certifications**")
                        for certification in roadmap.certifications:
                            st.write(f"- {certification}")

                    with roadmap_columns[1]:
                        st.markdown("**Portfolio projects**")
                        for project in roadmap.projects:
                            st.write(f"- {project}")

                        st.markdown("**Target role progression**")
                        for role in roadmap.target_roles:
                            st.write(f"- {role}")

                    with st.expander("How these scores are calculated"):
                        for note in score_result.scoring_notes:
                            st.write(f"- {note}")

                    if st.button("Save parsed profile and analysis"):
                        candidate_id = save_candidate_profile(
                            database_path=DATABASE_PATH,
                            schema_path=SCHEMA_PATH,
                            resume_file_name=result.file_name,
                            raw_resume_text=result.cleaned_text,
                            target_role=target_role,
                            profile=profile,
                        )
                        analysis_id = save_analysis_result(
                            database_path=DATABASE_PATH,
                            schema_path=SCHEMA_PATH,
                            candidate_id=candidate_id,
                            result=score_result,
                        )
                        st.success(
                            f"Saved candidate profile #{candidate_id} and analysis #{analysis_id} to SQLite."
                        )

                st.header("Parsed Resume Profile")
                st.subheader("Detected Skills")
                if profile.skills:
                    st.dataframe(
                        [
                            {
                                "Skill": skill.name,
                                "Confidence": skill.confidence_score,
                                "Method": skill.extraction_method,
                            }
                            for skill in profile.skills
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.warning(
                        "CareerIQ did not detect known skills from the current skills library. "
                        "Try adding a clear Skills section with role-relevant tools, methods, and platforms."
                    )

                detail_columns = st.columns(2)

                with detail_columns[0]:
                    st.subheader("Education")
                    if profile.education:
                        for item in profile.education:
                            st.write(f"- {item}")
                    else:
                        st.write("No education lines detected.")

                    st.subheader("Certifications")
                    if profile.certifications:
                        for item in profile.certifications:
                            st.write(f"- {item}")
                    else:
                        st.write("No certification lines detected.")

                with detail_columns[1]:
                    st.subheader("Experience")
                    if profile.experience:
                        for item in profile.experience:
                            st.write(f"- {item}")
                    else:
                        st.write("No experience lines detected.")

                    st.subheader("Projects")
                    if profile.projects:
                        for item in profile.projects:
                            st.write(f"- {item}")
                    else:
                        st.write("No project lines detected.")

                if st.button("Save parsed profile"):
                    candidate_id = save_candidate_profile(
                        database_path=DATABASE_PATH,
                        schema_path=SCHEMA_PATH,
                        resume_file_name=result.file_name,
                        raw_resume_text=result.cleaned_text,
                        target_role=target_role,
                        profile=profile,
                    )
                    st.success(f"Saved candidate profile #{candidate_id} to SQLite.")

            with preview_tab:
                st.text_area(
                    "Cleaned resume text",
                    value=result.cleaned_text,
                    height=420,
                )

            with raw_tab:
                st.text_area(
                    "Raw PDF text",
                    value=result.raw_text,
                    height=420,
                )

            st.download_button(
                "Download cleaned text",
                data=result.cleaned_text,
                file_name="resume_cleaned_text.txt",
                mime="text/plain",
            )

with dashboard_tab:
    if not job_postings_exist(DATABASE_PATH):
        st.warning("No job market data found.")
        if st.button("Load sample job market data"):
            summary = load_job_postings(
                csv_path=SAMPLE_JOBS_PATH,
                database_path=DATABASE_PATH,
                schema_path=SCHEMA_PATH,
                replace=True,
            )
            st.success(f"Loaded {summary.job_postings_loaded} job postings.")
            st.rerun()
    else:
        role_categories = ["All"] + load_role_categories(DATABASE_PATH)
        selected_category = st.selectbox("Role category", role_categories)

        overview = load_market_overview(DATABASE_PATH, selected_category)
        dashboard_metrics = st.columns(4)
        dashboard_metrics[0].metric("Job postings", overview["posting_count"])
        dashboard_metrics[1].metric("Companies", overview["company_count"])
        dashboard_metrics[2].metric("Locations", overview["location_count"])
        dashboard_metrics[3].metric("Employment types", overview["employment_type_count"])

        top_skills = load_top_skills(DATABASE_PATH, selected_category)
        top_cities = load_top_cities(DATABASE_PATH, selected_category)
        experience = load_experience_requirements(DATABASE_PATH, selected_category)
        employment_mix = load_employment_type_mix(DATABASE_PATH, selected_category)
        role_demand = load_role_category_demand(DATABASE_PATH)

        chart_columns = st.columns(2)

        with chart_columns[0]:
            st.subheader("Most in-demand skills")
            highlighted_bar_chart(top_skills, "skill_name", "posting_count")
            st.dataframe(top_skills, use_container_width=True, hide_index=True)

            st.subheader("Experience requirements")
            highlighted_bar_chart(experience, "experience_level", "posting_count", height=240)
            st.dataframe(experience, use_container_width=True, hide_index=True)

        with chart_columns[1]:
            st.subheader("Top hiring cities")
            highlighted_bar_chart(top_cities, "location", "posting_count")
            st.dataframe(top_cities, use_container_width=True, hide_index=True)

            st.subheader("Hiring by role category")
            highlighted_bar_chart(role_demand, "role_category", "posting_count", height=280)
            st.dataframe(role_demand, use_container_width=True, hide_index=True)

        st.subheader("Employment type mix")
        highlighted_bar_chart(employment_mix, "employment_type", "posting_count", height=220)
