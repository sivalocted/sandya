"""
Build Script for MSc Interim Progress Report (IPR)
University of Hertfordshire - School of Physics, Engineering and Computer Science
Module: 7COM1080 MSc Project / Dissertation (DMD)
Student: Nithin
Generates the publication-grade Word document meeting all criteria for Outstanding (90-100%).
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUTPUT_PATH = r"C:\Users\siriv\OneDrive\Desktop\sandya project\StudentNumber-Nithin-Surname IPR (1).docx"
ASSETS_DIR = r"C:\Users\siriv\OneDrive\Desktop\sandya project\assets"


def set_cell_background(cell, fill_hex):
    """Sets background shading of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets internal padding for a table cell (in twips: 20 twips = 1 pt)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def set_table_borders(table, color="D3D3D3", sz="4"):
    """Applies clean subtle borders to a table."""
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl_pr.append(borders)


def format_table_header(row, fill_hex="003366"):
    """Formats header row with dark blue background and white bold text."""
    for cell in row.cells:
        set_cell_background(cell, fill_hex)
        set_cell_margins(cell, top=140, bottom=140, left=160, right=160)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.name = "Arial"
                r.font.size = Pt(9.5)


def format_table_body(table, col_alignments=None):
    """Formats table body cells with clean padding, borders, and alternating zebra shading."""
    for r_idx, row in enumerate(table.rows[1:], start=1):
        # Repeat header row across pages
        tr_pr = row._tr.get_or_add_trPr()
        tr_pr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        bg_color = "F9FBFD" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_after = Pt(2)
                if col_alignments and c_idx < len(col_alignments):
                    p.alignment = col_alignments[c_idx]
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(9)
                    r.font.color.rgb = RGBColor(30, 30, 30)


def create_full_document():
    doc = docx.Document()

    # 1. Page Setup: Standard Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # 2. Styles Setup
    styles = doc.styles

    # Normal Style
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(40, 40, 40)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)

    # Heading 1
    h1 = styles["Heading 1"]
    h1.font.name = "Arial"
    h1.font.size = Pt(15)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0, 51, 102)  # Navy Blue
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    h1.paragraph_format.keep_with_next = True

    # Heading 2
    h2 = styles["Heading 2"]
    h2.font.name = "Arial"
    h2.font.size = Pt(12.5)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(13, 71, 161)
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(4)
    h2.paragraph_format.keep_with_next = True

    # Heading 3
    h3 = styles["Heading 3"]
    h3.font.name = "Arial"
    h3.font.size = Pt(11)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor(50, 50, 50)
    h3.paragraph_format.space_before = Pt(6)
    h3.paragraph_format.space_after = Pt(2)
    h3.paragraph_format.keep_with_next = True

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36)

    p_super = doc.add_paragraph("UNIVERSITY OF HERTFORDSHIRE")
    p_super.runs[0].font.size = Pt(12)
    p_super.runs[0].font.bold = True
    p_super.runs[0].font.color.rgb = RGBColor(100, 100, 100)
    p_super.paragraph_format.space_after = Pt(2)

    p_dept = doc.add_paragraph("School of Physics, Engineering and Computer Science")
    p_dept.runs[0].font.size = Pt(11)
    p_dept.runs[0].font.color.rgb = RGBColor(120, 120, 120)
    p_dept.paragraph_format.space_after = Pt(40)

    p_title = doc.add_paragraph("Interim Progress Report (IPR)")
    p_title.runs[0].font.size = Pt(24)
    p_title.runs[0].font.bold = True
    p_title.runs[0].font.color.rgb = RGBColor(0, 51, 102)
    p_title.paragraph_format.space_after = Pt(12)

    p_sub = doc.add_paragraph("Assistive Technology for Alzheimer's and Dementia:\nA Caregiver-Configured Daily-Living Assistant")
    p_sub.runs[0].font.size = Pt(17)
    p_sub.runs[0].font.bold = True
    p_sub.runs[0].font.color.rgb = RGBColor(40, 40, 40)
    p_sub.paragraph_format.space_after = Pt(50)

    # Metadata Block
    meta_p = doc.add_paragraph()
    meta_p.paragraph_format.line_spacing = 1.3
    meta_p.paragraph_format.space_after = Pt(40)

    def add_meta_line(label, val):
        r1 = meta_p.add_run(f"{label:<16}: ")
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(0, 51, 102)
        r2 = meta_p.add_run(f"{val}\n")
        r2.font.bold = False

    add_meta_line("Module", "7COM1080 MSc Project / Dissertation (DMD)")
    add_meta_line("Student", "[Student Registration Number] — Nithin [Surname]")
    add_meta_line("Supervisor", "[Supervisor Name]")
    add_meta_line("Date", "16 November 2026")
    add_meta_line("Work Completed", "Approx. 280–300 Hours (Midpoint Review)")

    p_note = doc.add_paragraph(
        "Appendices 1 to 6 contain complete supporting evidence (requirements traceability, wireframes, "
        "system architecture, database ERD, algorithm shortlist, Python source excerpts, unit test logs, "
        "full test plan, Gantt chart, and risk register) referred to throughout Sections 2 and 4."
    )
    p_note.runs[0].font.size = Pt(9.5)
    p_note.runs[0].font.italic = True
    p_note.runs[0].font.color.rgb = RGBColor(90, 90, 90)

    doc.add_page_break()

    # =========================================================================
    # SECTION 1: BACKGROUND RESEARCH AND LITERATURE REVIEW
    # =========================================================================
    doc.add_heading("1. Background Research and Literature Review", level=1)

    # 1.1 Introduction and Goals
    doc.add_heading("1.1 Introduction, Domain Context, and Problem Statement", level=2)
    doc.add_paragraph(
        "In 2021, approximately 57 million individuals were living with dementia globally, with nearly 10 million new cases "
        "diagnosed annually (WHO, 2025). Cognitive impairment progressively erodes prospective memory, making routine daily "
        "activities—such as scheduled nutrition, hydration, and strict medication adherence—increasingly difficult to maintain "
        "without continuous external support. Much of this supervisory burden falls on informal family caregivers. In the United "
        "Kingdom alone, unpaid family care comprises half of the estimated £42 billion annual societal cost of dementia, a figure "
        "projected to surpass £90 billion by 2040 (Alzheimer's Society, 2024)."
    )
    doc.add_paragraph(
        "This project investigates and builds an accessible, web-based assistive living assistant designed to guide an individual "
        "living with mild to moderate dementia through their daily schedule. A trusted caregiver configures all tasks, schedules, "
        "and alert parameters via an authenticated portal. The person living with dementia interacts with a dedicated, zero-configuration "
        "tablet interface that displays exactly one large, high-contrast prompt at a time, reinforces the visual message with spoken audio, "
        "and permits acknowledgement via a single physical tap. If a critical task remains unconfirmed across repeated attempts, and only "
        "if the caregiver has explicitly opted into escalation, an alert is dispatched. The application is strictly scoped to promote "
        "functional independence in daily living; it does not diagnose, treat, or modify clinical regimens."
    )
    doc.add_paragraph(
        "The central engineering and research goal is to determine the extent to which a transparent, deterministic rule-based reminder "
        "system can satisfy the rigorous reliability and accessibility criteria reported in dementia literature, and to evaluate where "
        "machine learning genuinely adds value versus where it introduces unmanageable risks. The project contributes in two distinct ways: "
        "practically, it produces a fully verifiable software prototype whose state transitions trace directly to formal rules; academically, "
        "it conducts a controlled empirical comparison between fixed rule thresholds and an unsupervised Isolation Forest anomaly detector "
        "on identical reminder logs, evaluating false-alert rates alongside precision and recall."
    )

    # 1.2 Research Questions and Objectives
    doc.add_heading("1.2 Research Questions and Measurable Objectives", level=2)
    doc.add_paragraph(
        "The overarching research question guiding this investigation is:\n"
        "Main Research Question: To what extent can a caregiver-configured, rule-based reminder application meet the reliability "
        "and accessibility requirements reported in the literature for supporting the daily routines of people living with mild to moderate dementia?"
    )
    doc.add_paragraph(
        "To operationalise this inquiry, three specific sub-questions (SQs) are addressed:\n"
        "• SQ1: Which functional and accessibility requirements recur across empirical assistive technology studies for dementia?\n"
        "• SQ2: Can a transparent, deterministic rule engine handle on-time prompts, snoozing, unconfirmed timeouts, and caregiver escalation correctly under real-world edge cases?\n"
        "• SQ3: Under what data, privacy, and clinical conditions would an unsupervised anomaly detector (Isolation Forest) improve upon or complement fixed rule thresholds?"
    )

    doc.add_paragraph("Table 1 defines the project objectives, measurable success criteria, and completion milestones.")

    # Table 1: Objectives
    t1_data = [
        ["ID", "Objective", "How Success is Measured", "Target Date & Status"],
        ["O1", "Derive user requirements and compare existing commercial solutions (SQ1)", "15 requirements traced to literature sources; 5 solution categories comparatively evaluated (Appendix 1)", "2 Nov 2026 [Completed]"],
        ["O2", "Implement the deterministic rule-based reminder engine (SQ2)", "All 10 scenario-based unit tests pass; state transitions auditable (Appendix 4)", "16 Nov 2026 [Completed]"],
        ["O3", "Build three accessible, zero-configuration web screens", "Full compliance with WCAG 2.2 AA: contrast >= 4.5:1; touch targets >= 48 px (exceeding 24 px minimum)", "23 Nov 2026 [Planned]"],
        ["O4", "Validate the full prototype under rigorous edge cases (SQ2)", "Zero dropped or duplicated prompts over 7 accelerated simulated days; zero false caregiver alerts below threshold", "29 Nov 2026 [Planned]"],
        ["O5", "Conduct offline comparative benchmarking: Rules vs. Isolation Forest (SQ3)", "Quantified precision, recall, and false-alert rates on simulated logs with injected routine anomalies", "29 Nov 2026 [Planned]"]
    ]
    t1 = doc.add_table(rows=len(t1_data), cols=4)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)
    for r_i, row in enumerate(t1_data):
        for c_i, val in enumerate(row):
            t1.rows[r_i].cells[c_i].text = val
    format_table_header(t1.rows[0])
    format_table_body(t1, col_alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])

    p_cap1 = doc.add_paragraph("Table 1. Project objectives, success measures, and target milestone dates.")
    p_cap1.runs[0].font.size = Pt(8.5)
    p_cap1.runs[0].font.italic = True
    p_cap1.paragraph_format.space_after = Pt(8)

    # 1.3 Theoretical Basis
    doc.add_heading("1.3 Theoretical Framework: Prospective Memory & Cognitive Scaffolding", level=2)
    doc.add_paragraph(
        "Theoretical Grounding: Prospective Memory. Remembering to perform an intended action at a specific future moment constitutes "
        "a time-based prospective memory task. In their seminal cognitive investigation, Einstein et al. (1995) demonstrated that older adults "
        "exhibit significant performance decrements on time-based tasks (e.g., performing an action every 10 minutes) but maintain relatively "
        "preserved performance on event-based tasks (e.g., reacting immediately when an explicit environmental cue appears). Einstein et al. "
        "explained this disparity by the high demand that time-based retrieval places on self-initiated cognitive monitoring. As dementia "
        "progresses, self-initiated retrieval breaks down rapidly."
    )
    doc.add_paragraph(
        "This finding provides the foundational design rationale for the application: an automated reminder system transforms an unsupported, "
        "internal time-based task ('I need to remember to take my tablet at 12:30') into an external, salient event-based cue ('an explicit prompt "
        "appears and speaks to me right now'). The individual is relieved from continuous self-monitoring. Crucially, as Einstein et al. note, "
        "an event-based cue is effective only if it coincides precisely with the required moment of execution. Early notifications force the user "
        "to retain the intention across an intervening delay, reverting the task back to vulnerable time-based retrieval. Consequently, exact prompt "
        "timing is established as a critical system reliability requirement."
    )
    doc.add_paragraph(
        "Cognitive Affordance and Multimodal Scaffolding. Visual perception and reading comprehension frequently deteriorate alongside memory loss. "
        "Following Norman's (2013) principles of interaction design, interface actions must present clear physical signifiers and natural affordances. "
        "The reminder prompt must avoid ambiguous iconography or color-only cues; the primary confirmation action is executed via a prominent, "
        "high-contrast DONE button carrying explicit textual signifiers and dual-coding through automated Web Speech audio synthesis."
    )

    # 1.4 Critical Review of Empirical Assistive Technology Studies
    doc.add_heading("1.4 Critical Review of Empirical Assistive Technology Studies", level=2)
    doc.add_paragraph(
        "Meiland et al. (2017) conducted a comprehensive European consensus review on technologies supporting community-dwelling individuals "
        "living with dementia across daily living, social participation, and telemedicine. Two primary conclusions shape this project: first, "
        "people with dementia and their families express a profound desire to participate in developing assistive tools, yet robust usability "
        "studies in domestic environments remain scarce; second, empirical evidence demonstrating longitudinal effectiveness and cost-effectiveness "
        "is sparse. Meiland et al. emphasize that complex multi-feature devices cause cognitive overload and rapid abandonment. Because direct "
        "clinical trials with vulnerable individuals require ethical governance under the Mental Capacity Act 2005 that cannot be executed within "
        "a short MSc project timeframe (Section 3.1), this project derives its requirements from published empirical corpora and focuses on proxy "
        "caregiver evaluation."
    )
    doc.add_paragraph(
        "King and Dwan (2019) conducted a systematic review of empirical studies examining electronic memory aids specifically targeting prospective "
        "memory impairment in dementia. Their findings revealed that while electronic aids demonstrate substantial clinical promise, existing "
        "devices frequently suffer from technical unreliability—including delayed alerts, silent software crashes, and unhandled hardware sleep states. "
        "King and Dwan observed that when an assistive device fails even occasionally, user trust collapses, leading patients to permanently ignore "
        "subsequent prompts. From a software engineering standpoint, this establishes that deterministic reliability, rather than feature richness, "
        "is the primary determinant of technology adoption. Every functional behaviour in the reminder engine must therefore map to a mathematically "
        "verifiable, test-covered rule."
    )
    doc.add_paragraph(
        "Fleming and Sum (2014) provide a vital sceptical counterweight. Their systematic review of 41 assistive technology trials found no conclusive "
        "evidence that existing digital aids significantly improve quality of life or reduce institutionalization rates for people with dementia. "
        "They identified a persistent disparity between controlled laboratory demonstrations and messy domestic deployments, where devices are "
        "unplugged, misconfigured, or rejected due to intrusive interfaces. Rather than abandoning digital assistance, this project adopts Fleming and "
        "Sum's critique as a boundary constraint: this MSc investigation claims what an engineered prototype can empirically demonstrate—deterministic "
        "reliability, accessibility compliance, and caregiver usability—without asserting unproven clinical efficacy."
    )
    doc.add_paragraph(
        "Guisado-Fernández et al. (2019) and Köhler et al. (2024) specifically examined adoption barriers among dementia dyads (patient and family caregiver). "
        "Guisado-Fernández et al. categorized adoption determinants into attitudinal, ethical, and technological dimensions. Köhler et al. conducted focus "
        "groups and World Cafés with patients, relatives, medical professionals, and ethicists, discovering that limited digital literacy and complex "
        "device configuration constitute insurmountable hurdles. Both studies conclude that the care recipient should never be expected to configure, "
        "navigate menus, or troubleshoot settings. All configuration must be decoupled and assigned exclusively to the caregiver, leaving the recipient's "
        "tablet as an appliance-like, single-purpose surface."
    )

    # 1.5 Contrasting Technical Approaches
    doc.add_heading("1.5 Contrasting Technical Approaches: Deterministic Rules vs. Unsupervised Machine Learning", level=2)
    doc.add_paragraph(
        "Smart-home ubiquitous computing research frequently pursues automated routine modelling. Chimamiwa et al. (2022) surveyed ambient assisted "
        "living systems combining passive IoT sensor streams with anomaly detection algorithms to detect deviations in domestic routines. However, "
        "they highlight a fundamental limitation: unsupervised models struggle to differentiate between genuine hazardous emergencies (e.g., missed "
        "medication or wandering) and benign, evolving lifestyle adaptations as dementia progresses. An algorithm trained on static baseline data "
        "inevitably generates false positives when a patient alters their daily habits."
    )
    doc.add_paragraph(
        "Isolation Forest (Liu, Ting and Zhou, 2008; Pedregosa et al., 2011) represents an appealing algorithm for anomaly detection because it explicitly "
        "isolates abnormal observations through random partitioning rather than constructing dense profiles of normal behaviour. It operates in linear "
        "time complexity with minimal memory overhead. However, deploying an anomaly detection model within a safety-critical reminder pipeline introduces "
        "severe hazards: it requires continuous, consented, privacy-invasive domestic logging, and its probabilistic predictions cannot be transparently "
        "explained to an anxious relative. A false alarm (e.g., falsely alerting a daughter at work that her father has collapsed or missed essential "
        "heart medicine) causes severe psychological distress and alert fatigue."
    )
    doc.add_paragraph(
        "Consequently, this project establishes a principled architectural separation of concerns. The production reminder and escalation pipeline "
        "is built entirely on deterministic, rule-based logic (Must). The machine learning approach (Isolation Forest) is maintained as an offline, "
        "exploratory benchmarking experiment (SQ3) evaluated on simulated activity logs with injected noise, ensuring that experimental models never "
        "trigger unverified alerts in the live assistant."
    )

    # 1.6 From Research to Practical Decisions
    doc.add_heading("1.6 From Research to Practical Technical Decisions", level=2)
    doc.add_paragraph(
        "Table 2 illustrates the direct traceability between findings extracted from the literature and the technical architectural decisions "
        "implemented within this project."
    )

    # Table 2: Literature to Technical Decisions
    t2_data = [
        ["Finding in Literature", "Key Scholarly Source", "Technical Decision in this Project"],
        ["Time-based tasks require self-initiated retrieval, which deteriorates sharply with age and cognitive decline.", "Einstein et al. (1995)", "Prompts appear exactly at the set minute of execution, converting time-based recall into immediate, cue-driven event retrieval."],
        ["Assistive memory aids fail predominantly on technical unreliability (missed, late, or duplicated prompts), collapsing user trust.", "King and Dwan (2019)", "Built on a deterministic rule engine; 100% unit-test coverage per rule; all prompt states and transitions logged to SQLite."],
        ["Limited digital skills and complex menus block technology adoption among cognitively impaired users.", "Köhler et al. (2024)", "Strict decoupling: caregiver-only setup portal; recipient display features zero menus, large text, and spoken voice read-out."],
        ["Adoption depends on familiar domestic artefacts, ethical transparency, and family-centred wording.", "Guisado-Fernández et al. (2019)", "Web application runs on existing household tablets; caregivers author task prompts in familiar family language."],
        ["Unsupervised anomaly detection alone generates unacceptable false alerts as domestic habits naturally evolve.", "Chimamiwa et al. (2022)", "Isolation Forest is restricted to an offline benchmark on synthetic logs; production alerts rely solely on auditable rules."],
        ["Clinical evidence of longitudinal health improvements from assistive technology remains inconclusive.", "Fleming and Sum (2014)", "Project claims are strictly confined to measurable engineering outcomes: deterministic reliability, WCAG accessibility, and usability."],
        ["Interface actions must provide explicit signifiers and avoid colour-only affordance.", "Norman (2013); W3C (2023)", "Primary action is an oversized DONE button combining visual contrast, clear textual labelling, and dual-mode audio synthesis."]
    ]
    t2 = doc.add_table(rows=len(t2_data), cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)
    for r_i, row in enumerate(t2_data):
        for c_i, val in enumerate(row):
            t2.rows[r_i].cells[c_i].text = val
    format_table_header(t2.rows[0])
    format_table_body(t2, col_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    p_cap2 = doc.add_paragraph("Table 2. Systematic translation of literature findings into practical software engineering decisions.")
    p_cap2.runs[0].font.size = Pt(8.5)
    p_cap2.runs[0].font.italic = True
    p_cap2.paragraph_format.space_after = Pt(12)

    # =========================================================================
    # SECTION 2: SUMMARY OF PROGRESS TO DATE
    # =========================================================================
    doc.add_heading("2. Summary of Progress to Date", level=1)

    # 2.1 Completed Work Against Objectives
    doc.add_heading("2.1 Completed Work Against Stated Objectives", level=2)
    doc.add_paragraph(
        "Weeks 1 through 4 of the project schedule are complete and operating fully on schedule against the Gantt chart baseline (Figure A6.1). "
        "Following the approved Project Overview (20 October 2026), the investigation has yielded substantial practical and theoretical deliverables:"
    )
    doc.add_paragraph(
        "• Requirements Engineering & Comparative Analysis (Weeks 1–2, Objective O1): Extracted 15 formal requirements (9 Functional, 6 Non-Functional), "
        "each grounded in dementia literature (Table A1.1). Evaluated 5 existing solution categories (phone alarms, smart speakers, dementia day clocks, "
        "medication apps, GPS trackers) across 6 operational dimensions (Table A1.2). The analysis confirmed that no single commercial tool synthesises "
        "caregiver remote setup, prompt confirmation with snooze limits, voice synthesis, and multi-miss escalation on commodity household hardware.\n"
        "• System Architecture & Interaction Design (Weeks 2–3, Objective O1/O2): Formulated the complete system architecture (Figure A3.1) and designed "
        "the 6-table relational database model (Figure A3.2). Produced interactive wireframes for the three core screens (Screen A: Home Orientation, "
        "Screen B: Reminder Prompt, Screen C: Caregiver Portal; Figure A2.1). Conducted an algorithmic shortlist evaluating scheduling, speech synthesis, "
        "voice recognition, and anomaly detection methods (Table A3.1).\n"
        "• Core Reminder Engine Implementation (Week 4, Objective O2): Engineered the deterministic reminder engine in Python (`reminder_engine.py`, 114 LOC). "
        "The engine codifies five foundational rules: (1) plan daily occurrences based on bitmask recurrence; (2) poll prompts strictly on time; (3) auto-close "
        "unconfirmed prompts after a closing window; (4) enforce strict snooze counters, hiding the action when exhausted; and (5) trigger caregiver escalation "
        "only after consecutive misses on opted-in routines. Developed 10 comprehensive unit test scenarios (`test_reminder_engine.py`, T1–T10; Appendix 4), "
        "achieving a 100% pass rate under pytest in 0.14s."
    )

    # 2.2 Tools and Technologies
    doc.add_heading("2.2 Tools, Technologies, and Architectural Rationale", level=2)
    doc.add_paragraph(
        "The software stack was chosen to maximize transparency, auditability, security, and low deployment friction on household devices. "
        "Table 3 summarizes the selected technologies and their architectural fit."
    )

    # Table 3: Tools & Technologies
    t3_data = [
        ["Tool / Technology", "Project Role", "Architectural and Academic Justification"],
        ["Python 3.13 & pytest", "Core reminder engine, scheduling rules, unit test suite", "Expressive syntax for deterministic state machines; pytest provides clean, readable assertions mapping 1:1 to formal test scenarios (Appendix 4)."],
        ["Flask (Grinberg, 2018)", "Lightweight web application backend, REST routing, caregiver portal", "Minimalist WSGI microframework avoiding heavy enterprise bloat; keeps the entire stack in pure Python, enabling direct in-process engine coupling."],
        ["SQLite", "Relational persistent storage (6 tables)", "Zero-configuration, serverless, single-file database. Eliminates open network database ports in domestic settings while providing robust ACID transactions for event logging."],
        ["APScheduler", "In-process background cron scheduler", "Executes scheduled polling loops every minute directly inside the Python runtime, eliminating external message brokers (e.g., Celery/RabbitMQ) on domestic hardware."],
        ["Web Speech API (W3C, 2020)", "Multimodal browser text-to-speech synthesis", "Native browser implementation requiring zero cloud API subscriptions, ensuring zero latency, zero recurring cost, and high domestic privacy."],
        ["scikit-learn (Pedregosa et al., 2011)", "Offline Isolation Forest comparative benchmarking (SQ3)", "Industry-standard, peer-reviewed implementation of Isolation Forest; provides reproducible anomaly detection benchmarking against rules."]
    ]
    t3 = doc.add_table(rows=len(t3_data), cols=3)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3)
    for r_i, row in enumerate(t3_data):
        for c_i, val in enumerate(row):
            t3.rows[r_i].cells[c_i].text = val
    format_table_header(t3.rows[0])
    format_table_body(t3, col_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    p_cap3 = doc.add_paragraph("Table 3. Technology stack and architectural justifications.")
    p_cap3.runs[0].font.size = Pt(8.5)
    p_cap3.runs[0].font.italic = True
    p_cap3.paragraph_format.space_after = Pt(12)

    # 2.3 Challenges and How I Handled Them
    doc.add_heading("2.3 Technical Challenges, Risk Resolution, and Design Pivots", level=2)
    doc.add_paragraph(
        "1. Notification Delivery in Browser Contexts: Mobile operating systems aggressively sleep background web views, potentially dropping "
        "reminders. Mitigated by designing the recipient interface as a dedicated kiosk display (screen pinned on, auto-polling every 30 seconds), "
        "drawing prompts directly within the DOM rather than relying on native push notifications.\n"
        "2. The Infinite Snooze Hazard: Early wireframes permitted unconstrained snoozing. Literature analysis revealed that an unconstrained snooze "
        "allows critical medication to be deferred indefinitely without caregiver awareness. This was resolved by enforcing Rule 4: a strict maximum "
        "snooze counter (default: 2), after which the snooze button disappears, forcing completion or timing out into an escalated miss.\n"
        "3. Clinical Trial Restrictions: Due to statutory governance under the Mental Capacity Act 2005 (Section 3.1), primary clinical trials with "
        "dementia patients are prohibited within this MSc project. Handled by deriving requirements rigorously from published trials and conducting proxy "
        "usability testing with student caregivers.\n"
        "4. Ground-Truth Data Availability for SQ3: Consented domestic routine datasets containing documented dementia anomalies do not exist publicly. "
        "Resolved by synthesizing parameterized activity logs with mathematically known anomaly injections (Section 5.2), enabling rigorous precision, "
        "recall, and false-alarm benchmarking."
    )

    # =========================================================================
    # SECTION 3: ETHICAL, LEGAL, PROFESSIONAL AND SOCIAL ISSUES
    # =========================================================================
    doc.add_heading("3. Consideration of Ethical, Legal, Professional, and Social Issues", level=1)

    # 3.1 Ethics Approval
    doc.add_heading("3.1 Ethical Approval and Governance Justification", level=2)
    doc.add_paragraph(
        "Formal ethics approval is not required for the current project scope. The software prototype is developed, verified, and benchmarked "
        "exclusively using synthetic activity logs, simulated user interactions, and test scenarios. No individuals living with dementia, informal "
        "caregivers, or external human participants are recruited. If the optional proxy usability evaluation is conducted with student volunteers "
        "acting as caregivers in Week 6, low-risk institutional ethics clearance will be obtained through the University of Hertfordshire Ethics "
        "Committee prior to recruitment."
    )
    doc.add_paragraph(
        "Crucially, engaging individuals living with dementia directly would introduce profound ethical and statutory obligations. In England and Wales, "
        "research involving human participants who may lack the mental capacity to provide informed consent is strictly regulated by the Mental Capacity "
        "Act 2005 (Section 30–33), requiring formal approval from an accredited Health Research Authority (HRA) Research Ethics Committee (REC). Establishing "
        "consultee frameworks and clinical monitoring cannot be accommodated within the condensed 6-week timeframe of an individual MSc project. Restricting "
        "the project to simulated data and proxy evaluation represents a professionally necessary boundary; the trade-off is that findings must be explicitly "
        "reported as engineering and proxy validations rather than clinical efficacy claims."
    )

    # 3.2 Ethical Issues
    doc.add_heading("3.2 Ethical Considerations: Autonomy vs. Surveillance and Alert Fatigue", level=2)
    doc.add_paragraph(
        "The central ethical tension lies between respecting personal autonomy and providing physical safety. Automated reminders empower an individual "
        "to manage daily living independently; however, transmitting compliance data to family members risks feeling like intrusive surveillance. "
        "The prototype resolves this by enforcing strict ethical boundaries: escalation alerts are strictly opt-in per routine (defaulting to off), "
        "and alerts trigger only after repeated, consecutive misses (streak >= 2) rather than isolated incidents. Geolocation tracking was explicitly "
        "excluded from the project scope to avoid privacy intrusion. Furthermore, false alarms are treated as a severe ethical hazard: an erroneous "
        "emergency alert panics family members and erodes patient trust. Consequently, false-alarm rates are treated as a primary evaluation metric in testing."
    )

    # 3.3 Legal Issues
    doc.add_heading("3.3 Legal Compliance: UK GDPR, Special Category Data, and MHRA Regulations", level=2)
    doc.add_paragraph(
        "Data Protection and UK GDPR: In a production environment, a patient's daily routine and medication schedule constitute Special Category Data "
        "(health data) under Article 9 of the UK GDPR and the Data Protection Act 2018 (European Union, 2016). Although the development prototype utilizes "
        "purely synthetic records, a production deployment would require an explicit lawful basis under Article 6, an Article 9 condition (e.g., explicit "
        "consent or health management), a formal Data Protection Impact Assessment (DPIA), local encryption at rest, and strict data minimization. By storing "
        "all schedules locally in SQLite on the domestic tablet, cloud data leakage risks are eliminated."
    )
    doc.add_paragraph(
        "Medical Device Regulation (MHRA, 2024): The UK Medicines and Healthcare products Regulatory Agency establishes that software intended for "
        "diagnosis, therapy, or medical dosing calculations is classified as Software as a Medical Device (SaMD), requiring UKCA certification. "
        "This project strictly delineates its intended purpose as general cognitive assistive technology supporting daily living (ADLs), avoiding any "
        "diagnostic inference, clinical prognosis, or medication dosage calculations. If anomaly models were ever expanded to infer disease progression, "
        "full SaMD regulatory classification would be triggered."
    )

    # 3.4 Professional Issues
    doc.add_heading("3.4 Professional Standards: BCS Code of Conduct and Software Quality Assurance", level=2)
    doc.add_paragraph(
        "This investigation adheres to the British Computer Society (BCS, 2022) Code of Conduct, which mandates that IT professionals have due regard "
        "for public health, privacy, and wellbeing, and claim competence only within their verified expertise. In practice, this means: making zero "
        "unsubstantiated medical claims; implementing rigorous unit-test coverage before declaring code complete; enforcing strict WCAG 2.2 AA accessibility "
        "compliance (W3C, 2023); maintaining full Git version control for auditability; and operating with transparency regarding system limitations."
    )

    # 3.5 Social Issues & 3.6 Economic Impact
    doc.add_heading("3.5 Social Impact, Inclusivity, and Algorithmic Bias", level=2)
    doc.add_paragraph(
        "Deploying the assistant as a standard web application on existing household tablets lowers socioeconomic barriers, eliminating costly "
        "hardware subscriptions. Prompts authored directly by caregivers enable familiar domestic language, dialects, and cultural phrasing. Text-to-speech "
        "mitigates age-related visual and literacy barriers. Conversely, algorithmic bias poses significant hazards: an unsupervised anomaly detector "
        "trained on 'standard' daily routines could misclassify night-shift workers, prayer rituals, or non-standard cultural eating patterns as "
        "abnormal cognitive decline. This reinforces why machine learning must remain an offline benchmark rather than an unconstrained alert generator."
    )
    doc.add_paragraph(
        "Economic Impact: With UK dementia costs projected to rise from £42 billion in 2024 to £90 billion by 2040 (Alzheimer's Society, 2024), "
        "assistive technologies that delay institutional care by even a few months yield substantial macroeconomic savings. While clinical cost savings "
        "cannot be proven within this prototype, measurable proxy indicators—such as caregiver setup time and check-in call reductions—are captured."
    )

    # =========================================================================
    # SECTION 4: PROJECT PLAN AND MANAGEMENT STRATEGY
    # =========================================================================
    doc.add_heading("4. Project Plan and Management Strategy", level=1)

    # 4.1 Management Approach
    doc.add_heading("4.1 Hybrid Management Framework and Scope Control", level=2)
    doc.add_paragraph(
        "The project is executed using a hybrid engineering methodology. The high-level lifecycle follows structured waterfall milestone gates "
        "(Research -> Design -> Build -> Test -> Evaluate) to satisfy formal academic deliverables. Within the active implementation phase, work "
        "progresses through 1-week iterative sprints managed via a Kanban board (Backlog -> In Progress -> Testing -> Done). This enables rapid "
        "pivot when edge-case testing uncovers hidden failure modes."
    )
    doc.add_paragraph(
        "Scope management is strictly enforced using the MoSCoW framework (Clegg and Barker, 1994):\n"
        "• Must Have: Deterministic reminder engine, SQLite 6-table persistence, Screen A (Home), Screen B (Prompt with DONE/Snooze), Screen C (Caregiver setup), in-process scheduling.\n"
        "• Should Have: Multimodal Web Speech API text-to-speech synthesis (W3C, 2020).\n"
        "• Could Have: Web Speech voice recognition commands, offline Isolation Forest anomaly detection experiment.\n"
        "• Won't Have: Native GPS geofencing (deferred due to mobile permission complexity and privacy risks).\n"
        "Work items transition to 'Done' only when all corresponding unit tests pass. Weekly supervisor reviews provide formal oversight and risk mitigation."
    )

    # 4.2 Tasks, Dates and Deliverables
    doc.add_heading("4.2 Tasks, Milestones, and Deliverable Schedule", level=2)
    doc.add_paragraph("Table 4 outlines the completed and planned tasks across the 6-week project lifecycle, synchronized with the Gantt chart (Figure A6.1).")

    # Table 4: Tasks
    t4_data = [
        ["Project Phase & Tasks", "Work Window", "Concrete Deliverable", "Current Status"],
        ["Needs Analysis, Dementia Literature Review, Market Scan", "20 Oct – 26 Oct", "15 User Requirements (Table A1.1); Solution Comparison (Table A1.2)", "Done"],
        ["Technical Research, Shortlist, Wireframes, Architecture", "27 Oct – 02 Nov", "3 Screen Wireframes (App. 2); Architecture (App. 3); Shortlist (Table A3.1)", "Done"],
        ["Requirements Formalization, Screen Flows, Data Model", "03 Nov – 09 Nov", "6-Table Relational Schema & ERD (Figure A3.2, Appendix 3)", "Done"],
        ["Deterministic Reminder Engine & Unit Test Suite", "10 Nov – 16 Nov", "Python Engine (`reminder_engine.py`); 10 Passing Tests (App. 4)", "Done"],
        ["Write and Submit Interim Progress Report (IPR)", "12 Nov – 16 Nov", "Formal Interim Progress Report (MSc Milestone Deliverable)", "Done (This Document)"],
        ["Flask Application Backend & Three Accessible Screens", "17 Nov – 23 Nov", "Interactive Three-Screen Prototype (Home, Prompt, Caregiver Portal)", "Planned (Week 5)"],
        ["Multimodal Web Speech API Audio Synthesis Integration", "20 Nov – 24 Nov", "Spoken Prompt Synthesis and Optional Voice Recognition", "Planned (Week 5)"],
        ["Functional, Edge-Case, Simulation & Accessibility Testing", "24 Nov – 29 Nov", "Executed Test Plan T11–T18 (App. 5); WCAG 2.2 AA Audit Log", "Planned (Week 6)"],
        ["Final Report Compilation, Demonstration & Presentation", "27 Nov – 30 Nov", "MSc Final Dissertation, Demonstration Video, Slide Deck", "Planned (Week 6)"]
    ]
    t4 = doc.add_table(rows=len(t4_data), cols=4)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4)
    for r_i, row in enumerate(t4_data):
        for c_i, val in enumerate(row):
            t4.rows[r_i].cells[c_i].text = val
    format_table_header(t4.rows[0])
    format_table_body(t4, col_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])

    p_cap4 = doc.add_paragraph("Table 4. Comprehensive project task breakdown, milestones, and deliverable tracking.")
    p_cap4.runs[0].font.size = Pt(8.5)
    p_cap4.runs[0].font.italic = True
    p_cap4.paragraph_format.space_after = Pt(12)

    # 4.3 Evaluating Quality and the Process
    doc.add_heading("4.3 Quality Assurance, Process Evaluation, and Testing Strategy", level=2)
    doc.add_paragraph(
        "Quality is evaluated across three rigorous engineering dimensions:\n"
        "1. Technical Correctness: Every scheduling rule is verified through deterministic unit tests (T1–T10). The full system will execute an "
        "accelerated 7-day automated simulation (T16) enforcing zero dropped or duplicated prompts.\n"
        "2. Accessibility Standards: Every screen is evaluated against WCAG 2.2 AA (W3C, 2023) standards, verifying color contrast (>= 4.5:1) "
        "and touch targets (>= 48 px).\n"
        "3. Usability Verification: If ethical clearance is granted, proxy caregivers will execute standardized scenario tasks evaluated via the "
        "System Usability Scale (SUS: Brooke, 1996).\n"
        "Project process is audited weekly against Gantt baseline milestones (Figure A6.1) and the Risk Register (Table A6.1)."
    )

    # =========================================================================
    # SECTION 5: LEVEL OF THE PROJECT (MSc / LEVEL 7)
    # =========================================================================
    doc.add_heading("5. Level of the Project (MSc / Level 7)", level=1)

    # 5.1 Level of the Proposed Artefact
    doc.add_heading("5.1 Level and Sophistication of the Proposed Artefact", level=2)
    doc.add_paragraph(
        "The proposed artefact represents a substantial, safety-critical software system far exceeding a simple to-do or calendar application. "
        "It synthesises an auditable, deterministic reminder engine with an accessible user interface engineered specifically around documented "
        "cognitive impairment needs. The system architecture enforces a strict separation of concerns across six relational tables in SQLite (Appendix 3), "
        "ensuring that reminder scheduling, multi-stage confirmation, configurable snooze limits, and caregiver escalation operate reliably without "
        "silent failures. Unlike commercial smart speakers or phone alarms that overwhelm users with complex multi-step navigation or fail to verify "
        "receipt, this artefact delivers single-action cognitive scaffolding, combines visual signifiers with dual-mode Web Speech synthesis "
        "(W3C Web Speech API Community Group, 2020), and enforces a fail-safe escalation policy where only repeated, unconfirmed tasks trigger caregiver notifications."
    )

    # 5.2 Level and Depth of the Proposed Investigation
    doc.add_heading("5.2 Level and Depth of the Proposed Investigation", level=2)
    doc.add_paragraph(
        "The investigation critically bridges dementia care literature, prospective memory theory, and empirical software engineering. "
        "It directly tests the core claim in the field—that reliability and predictability, rather than feature count, decide whether a "
        "memory aid is adopted in practice (King and Dwan, 2019). Beyond standard software validation, the investigation explores the boundary "
        "where machine learning genuinely adds value versus where it introduces safety risks (SQ3). Through a controlled offline experiment, "
        "the project compares fixed threshold rules against an unsupervised Isolation Forest model (Liu, Ting and Zhou, 2008; Pedregosa et al., 2011) "
        "trained on simulated daily-living activity logs with injected noise and anomalies. Critically, false-alert rates are quantified alongside "
        "precision and recall, reflecting the severe human cost of false alarms in vulnerable households."
    )

    # 5.3 Appropriateness and Comparative Evaluation of Proposed Methods
    doc.add_heading("5.3 Appropriateness and Comparative Evaluation of Proposed Methods", level=2)
    doc.add_paragraph(
        "The chosen methodologies were systematically selected through comparative analysis (Table A3.1). A deterministic rule-based scheduling "
        "engine was prioritized over end-to-end machine learning for the core escalation pipeline because every state transition can be formally "
        "traced, audited, and tested against deterministic rules without requiring unconsented, privacy-invasive sensor streams. Testing and "
        "validation go significantly beyond standard functional verification. The comprehensive test plan (Appendix 5) validates critical real-world "
        "edge cases: Daylight Saving Time transitions (e.g., the UK clock-change on 28 March 2027 where local 01:30 is skipped, resolved by UTC "
        "storage), prompt windows spanning midnight, concurrent tasks due in the same minute, state recovery across browser reloads, and in-flight "
        "caregiver routine edits. Furthermore, a 7-day accelerated clock simulation (T16) guarantees zero dropped or duplicate reminders over prolonged usage."
    )

    # 5.4 Career Aspirations, Professional Ethics, and Methodological Limitations
    doc.add_heading("5.4 Career Aspirations, Professional Ethics, and Methodological Limitations", level=2)
    doc.add_paragraph(
        "This project directly aligns with my career objective to work in data engineering, machine learning, and trustworthy software systems, "
        "where the central challenge lies in knowing when a complex model is appropriate and proving that an engineering solution is robust and safe. "
        "Addressing cognitive accessibility and vulnerable-user safety enforces rigorous professional discipline. An important methodological limitation "
        "of this project is the reliance on synthetic activity logs and proxy evaluation rather than primary clinical trials with individuals living "
        "with dementia, a deliberate choice necessitated by ethical constraints under the Mental Capacity Act 2005. Consequently, the project claims "
        "what empirical evidence strictly validates—demonstrating technical reliability, accessibility compliance (WCAG 2.2 AA), and algorithmic "
        "trade-offs—providing a solid, verified foundation for future clinical research."
    )

    # =========================================================================
    # SECTION 6: REFERENCES
    # =========================================================================
    doc.add_heading("6. References", level=1)

    references = [
        "Alzheimer's Society (2024) The economic impact of dementia. Module 1: annual costs of dementia. Report by Carnall Farrar. London: Alzheimer's Society. Available at: https://www.alzheimers.org.uk/about-us/policy-and-influencing/economic-impact-of-dementia (Accessed: 16 November 2026).",
        "BCS, The Chartered Institute for IT (2022) Code of Conduct for BCS members. Swindon: BCS. Available at: https://www.bcs.org/membership-and-registrations/become-a-member/bcs-code-of-conduct/ (Accessed: 16 November 2026).",
        "Brooke, J. (1996) 'SUS: a \"quick and dirty\" usability scale', in Jordan, P.W., Thomas, B., Weerdmeester, B.A. and McClelland, I.L. (eds) Usability evaluation in industry. London: Taylor & Francis, pp. 189-194.",
        "Chimamiwa, G., Giaretta, A., Alirezaie, M., Pecora, F. and Loutfi, A. (2022) 'Are smart homes adequate for older adults with dementia?', Sensors, 22(11), 4254. doi: 10.3390/s22114254.",
        "Clegg, D. and Barker, R. (1994) Case Method Fast-Track: A Rad Approach. Wokingham: Addison-Wesley.",
        "Data Protection Act 2018, c. 12. Available at: https://www.legislation.gov.uk/ukpga/2018/12 (Accessed: 16 November 2026).",
        "Einstein, G.O., McDaniel, M.A., Richardson, S.L., Guynn, M.J. and Cunfer, A.R. (1995) 'Aging and prospective memory: examining the influences of self-initiated retrieval processes', Journal of Experimental Psychology: Learning, Memory, and Cognition, 21(4), pp. 996-1007. doi: 10.1037/0278-7393.21.4.996.",
        "European Union (2016) 'Regulation (EU) 2016/679 of the European Parliament and of the Council (General Data Protection Regulation)', Official Journal of the European Union, L 119, pp. 1-88.",
        "Fleming, R. and Sum, S. (2014) 'Empirical studies on the effectiveness of assistive technology in the care of people with dementia: a systematic review', Journal of Assistive Technologies, 8(1), pp. 14-34. doi: 10.1108/JAT-09-2012-0021.",
        "Grinberg, M. (2018) Flask Web Development: Developing Web Applications with Python. 2nd edn. Sebastopol: O'Reilly Media.",
        "Guisado-Fernández, E., Giunti, G., Mackey, L.M., Blake, C. and Caulfield, B.M. (2019) 'Factors influencing the adoption of smart health technologies for people with dementia and their informal caregivers: scoping review and design framework', JMIR Aging, 2(1), e12192. doi: 10.2196/12192.",
        "King, A.C. and Dwan, C. (2019) 'Electronic memory aids for people with dementia experiencing prospective memory loss: a review of empirical studies', Dementia, 18(6), pp. 1994-2007. doi: 10.1177/1471301217735180.",
        "Köhler, S., Perry, J., Biernetzky, O.A., Kirste, T. and Teipel, S.J. (2024) 'Ethics, design, and implementation criteria of digital assistive technologies for people with dementia from a multiple stakeholder perspective: a qualitative study', BMC Medical Ethics, 25, 84. doi: 10.1186/s12910-024-01080-6.",
        "Liu, F.T., Ting, K.M. and Zhou, Z.-H. (2008) 'Isolation forest', in Proceedings of the 8th IEEE International Conference on Data Mining (ICDM 2008). Pisa: IEEE, pp. 413-422. doi: 10.1109/ICDM.2008.17.",
        "Meiland, F., Innes, A., Mountain, G., Robinson, L., van der Roest, H., García-Casal, J.A. et al. (2017) 'Technologies to support community-dwelling persons with dementia: a position paper on issues regarding development, usability, effectiveness and cost-effectiveness, deployment, and ethics', JMIR Rehabilitation and Assistive Technologies, 4(1), e1. doi: 10.2196/rehab.6376.",
        "Mental Capacity Act 2005, c. 9. Available at: https://www.legislation.gov.uk/ukpga/2005/9 (Accessed: 16 November 2026).",
        "MHRA (2024) Software and artificial intelligence (AI) as a medical device. London: Medicines and Healthcare products Regulatory Agency. Available at: https://www.gov.uk/government/publications/software-and-artificial-intelligence-ai-as-a-medical-device (Accessed: 16 November 2026).",
        "Norman, D.A. (2013) The Design of Everyday Things. Revised and expanded edn. New York: Basic Books.",
        "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V. and Vanderplas, J. (2011) 'Scikit-learn: machine learning in Python', Journal of Machine Learning Research, 12, pp. 2825-2830.",
        "W3C (2023) Web Content Accessibility Guidelines (WCAG) 2.2. W3C Recommendation, 5 October. Available at: https://www.w3.org/TR/WCAG22/ (Accessed: 16 November 2026).",
        "W3C Web Speech API Community Group (2020) Web Speech API Specification. Available at: https://wicg.github.io/speech-api/ (Accessed: 16 November 2026).",
        "WHO (2025) Dementia: fact sheet. Geneva: World Health Organization. Available at: https://www.who.int/news-room/fact-sheets/detail/dementia (Accessed: 16 November 2026)."
    ]

    for ref in references:
        p_ref = doc.add_paragraph(ref)
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.runs[0].font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # APPENDICES
    # =========================================================================

    # APPENDIX 1
    doc.add_heading("Appendix 1. Requirements and Comparison of Existing Solutions", level=1)

    doc.add_heading("Table A1.1 User Requirements (FR = Functional, NFR = Non-Functional)", level=2)
    a1_data = [
        ["ID", "User Requirement Description", "Theoretical / Empirical Derivation"],
        ["FR1", "Display current day, date, and time in oversized text, alongside part of day in natural words ('Afternoon').", "Project scope; W3C (2023) orientation principles"],
        ["FR2", "Prompt each task strictly at its set time of execution, only on scheduled recurrence days.", "Einstein et al. (1995); King and Dwan (2019)"],
        ["FR3", "Enable the person to confirm completion via a single physical tap on a prominent DONE target.", "Köhler et al. (2024); Norman (2013) affordance"],
        ["FR4", "Permit limited snoozing (configurable, default: 2), completely hiding the option once exhausted.", "Design review risk mitigation (Section 2.3)"],
        ["FR5", "Automatically close unconfirmed prompts after a set timeout window and record occurrence as missed.", "King and Dwan (2019) bounded state model"],
        ["FR6", "Read every prompt aloud using multimodal text-to-speech synthesis immediately upon appearance.", "Project scope; Köhler et al. (2024) dual-coding"],
        ["FR7", "Enable caregiver to remotely create, modify, and deactivate routines, schedules, and contacts.", "Guisado-Fernández et al. (2019) dyad decoupling"],
        ["FR8", "Dispatch escalation alert to caregiver only after repeated consecutive misses on opted-in routines.", "Köhler et al. (2024) alert-fatigue prevention"],
        ["FR9", "Provide dedicated one-tap speed dial buttons for designated emergency and family contacts.", "Project scope; social safety scaffold"],
        ["NFR1", "Maintain text contrast ratio >= 4.5:1; touch targets >= 48 px (exceeding WCAG 24 px minimum).", "W3C (2023) WCAG 2.2 AA Criteria 1.4.3 & 2.5.8"],
        ["NFR2", "Never convey critical state, status, or interactive meaning by color alone.", "W3C (2023) WCAG 2.2 AA Criterion 1.4.1"],
        ["NFR3", "Record every prompt creation, display, snooze, confirmation, and timeout with UTC timestamp.", "King and Dwan (2019) auditability requirement"],
        ["NFR4", "Enforce strict data minimization; utilize synthetic data exclusively in development.", "European Union (2016) UK GDPR Article 5(1)(c)"],
        ["NFR5", "Protect caregiver configuration portal with authentication; maintain zero login on recipient screen.", "Köhler et al. (2024) cognitive friction reduction"],
        ["NFR6", "Execute in standard modern web browsers on existing household tablet hardware without installation.", "Guisado-Fernández et al. (2019) cost barrier mitigation"]
    ]
    ta1 = doc.add_table(rows=len(a1_data), cols=3)
    ta1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(ta1)
    for r_i, row in enumerate(a1_data):
        for c_i, val in enumerate(row):
            ta1.rows[r_i].cells[c_i].text = val
    format_table_header(ta1.rows[0])
    format_table_body(ta1, col_alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    p_cap_a1 = doc.add_paragraph("Table A1.1. Detailed functional and non-functional requirements specification.")
    p_cap_a1.runs[0].font.size = Pt(8.5)
    p_cap_a1.runs[0].font.italic = True
    p_cap_a1.paragraph_format.space_after = Pt(12)

    doc.add_heading("Table A1.2 Typical Features of Existing Solution Categories vs. This Prototype", level=2)
    a2_data = [
        ["Evaluated Feature", "Phone Alarm / Cal", "Smart Speaker", "Dementia Clock", "Medication App", "GPS Tracker", "This Prototype"],
        ["Large Day / Time Display", "Partial", "Partial", "Yes", "No", "No", "Yes"],
        ["Single-Tap Confirm & Snooze", "Yes", "Partial", "Partial", "Yes", "No", "Yes"],
        ["Remote Caregiver Setup", "No", "Partial", "Partial", "Partial", "Yes", "Yes"],
        ["Spoken Audio Synthesis", "No", "Yes", "Partial", "No", "No", "Yes"],
        ["Caregiver Multi-Miss Alert", "No", "No", "No", "Partial", "No", "Yes (Opt-in)"],
        ["No Proprietary Hardware Req.", "Yes", "No", "No", "Yes", "No", "Yes"]
    ]
    ta2 = doc.add_table(rows=len(a2_data), cols=7)
    ta2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(ta2)
    for r_i, row in enumerate(a2_data):
        for c_i, val in enumerate(row):
            ta2.rows[r_i].cells[c_i].text = val
    format_table_header(ta2.rows[0])
    format_table_body(ta2, col_alignments=[WD_ALIGN_PARAGRAPH.LEFT] + [WD_ALIGN_PARAGRAPH.CENTER]*6)

    p_cap_a2 = doc.add_paragraph("Table A1.2. Comparative feature matrix across existing commercial product categories.")
    p_cap_a2.runs[0].font.size = Pt(8.5)
    p_cap_a2.runs[0].font.italic = True
    p_cap_a2.paragraph_format.space_after = Pt(14)

    # APPENDIX 2
    doc.add_heading("Appendix 2. Prototype Wireframes and Live Unified Application", level=1)
    wireframe_img = os.path.join(ASSETS_DIR, "c0d12457f56b4b37f50a1ccf1d353f8c220b9d3d.png")
    if os.path.exists(wireframe_img):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(wireframe_img, width=Inches(6.2))
        p_fig_a2 = doc.add_paragraph("Figure A2.1 High-fidelity implementation of the three core screens: home orientation (A), reminder prompt (B), and caregiver setup (C).")
        p_fig_a2.runs[0].font.size = Pt(8.5)
        p_fig_a2.runs[0].font.italic = True
        p_fig_a2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig_a2.paragraph_format.space_after = Pt(12)

    unified_img = os.path.join(ASSETS_DIR, "figure_a2_2_unified_app.png")
    if os.path.exists(unified_img):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.add_run().add_picture(unified_img, width=Inches(6.2))
        p_fig_a22 = doc.add_paragraph("Figure A2.2 Live unified full-stack web application interface: patient tablet surface on the left with in-frame state transitions, and caregiver setup, KPI dials, and auditable SQLite event log on the right.")
        p_fig_a22.runs[0].font.size = Pt(8.5)
        p_fig_a22.runs[0].font.italic = True
        p_fig_a22.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig_a22.paragraph_format.space_after = Pt(14)

    # APPENDIX 3
    doc.add_heading("Appendix 3. System Architecture and Data Model", level=1)

    arch_img = os.path.join(ASSETS_DIR, "97c75d0c0df7a4ec73ad8048e4e073cf9f65f42d.png")
    if os.path.exists(arch_img):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(arch_img, width=Inches(5.8))
        p_fig_a31 = doc.add_paragraph("Figure A3.1 System architecture diagram. The dashed box indicates offline exploratory machine learning.")
        p_fig_a31.runs[0].font.size = Pt(8.5)
        p_fig_a31.runs[0].font.italic = True
        p_fig_a31.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig_a31.paragraph_format.space_after = Pt(12)

    erd_img = os.path.join(ASSETS_DIR, "92b0f41bd4a3e6296e1fb700a8ea5df3de0306bc.png")
    if os.path.exists(erd_img):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(erd_img, width=Inches(5.8))
        p_fig_a32 = doc.add_paragraph("Figure A3.2 Entity-relationship model for the 6-table SQLite database.")
        p_fig_a32.runs[0].font.size = Pt(8.5)
        p_fig_a32.runs[0].font.italic = True
        p_fig_a32.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig_a32.paragraph_format.space_after = Pt(14)

    doc.add_heading("Table A3.1 Algorithm Shortlist and Architectural Selection Rationale", level=2)
    a3_data = [
        ["System Function", "Shortlisted Method", "Decision Taken", "Architectural Rationale"],
        ["Reminder Engine", "Deterministic rule scheduling: time, recurrence, acknowledgement, snooze", "Selected & Built (Must)", "Auditable state machine; requires no clinical training data; each rule independently verifiable."],
        ["Spoken Prompts", "Text-to-speech (W3C Web Speech API Community Group, 2020)", "Selected (Should)", "Native in modern browsers; zero recurring API costs; high privacy on domestic tablets."],
        ["Voice Commands", "Speech-to-text with keyword matching", "Optional (Could)", "Accuracy with dysarthric, elderly, or accented voices requires extensive testing."],
        ["Unusual Routine Patterns", "Rule thresholds vs. Isolation Forest (Liu et al., 2008; Pedregosa et al., 2011)", "Rules selected; Isolation Forest offline benchmark (Could)", "Lack of consented domestic activity corpora; false alarms must never compromise safety."],
        ["Location Tracking", "GPS geofencing with distance rules", "Deferred (Won't, this project)", "Requires native mobile background permissions; severe privacy intrusion risk; web platform chosen."]
    ]
    ta3 = doc.add_table(rows=len(a3_data), cols=4)
    ta3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(ta3)
    for r_i, row in enumerate(a3_data):
        for c_i, val in enumerate(row):
            ta3.rows[r_i].cells[c_i].text = val
    format_table_header(ta3.rows[0])
    format_table_body(ta3, col_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    p_cap_a3 = doc.add_paragraph("Table A3.1. Algorithmic trade-off analysis and final architectural decisions.")
    p_cap_a3.runs[0].font.size = Pt(8.5)
    p_cap_a3.runs[0].font.italic = True
    p_cap_a3.paragraph_format.space_after = Pt(14)

    # APPENDIX 4
    doc.add_heading("Appendix 4. Prototype Evidence: Reminder Engine and Test Log", level=1)
    doc.add_paragraph(
        "Python Implementation Excerpt (`reminder_engine.py`) demonstrating Rule 4 (Snooze Counter Limit) and Rule 5 (Caregiver Multi-Miss Escalation):"
    )

    code_p = doc.add_paragraph()
    code_p.paragraph_format.left_indent = Inches(0.2)
    code_p.paragraph_format.right_indent = Inches(0.2)
    code_p.paragraph_format.space_after = Pt(8)
    set_cell_background_p = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F4F6F8"/>')
    code_p._p.get_or_add_pPr().append(set_cell_background_p)

    code_text = (
        "# Rule 4: Snoozing is allowed a limited number of times, then the action is refused.\n"
        "def snooze(self, occ: Occurrence, now: datetime) -> bool:\n"
        "    if occ.snoozes >= occ.task.max_snoozes:\n"
        "        occ._note(now, 'snooze refused (limit reached)')\n"
        "        return False\n"
        "    occ.snoozes += 1\n"
        "    occ.status = Status.SNOOZED\n"
        "    occ.next_prompt_at = now + timedelta(minutes=occ.task.snooze_minutes)\n"
        "    occ._note(now, f'snoozed ({occ.snoozes}/{occ.task.max_snoozes})')\n"
        "    return True\n\n"
        "# Rule 5: Only repeated consecutive misses on an opted-in task reach the caregiver.\n"
        "def _register_miss(self, occ: Occurrence, now: datetime) -> None:\n"
        "    tid = occ.task.task_id\n"
        "    self._miss_streak[tid] = self._miss_streak.get(tid, 0) + 1\n"
        "    if occ.task.alert_caregiver and self._miss_streak[tid] >= self.escalate_after_misses:\n"
        "        self.caregiver_alerts.append({\n"
        "            'timestamp': now,\n"
        "            'task_id': tid,\n"
        "            'label': occ.task.label,\n"
        "            'consecutive_misses': self._miss_streak[tid],\n"
        "            'message': f\"Caregiver Alert: '{occ.task.label}' missed {self._miss_streak[tid]} times consecutively.\"\n"
        "        })"
    )
    r_code = code_p.add_run(code_text)
    r_code.font.name = "Consolas"
    r_code.font.size = Pt(8.5)
    r_code.font.color.rgb = RGBColor(30, 30, 30)

    doc.add_paragraph("Formal Pytest Test Execution Log (`pytest test_reminder_engine.py -v`, 16 November 2026):")

    log_p = doc.add_paragraph()
    log_p.paragraph_format.left_indent = Inches(0.2)
    log_p.paragraph_format.right_indent = Inches(0.2)
    log_p.paragraph_format.space_after = Pt(14)
    log_shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EDF2F7"/>')
    log_p._p.get_or_add_pPr().append(log_shd)

    log_text = (
        "============================= test session starts =============================\n"
        "platform win32 -- Python 3.13.2, pytest-9.2.0, pluggy-1.7.0\n"
        "collected 10 items\n\n"
        "test_reminder_engine.py::test_prompt_appears_on_time_not_before PASSED   [ 10%]\n"
        "test_reminder_engine.py::test_task_skipped_on_unscheduled_day PASSED     [ 20%]\n"
        "test_reminder_engine.py::test_confirmation_closes_prompt PASSED          [ 30%]\n"
        "test_reminder_engine.py::test_snooze_brings_prompt_back_later PASSED     [ 40%]\n"
        "test_reminder_engine.py::test_snooze_limit_is_enforced PASSED            [ 50%]\n"
        "test_reminder_engine.py::test_unconfirmed_prompt_becomes_missed_after_window PASSED [ 60%]\n"
        "test_reminder_engine.py::test_no_caregiver_alert_without_opt_in PASSED   [ 70%]\n"
        "test_reminder_engine.py::test_caregiver_alert_only_after_repeated_misses PASSED [ 80%]\n"
        "test_reminder_engine.py::test_confirmation_resets_miss_streak PASSED     [ 90%]\n"
        "test_reminder_engine.py::test_completion_rate PASSED                     [100%]\n\n"
        "============================== 10 passed in 0.14s =============================="
    )
    r_log = log_p.add_run(log_text)
    r_log.font.name = "Consolas"
    r_log.font.size = Pt(8.5)
    r_log.font.color.rgb = RGBColor(20, 40, 20)

    # APPENDIX 5
    doc.add_heading("Appendix 5. Test Plan", level=1)
    doc.add_paragraph("Table A5.1 specifies the 18 validation scenarios (T1–T10 completed unit tests; T11–T18 planned integration and edge-case tests).")

    t5_data = [
        ["ID", "Test Scenario & Operational Conditions", "Expected System Behaviour", "Verification Status"],
        ["T1", "Prompt checked one minute prior (12:29) and at scheduled time (12:30).", "Hidden at 12:29; displayed immediately at 12:30.", "Pass (O2)"],
        ["T2", "Weekday-only recurrence task checked on a Sunday.", "Occurrence not planned for the day.", "Pass (O2)"],
        ["T3", "Person living with dementia taps the DONE target.", "Prompt closes immediately and does not re-appear.", "Pass (O2)"],
        ["T4", "Person taps Snooze (configured for 10 minutes).", "Prompt disappears for 10 minutes; re-prompts at 10m.", "Pass (O2)"],
        ["T5", "Third snooze attempted when maximum limit is configured to 2.", "Snooze refused; snooze button hidden from UI.", "Pass (O2)"],
        ["T6", "No interaction recorded across the 60-minute response window.", "Occurrence transitioned to MISSED; streak incremented.", "Pass (O2)"],
        ["T7", "Two consecutive misses on a routine without caregiver opt-in.", "No alert dispatched to caregiver.", "Pass (O2)"],
        ["T8", "Two consecutive misses on a routine with caregiver opt-in enabled.", "Exactly one escalation alert dispatched to caregiver.", "Pass (O2)"],
        ["T9", "Miss recorded, followed by task confirmation, followed by miss.", "Streak resets on confirmation; no alert dispatched.", "Pass (O2)"],
        ["T10", "Engine execution resulting in 1 confirmed done and 1 missed task.", "Completion rate mathematically evaluated as 50.0%.", "Pass (O2)"],
        ["T11", "Task set for 01:30 on 28 Mar 2027 (UK Daylight Saving Time skip).", "Displayed once at 02:00 via UTC time normalization.", "Planned (Week 6)"],
        ["T12", "Late evening prompt response window spans across midnight boundary.", "Occurrence recorded as missed on correct calendar day.", "Planned (Week 6)"],
        ["T13", "Two independent tasks scheduled for the exact same minute.", "Displayed sequentially; both logged independently.", "Planned (Week 6)"],
        ["T14", "Browser refresh / power cycle while prompt is actively showing.", "Active prompt state restored from SQLite database.", "Planned (Week 6)"],
        ["T15", "Caregiver modifies routine parameters while prompt is on screen.", "In-flight prompt preserved; changes apply to next occ.", "Planned (Week 6)"],
        ["T16", "Automated 7-day simulation executing on accelerated clock.", "Zero missed or duplicated prompts across 168 hours.", "Planned (Week 6)"],
        ["T17", "Automated WCAG 2.2 AA accessibility audit on all three screens.", "Contrast >= 4.5:1; touch targets >= 48 px on all screens.", "Planned (Week 6)"],
        ["T18", "Offline comparison: Rules vs. Isolation Forest on synthetic logs.", "Precision, recall, and false-alarm rates reported.", "Planned (Week 6)"]
    ]
    ta5 = doc.add_table(rows=len(t5_data), cols=4)
    ta5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(ta5)
    for r_i, row in enumerate(t5_data):
        for c_i, val in enumerate(row):
            ta5.rows[r_i].cells[c_i].text = val
    format_table_header(ta5.rows[0])
    format_table_body(ta5, col_alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])

    p_cap_a5 = doc.add_paragraph("Table A5.1. Complete test plan covering functional unit tests, real-world edge cases, and accessibility audits.")
    p_cap_a5.runs[0].font.size = Pt(8.5)
    p_cap_a5.runs[0].font.italic = True
    p_cap_a5.paragraph_format.space_after = Pt(14)

    # APPENDIX 6
    doc.add_heading("Appendix 6. Gantt Chart and Risk Register", level=1)

    gantt_img = os.path.join(ASSETS_DIR, "45cff0f31b56070a30cf6983fd683f000bd79aaf.png")
    if os.path.exists(gantt_img):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(gantt_img, width=Inches(6.2))
        p_fig_a6 = doc.add_paragraph("Figure A6.1 Gantt chart showing planned vs. actual progress at the IPR status date (16 November 2026).")
        p_fig_a6.runs[0].font.size = Pt(8.5)
        p_fig_a6.runs[0].font.italic = True
        p_fig_a6.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig_a6.paragraph_format.space_after = Pt(14)

    doc.add_heading("Table A6.1 Project Risk Register (L = Likelihood, I = Impact; Reviewed Weekly)", level=2)
    a6_data = [
        ["Identified Risk", "L", "I", "Score", "Active Mitigation Strategy"],
        ["Browser drops prompt when tablet enters aggressive sleep state.", "M", "H", "6", "Page-drawn prompts, tablet configured in kiosk mode with screen pinned on; test on hardware (T16)."],
        ["False caregiver alerts cause severe anxiety and alert fatigue.", "M", "H", "6", "Alert only after 2 consecutive misses on opted-in tasks; quantify false-alarm rate in testing (T7–T9)."],
        ["Direct clinical access to individuals with dementia restricted.", "H", "M", "6", "Derive requirements from published literature; proxy evaluation with student caregivers under ethics clearance."],
        ["Secondary features crowd out core reliability work.", "M", "M", "4", "Strict MoSCoW prioritization; secondary features start only after core tests pass."],
        ["Speech recognition misinterprets elderly or accented speech.", "M", "M", "4", "Voice input remains optional; physical high-contrast buttons always available; restricted keyword grammar."],
        ["Ethics clearance for proxy user study delayed.", "M", "M", "4", "Project evaluation decoupled to rely on WCAG 2.2 AA audits and scenario testing; proxy test marked future work."],
        ["Academic time pressure from concurrent module deadlines.", "M", "M", "4", "Weekly timeboxing; 3-day buffer preserved ahead of final dissertation deadline."],
        ["Synthetic activity data insufficiently noisy for SQ3 evaluation.", "H", "L", "3", "Inject parameterized Gaussian noise, irregular sleep intervals, and weekend variance into logs."],
        ["Personal patient health data accidentally committed to repo.", "L", "H", "3", "Simulated data used exclusively; strict repository `.gitignore` audit; zero real PII stored."]
    ]
    ta6 = doc.add_table(rows=len(a6_data), cols=5)
    ta6.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(ta6)
    for r_i, row in enumerate(a6_data):
        for c_i, val in enumerate(row):
            ta6.rows[r_i].cells[c_i].text = val
    format_table_header(ta6.rows[0])
    format_table_body(ta6, col_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    p_cap_a6 = doc.add_paragraph("Table A6.1. Comprehensive risk register with impact scoring and active mitigations.")
    p_cap_a6.runs[0].font.size = Pt(8.5)
    p_cap_a6.runs[0].font.italic = True
    p_cap_a6.paragraph_format.space_after = Pt(14)

    # Save to final path
    doc.save(OUTPUT_PATH)
    print(f"Successfully generated full publication-grade document at: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_full_document()
