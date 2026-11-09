"""Builds Mazen EL-Gayar's CV variants from template.docx and exports them to PDF
(with Pages on macOS, or Microsoft Word on Windows).

Variants: software, game and general, each as a one-page ("short") and a full version.
Generated files go to resume/output/ (git-ignored). The one-page software CV is also copied to
resume/Mazen-EL-Gayar-CV.pdf, the file the portfolio's "Download CV" buttons link to.

Usage:
    python3 resume/build_resume.py             # build all six variants and export PDFs
    python3 resume/build_resume.py --no-pdf    # build the DOCX files only
    python3 resume/build_resume.py --role software --role game
"""

from __future__ import annotations

import argparse
import platform
import re
import shutil
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template.docx"
OUTPUT = HERE / "output"
PUBLIC_CV = HERE / "Mazen-EL-Gayar-CV.pdf"
PUBLIC_VARIANT = ("software", True)

ROLES = ("software", "game", "general")
FILE_NAMES = {
    ("software", True): "Mazen_EL-Gayar_Software_Engineer_1Page",
    ("software", False): "Mazen_EL-Gayar_Software_Engineer_Full",
    ("game", True): "Mazen_EL-Gayar_Game_Developer_1Page",
    ("game", False): "Mazen_EL-Gayar_Game_Developer_Full",
    ("general", True): "Mazen_EL-Gayar_General_1Page",
    ("general", False): "Mazen_EL-Gayar_General_International_Full",
}
TITLES = {
    "software": "Software Engineer | Flutter & NestJS & UE",
    "game": "Unreal Engine Game Developer | MazenX",
    "general": "Software Engineer & Game Developer",
}

# --------------------------------------------------------------------------------------------
# Links. The full CVs list them all, in this order, under "Portfolio and supporting records".
# --------------------------------------------------------------------------------------------
LINKS = {
    "linkedin": ("LinkedIn", "https://www.linkedin.com/in/mazen-el-gayar-995949218/"),
    "github": ("GitHub", "https://github.com/MazenxELGayar/"),
    "mazenx": ("MazenX LinkedIn", "https://www.linkedin.com/company/144794199"),
    "pubdev": ("pub.dev", "https://pub.dev/"),
    "paypal": ("PayPal package", "https://pub.dev/packages/flutter_paypal_payment_checkout_v2"),
    "i18n": ("i18n package", "https://pub.dev/packages/flutter_i18n_translator"),
    "penguin": ("Penguin", "https://penguin.com.sa/"),
    "doctorvoice": ("DoctorVoice", "https://doctorvoice.net/"),
    "dv_app_store": ("DoctorVoice App Store", "https://apps.apple.com/eg/developer/doctor-voice-technology/id1815534864"),
    "dv_google_play": ("DoctorVoice Google Play", "https://play.google.com/store/apps/developer?id=DoctorVoice"),
    "grwan_app_store": ("Grwan App Store", "https://apps.apple.com/us/developer/grwan-group-fze/id1619845290"),
    "grwan_google_play": ("Grwan Google Play", "https://play.google.com/store/apps/developer?id=GRWAN+GROUP+FZE"),
    "leango": ("LeanGo", "https://www.linkedin.com/company/global-lean-industry-4-0/posts/?feedView=all"),
    "flexonexus": ("FlexoNexus", "https://www.linkedin.com/company/flexonexus"),
    "rasid": ("RASID", "https://rasid.com.eg"),
    "rasid_google_play": ("RASID Google Play", "https://play.google.com/store/apps/developer?id=Rasid+L.L.C&hl=en"),
    "myflix_remote": ("MyFlix Remote", "https://play.google.com/store/apps/details?id=com.mazenx.myflix_remote"),
    "myflix_windows": ("MyFlix Windows", "https://apps.microsoft.com/detail/9p61pw36ppqw"),
    "samsarly": ("Samsarly project", "https://drive.google.com/drive/folders/1vXvlVPVPDqettWt_7VDlilIxYMwcqb-j?usp=sharing"),
    "bsc": ("BSc certificate", "https://drive.google.com/file/d/1AxyaEUN3p8mVAFbysw71h2R3P54kZodg/view?usp=drive_link"),
    "transcript": ("Transcript", "https://drive.google.com/drive/folders/1G2ebxA9ZLFZMTs11qvQE98O3z7seSj4E?usp=drive_link"),
    "graduation": ("Graduation records", "https://drive.google.com/drive/folders/1o9FbGak9h_8mKDPU8kH732-GOLIlV0Ah?usp=sharing"),
    "honors": ("Honors record", "https://drive.google.com/drive/folders/1ZRxuPVCCSGLwANxNcDBtklhPvwlkqsMl?usp=drive_link"),
    "iti": ("ITI certificate", "https://drive.google.com/drive/folders/1VxIlNP1aEMxSY1IrY-6tp90k3nWI5HTm?usp=drive_link"),
    "ue5": ("UE5 course", "https://www.udemy.com/certificate/UC-aef39d5c-400b-4e7a-8cd5-f176edd564b9/"),
    "ielts": ("IELTS camp", "https://drive.google.com/file/d/1ZV1urBkg99-SOX8rifqWZ7pTSzPLcmpr/view?usp=drive_link"),
    "rasid_appreciation": ("RASID appreciation", "https://drive.google.com/file/d/1CrptTPTvchxBL_E1vqTnwMbjTIUrsXG0/view?usp=drive_link"),
    "rasid_experience": ("RASID experience", "https://drive.google.com/file/d/1Kz0Tw8DL-INkzbP9-f60v2yJwS80ib6v/view?usp=drive_link"),
    "grwan_experience": ("Grwan experience", "https://drive.google.com/file/d/1duyA4hdNlaTIMwHKmq8A7kkIhDB4FEub/view?usp=drive_link"),
    "crazykix_windows": ("Crazy Kix Windows", "https://apps.microsoft.com/detail/9nst3zj3r8d7"),
    "crazykix_android": ("Crazy Kix Android", "https://play.google.com/store/apps/details?id=com.mazenx.crazykix"),
    "bonerunner_windows": ("The Bone Runner Windows", "https://apps.microsoft.com/detail/9phqzbvkflf5?hl=en-US&gl=EG"),
    "bonerunner_android": ("The Bone Runner Android", "https://play.google.com/store/apps/details?id=com.mazenx.thebonerunner"),
    "crazykix_github": ("Crazy Kix GitHub", "https://github.com/MazenxELGayar/Jetpack"),
    "portfolio": ("Portfolio", "https://mazenxelgayar.github.io/"),
}
GAME_STORES = ["crazykix_windows", "crazykix_android", "bonerunner_windows", "bonerunner_android"]
# (link key, label shown in the short CV, label shown in the full CV)
CREDENTIALS_SHORT = [("iti", "ITI Flutter"), ("grwan_experience", "Grwan Exp."), ("rasid_experience", "RASID Exp."),
                     ("rasid_appreciation", "RASID Appreciation")]
CREDENTIALS_FULL = [("iti", "ITI Flutter Course"), ("grwan_experience", "Grwan Experience Certificate"),
                    ("rasid_experience", "RASID Experience Certificate"), ("rasid_appreciation", "RASID Appreciation Certificate"),
                    ("ue5", "UE5 Course"), ("ielts", "IELTS Certificate"), ("bsc", "BSc Certificate")]

# --------------------------------------------------------------------------------------------
# Content. A " — " in a bullet makes the text before it bold.
# --------------------------------------------------------------------------------------------
PLATFORMS = "Android, iOS, Web, macOS, and Windows"

SUMMARY = {
    "software": [
        f"Software Engineer with 4+ years of experience building and delivering production-ready software across mobile, web, desktop, backend, and game development. Specialized in Flutter for {PLATFORMS} applications, NestJS for backend services and APIs, and Unreal Engine for cross-platform game development targeting Android, iOS, and Windows.",
        "Built and contributed to a wide range of applications across enterprise, healthcare, education, and SaaS domains, including multi-tenant ERP systems, Facility Management platforms, AI-powered healthcare apps, e-learning platforms with live video classes, LeanGo applications, entertainment apps, and location-based services using Maps.",
        "Experienced in building products end-to-end, from initial ideas and architecture through development, deployment, and maintenance. Worked on live products, collaborated with cross-functional teams, contributed to open-source Flutter packages on pub.dev, and mentored fresh/junior developers.",
    ],
    "game": [
        "Independent Unreal Engine game developer and founder of MazenX, developing and publishing games for Android and Windows using C++ and Blueprints. Builds gameplay systems for movement, combat, enemy AI, navigation, interactive mechanics, and 2D platforming. Brings 4+ years of production software engineering experience in architecture, cross-platform delivery, debugging, and collaboration.",
    ],
    "general": [
        f"Software and game developer with 4+ years of experience building and delivering production-ready software across mobile, web, desktop, backend, and game development. Builds Flutter applications for {PLATFORMS}; NestJS services and APIs; and Unreal Engine games with C++ and Blueprints.",
        "Experience across enterprise, healthcare, SaaS, multi-tenant ERP, Facility Management, e-learning, entertainment, and location-based products. Contributes from idea and architecture through deployment and maintenance, collaborates with cross-functional teams, publishes Flutter packages, and mentors junior developers.",
    ],
}
SHORT_SUMMARY = {
    "software": "Software Engineer with 4+ years delivering production Flutter/Dart applications and NestJS APIs across mobile, web, desktop, healthcare, ERP, and SaaS. Also develops Unreal Engine games for Android, iOS, and Windows. Experienced in end-to-end delivery, cross-functional collaboration, open-source packages, and mentoring.",
    "game": "Independent Unreal Engine game developer and founder of MazenX, publishing Android and Windows games with C++ and Blueprints. Focused on gameplay programming, 2D platforming, movement, combat, enemy AI, and level design, backed by 4+ years in production software engineering.",
    "general": "Software and game developer with 4+ years delivering Flutter applications, NestJS backend services, and Unreal Engine games. Experienced across enterprise, healthcare, ERP, facility operations, and SaaS, from architecture through release, with cross-functional collaboration and mentoring.",
}

PENGUIN_SHORT = f"Senior Flutter Developer | Penguin (KSA) | Part-time | Oct 2026–Present — Builds two EdTech Flutter apps on one shared package for {PLATFORMS}, including Zoom-style live video classes."
PENGUIN_FULL = f"Senior Flutter Developer | Penguin (KSA) | Part-time | Oct 2026–Present — Builds the Penguin (students and parents) and Penguin Staff (teachers and supervisors) Flutter apps on one shared package for {PLATFORMS}: Zoom-style live video classes, courses, homework, real-time chat, and QR parent linking; set up CI/CD store releases."

SOFTWARE_EXPERIENCE_SHORT = [
    PENGUIN_SHORT,
    f"Senior Software Engineer | DoctorVoice (Egypt) | Part-time | May 2024–Present — Builds Flutter apps for {PLATFORMS} and NestJS APIs; manages QC, AI, backend, frontend, mobile, and data-analysis teams; liaises between the CEO/Marketing and tech teams; mentored 5+ interns.",
    "Independent Game Developer | MazenX | Jul 2026–Present — Founded the studio; develops and publishes Unreal Engine games for Android and Windows.",
    "Senior Flutter Developer | FlexoNexus (KSA) | Full-time | Jan–Mar 2026 — Built multi-tenant ERP and four client app flavors.",
    "Flutter Developer / Project Manager | Grwan LLC (UAE) | Full-time | Mar–Dec 2025 — Led LeanGo application development and releases.",
    "Flutter Developer Lead & Mentor | RASID (Egypt) | Full-time | Apr 2024–Mar 2025 — Mentored 7+ developers and built RASID apps.",
]
SOFTWARE_EXPERIENCE_FULL = [
    PENGUIN_FULL,
    f"Senior Software Engineer | DoctorVoice (Egypt) | Part-time | May 2024–Present — Builds Flutter apps for {PLATFORMS} and NestJS APIs; managed QC, AI, backend, frontend, mobile, and data-analysis teams; served as liaison between the CEO/Marketing and tech teams; mentored 5+ interns.",
    "Independent Game Developer | MazenX | Jul 2026–Present — Founded the studio and independently develops, tests, and publishes Unreal Engine games for Android and Windows using C++ and Blueprints.",
    "Senior Flutter Developer | FlexoNexus (KSA) | Full-time | Jan–Mar 2026 — Built a multi-tenant ERP mobile app; delivered four client flavors using shared architecture and client-specific workflows; supported controlled store releases.",
    "Flutter Developer / Project Manager | Grwan LLC (UAE) | Full-time | Mar–Dec 2025 — Led LeanGo Eye, FTE, FM, CIL, and related app development; coordinated Jira work and staged Play Store/App Store releases.",
    "Flutter Developer Lead & Mentor | RASID (Egypt) | Full-time | Apr 2024–Mar 2025 — Mentored 7+ developers in Flutter, Dart, clean architecture, OOP, and state management; built RASID and Admin apps; performed reviews and coordinated releases.",
    "Flutter Package Publisher | pub.dev | 2025–Present — Published reusable Flutter packages including PayPal checkout, i18n translation tooling, and utilities.",
]
SOFTWARE_SKILLS_SHORT = [
    "Flutter, Dart, Android, iOS, Web, macOS, Windows, Unreal Engine 5, C++, Blueprints, NestJS, Node.js, REST APIs, OOP, Clean Architecture, design patterns, dependency injection, Cubit, Notifiers, GetIt, Firebase, SQLite, Hive, Maps/GPS, NFC, Bluetooth, QR/barcode, AI integrations, testing, debugging, Git, GitHub, Codemagic, CI/CD, Agile/Scrum, Jira.",
]
SOFTWARE_SKILLS_FULL = [
    "Mobile: Flutter, Dart, Android, iOS, Web, macOS, Windows, GPS/maps, NFC, Bluetooth, QR/barcode, camera, notifications, offline/background services.",
    "Backend & Data: NestJS, Node.js, REST APIs, sockets, Firebase, SQLite, Hive, JSON serialization, pagination.",
    "Architecture: OOP, Clean Architecture, design patterns, dependency injection, modular/reusable components, Cubit, Notifiers, GetIt.",
    "Delivery: Testing, debugging, unit testing, code review, Git/GitHub, Codemagic, CI/CD, Agile/Scrum, Jira.",
    "Game development: Unreal Engine 5, C++, Blueprints, gameplay programming, movement, combat, AI/navigation, Android/iOS/Windows targets.",
]
SOFTWARE_PROJECTS = [
    "Multi-tenant ERP platform (FlexoNexus) — Shared architecture, client-specific workflows, and four white-labeled app flavors.",
    "LeanGo applications — Contributed to most of the family, including LeanGo Eye, LeanGo FTE, LeanGo FM, LeanGo CIL, and others; facility/enterprise workflows include GPS, NFC, messaging, safety, and ticketing.",
    f"Penguin — Saudi online-learning platform: student/parent and staff Flutter apps on one shared package, with Zoom-style live video classes, on {PLATFORMS}.",
    "DoctorVoice — AI-assisted healthcare applications with Flutter clients and NestJS backend services.",
    "Open-source Flutter packages — PayPal checkout and i18n tools on pub.dev.",
    "MazenX Unreal Engine games — Crazy Kix, The Bone Runner, and Gambling Addiction; 2D movement, combat, enemy AI, traps, and interactive systems.",
]
# The one-page CV repeats less: Penguin is already described under Experience.
SOFTWARE_PROJECTS_SHORT = [
    f"Penguin — EdTech Flutter apps with Zoom-style live video classes on {PLATFORMS}." if line.startswith("Penguin") else line
    for line in SOFTWARE_PROJECTS
]
SOFTWARE_EXTRA_PROJECTS = [
    "MyFlix and MyFlix Remote — Connected desktop/mobile media ecosystem with synchronized playback and mobile remote control.",
    "Samsarly — Real-estate marketplace with map-based property search and AI-assisted price estimation.",
]

GAME_EXPERIENCE = [
    "Founder & Independent Game Developer | MazenX | Jul 2026–Present — Independently develops, tests, and publishes Unreal Engine games for Android and Windows using C++ and Blueprints.",
    "Gameplay work: movement, combat, enemy AI and navigation, interactive mechanics, traps, animation, and level design.",
]
GAMES = [
    "Crazy Kix — Action platformer with jumping, interactive buttons, cannons, chasing drones, and laser attacks.",
    "The Bone Runner — 2D action platformer with skeleton enemies, combat, spikes, saws, and timed traps.",
    "Gambling Addiction — Expanded Blueprint course project; magic-ball outcomes heal, spawn/destroy allies or enemies across Bot vs Bots, Human vs Bot, and Bots vs Humans modes.",
]
GAME_SKILLS = "Unreal Engine 5, C++, Blueprints, gameplay programming, 2D platforming, character movement, combat, enemy AI, navigation, interactive mechanics, level design, debugging, Android/Windows deployment, Git, OOP, Clean Architecture, Flutter, Dart, NestJS, REST APIs, Agile/Scrum, Jira."
GAME_SOFTWARE_EXPERIENCE = [
    f"Penguin (KSA) | Senior Flutter Developer, Part-time | Oct 2026–Present — Two EdTech Flutter apps on one shared package for {PLATFORMS}, including Zoom-style live video classes.",
    "DoctorVoice (Egypt) | Senior Software Engineer, Part-time | May 2024–Present — Flutter and NestJS delivery; managed QC, AI, backend, frontend, mobile, and data-analysis teams; liaison between CEO/Marketing and tech; mentored 5+ interns.",
    "FlexoNexus (KSA) | Senior Flutter Developer, Full-time | Jan–Mar 2026 — Multi-tenant ERP and four client app flavors.",
    "Grwan LLC (UAE) | Flutter Developer / Project Manager, Full-time | Mar–Dec 2025 — Led LeanGo apps and staged releases.",
    "RASID (Egypt) | Flutter Developer Lead & Mentor, Full-time | Apr 2024–Mar 2025 — Mentored 7+ developers and delivered Flutter applications.",
]
GAME_RELATED_ENGINEERING = [
    "Multi-tenant ERP — Shared Flutter architecture supports four client-specific app flavors and workflows.",
    "Facility operations — LeanGo apps apply mobile workflows for location, NFC, safety, messaging, and tickets.",
    "Healthcare — DoctorVoice products combine Flutter clients, NestJS services, and AI-assisted workflows.",
    "Education — Penguin apps share one Flutter package across mobile, web, and desktop, including Zoom-style live video classes.",
]

GENERAL_SKILLS = "Flutter, Dart, Android, iOS, Web, macOS, Windows, NestJS, Node.js, REST APIs, Unreal Engine 5, C++, Blueprints, OOP, Clean Architecture, design patterns, dependency injection, Cubit, Firebase, SQLite, Hive, Maps/GPS, AI integrations, testing, debugging, Git, CI/CD, Agile/Scrum, Jira, mentoring, project coordination."
GENERAL_EXPERIENCE = [
    PENGUIN_SHORT,
    f"Senior Software Engineer | DoctorVoice (Egypt) | Part-time | May 2024–Present — Builds Flutter apps for {PLATFORMS} and NestJS APIs; manages QC, AI, backend, frontend, mobile, and data-analysis teams; liaises between CEO/Marketing and tech; mentors 5+ interns.",
    "Founder & Independent Game Developer | MazenX | Jul 2026–Present — Develops and publishes Unreal Engine games for Android and Windows.",
    "Senior Flutter Developer | FlexoNexus (KSA) | Full-time | Jan–Mar 2026 — Built a multi-tenant ERP and four app flavors.",
    "Flutter Developer / Project Manager | Grwan LLC (UAE) | Full-time | Mar–Dec 2025 — Led development and releases for LeanGo applications.",
    "Flutter Developer Lead & Mentor | RASID (Egypt) | Full-time | Apr 2024–Mar 2025 — Mentored 7+ developers and delivered Flutter applications.",
]
GENERAL_PROJECTS = [
    "Multi-tenant ERP platform (FlexoNexus) — Shared architecture, client-specific workflows, and four app flavors.",
    "LeanGo applications — Contributed to most of the family, including LeanGo Eye, LeanGo FTE, LeanGo FM, LeanGo CIL, and others; facility-management and enterprise-operations products.",
    f"Penguin — EdTech Flutter apps with Zoom-style live video classes on {PLATFORMS}.",
    "DoctorVoice — AI-assisted healthcare apps with Flutter and NestJS.",
    "MazenX Games — Crazy Kix, The Bone Runner, Gambling Addiction; Unreal Engine, C++, and Blueprints.",
]
GENERAL_EXTRA_PROJECTS = [
    "MyFlix and MyFlix Remote — Connected desktop/mobile media ecosystem with synchronized playback and remote control.",
    "Samsarly — Real-estate marketplace with map-based property search and AI-assisted price estimation.",
    "Open-source Flutter packages — Published PayPal checkout integration and i18n translation tooling on pub.dev.",
]
LANGUAGES = "Arabic C2 | English B2 | French A2"

EDUCATION_SHORT = [
    "B.S. Computers and Informatics, Suez Canal University, 2023; GPA 4.0, Excellent with Honors; ranked 5th in the Faculty of Computers and Informatics.",
    "Presidential Recognition from Egypt's President at Suez Canal Authority Stadium; represented SCU and held the university flag. Also honored by the SCU President.",
    "Certificates: ITI Flutter Course; UE5 Blueprints (Udemy); English B2; IELTS preparation; Grwan and RASID Experience Certificates; RASID Certificate of Appreciation.",
]
EDUCATION_FULL = [
    "B.S. Computers and Informatics, Suez Canal University, 2023 | GPA 4.0, Excellent with Honors | Ranked 5th in the Faculty of Computers and Informatics.",
    "Presidential Recognition from the President of Egypt at Suez Canal Authority Stadium; represented SCU and held the university flag. Also honored by the SCU President.",
]
CERTIFICATES_FULL = "UE5 Blueprints — Udemy, Stephen Ulibarri | ITI Flutter Course Certification | English B2 | 45-hour IELTS Preparation Camp | Grwan and RASID Experience Certificates | RASID Certificate of Appreciation."


# --------------------------------------------------------------------------------------------
# DOCX helpers
# --------------------------------------------------------------------------------------------
def replace_text(paragraph, text: str, plain: bool = False) -> None:
    """Replaces a paragraph's text while keeping the first run's formatting."""
    for old in list(paragraph._p.findall(".//" + qn("w:hyperlink"))):
        old.getparent().remove(old)
    runs = paragraph._p.findall(".//" + qn("w:r"))
    if not runs:
        paragraph.add_run(text)
        return
    first = runs[0]
    t = first.find(qn("w:t"))
    if t is None:
        t = OxmlElement("w:t")
        first.append(t)
    t.text = text
    for extra in runs[1:]:
        extra.getparent().remove(extra)
    if plain:
        props = first.find(qn("w:rPr"))
        if props is not None:
            for tag in (qn("w:b"), qn("w:bCs"), qn("w:i"), qn("w:iCs")):
                node = props.find(tag)
                if node is not None:
                    props.remove(node)


def add_link(paragraph, label: str, url: str) -> None:
    rid = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    props.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    props.append(underline)
    run.append(props)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    link.append(run)
    paragraph._p.append(link)


def add_link_list(paragraph, items: list[tuple[str, str]]) -> None:
    """Appends "label | label | ..." links to a paragraph; items are (label, url)."""
    for i, (label, url) in enumerate(items):
        if i:
            paragraph.add_run(" | ")
        add_link(paragraph, label, url)


# --------------------------------------------------------------------------------------------
# Resume
# --------------------------------------------------------------------------------------------
class Resume:
    def __init__(self, role: str, short: bool):
        if not TEMPLATE.exists():
            raise SystemExit(f"Missing CV template: {TEMPLATE}")
        self.role, self.short = role, short
        self.doc = Document(TEMPLATE)
        self.prototypes = {
            style: deepcopy(next(p._p for p in self.doc.paragraphs if p.style.name == style))
            for style in ("Heading 1", "Heading 2", "List Bullet")
        }
        self.prototypes["Normal"] = deepcopy(
            next(p._p for p in self.doc.paragraphs if p.style.name == "Normal" and p.text.strip())
        )
        # Keep the name, title and contact lines; everything below is rebuilt.
        for p in list(self.doc.paragraphs)[3:]:
            p._element.getparent().remove(p._element)
        replace_text(self.doc.paragraphs[1], TITLES[role])
        contact = self.doc.paragraphs[2]
        for run in contact.runs:
            run.text = run.text.replace(" 42514", "")
        contact.add_run(" | ")
        add_link(contact, "MazenX", LINKS["mazenx"][1])
        contact.add_run().add_break()
        contact.add_run("Portfolio: ")
        add_link(contact, "mazenxelgayar.github.io", LINKS["portfolio"][1])

    # Building blocks -----------------------------------------------------------------------
    def para(self, text: str = "", kind: str = "Normal"):
        element = deepcopy(self.prototypes[kind])
        body = self.doc._body._body
        body.insert(len(body) - 1, element)
        p = self.doc.paragraphs[-1]
        replace_text(p, text, plain=kind in ("Normal", "List Bullet"))
        if kind == "Heading 1":
            borders = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            for key, value in (("val", "single"), ("sz", "6"), ("space", "4"), ("color", "000000")):
                bottom.set(qn("w:" + key), value)
            borders.append(bottom)
            p._p.get_or_add_pPr().append(borders)
        return p

    def heading(self, text: str) -> None:
        self.para(text, "Heading 1")

    def bullet(self, text: str) -> None:
        p = self.para("", "List Bullet")
        if " — " in text:
            lead, tail = text.split(" — ", 1)
            p.add_run(lead).bold = True
            p.add_run(" — " + tail)
        else:
            p.add_run(text)

    def bullets(self, items: list[str]) -> None:
        for item in items:
            self.bullet(item)

    def labelled_links(self, label: str, keys_and_labels: list[tuple[str, str]]) -> None:
        p = self.para(label)
        p.add_run(" ")
        add_link_list(p, [(text, LINKS[key][1]) for key, text in keys_and_labels])

    def game_stores(self, label: str = "MazenX game stores:") -> None:
        self.labelled_links(label, [(key, LINKS[key][0]) for key in GAME_STORES])

    def crazykix_source(self) -> None:
        self.labelled_links("Crazy Kix source code:", [("crazykix_github", "GitHub repository")])

    def all_links(self) -> None:
        self.heading("Portfolio and supporting records")
        add_link_list(self.para(""), list(LINKS.values()))

    def education(self) -> None:
        self.heading("Education, honors & certificates")
        if self.short:
            for text in EDUCATION_SHORT:
                self.para(text)
            self.labelled_links("Certificate links:", CREDENTIALS_SHORT)
        else:
            self.bullets(EDUCATION_FULL)
            self.para(CERTIFICATES_FULL)
            self.labelled_links("Credential links:", CREDENTIALS_FULL)

    # Sections per role ---------------------------------------------------------------------
    def software(self) -> None:
        self.heading("Experience")
        self.bullets(SOFTWARE_EXPERIENCE_SHORT if self.short else SOFTWARE_EXPERIENCE_FULL)
        self.heading("Technical skills")
        self.bullets(SOFTWARE_SKILLS_SHORT if self.short else SOFTWARE_SKILLS_FULL)
        self.heading("Selected projects")
        self.bullets(SOFTWARE_PROJECTS_SHORT if self.short else SOFTWARE_PROJECTS)
        self.game_stores()
        self.crazykix_source()
        if not self.short:
            self.heading("Additional product work")
            self.bullets(SOFTWARE_EXTRA_PROJECTS)
        self.education()
        if not self.short:
            self.all_links()

    def game(self) -> None:
        self.heading("Game development experience")
        self.bullets(GAME_EXPERIENCE)
        self.heading("Selected games")
        self.bullets(GAMES)
        self.game_stores("Store pages:")
        self.crazykix_source()
        self.heading("Technical skills")
        self.para(GAME_SKILLS)
        self.heading("Software engineering experience")
        self.bullets(GAME_SOFTWARE_EXPERIENCE)
        if not self.short:
            self.heading("Related product engineering")
            self.bullets(GAME_RELATED_ENGINEERING)
        self.education()
        if not self.short:
            self.all_links()

    def general(self) -> None:
        self.heading("Core skills")
        self.para(GENERAL_SKILLS)
        self.heading("Experience")
        self.bullets(GENERAL_EXPERIENCE)
        self.heading("Selected projects")
        self.bullets(GENERAL_PROJECTS)
        self.game_stores()
        self.crazykix_source()
        if not self.short:
            self.heading("Additional projects")
            self.bullets(GENERAL_EXTRA_PROJECTS)
        self.education()
        if not self.short:
            self.all_links()
            self.para(LANGUAGES)

    # Output --------------------------------------------------------------------------------
    def normalize_hyperlinks(self) -> None:
        for link in self.doc._element.body.findall(".//" + qn("w:hyperlink")):
            for run in link.findall(".//" + qn("w:r")):
                props = run.find(qn("w:rPr"))
                if props is None:
                    props = OxmlElement("w:rPr")
                    run.insert(0, props)
                for tag in (qn("w:color"), qn("w:u")):
                    for old in props.findall(tag):
                        props.remove(old)
                color = OxmlElement("w:color")
                color.set(qn("w:val"), "0563C1")
                props.append(color)
                underline = OxmlElement("w:u")
                underline.set(qn("w:val"), "single")
                props.append(underline)

    def tighten_for_one_page(self) -> None:
        for p in self.doc.paragraphs:
            p.paragraph_format.line_spacing = 1.0
            if p.style.name in ("Normal", "List Bullet"):
                p.paragraph_format.space_after = Pt(0)
            elif p.style.name == "Heading 1":
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(1)

    def build(self) -> Path:
        self.heading("Professional summary")
        for text in [SHORT_SUMMARY[self.role]] if self.short else SUMMARY[self.role]:
            self.para(text)
        getattr(self, self.role)()
        self.normalize_hyperlinks()
        if self.short:
            self.tighten_for_one_page()
        OUTPUT.mkdir(parents=True, exist_ok=True)
        path = OUTPUT / f"{FILE_NAMES[(self.role, self.short)]}.docx"
        self.doc.save(path)
        return path


# --------------------------------------------------------------------------------------------
# PDF export: Pages on macOS (Word for Mac rejects "save as" from scripts), Word on Windows,
# LibreOffice on Linux (used by the GitHub Pages deploy)
# --------------------------------------------------------------------------------------------
MAC_PAGES_EXPORT = """
on run argv
  set docxPath to item 1 of argv
  set pdfPath to item 2 of argv
  set docName to item 3 of argv
  -- Resolve the paths here, not inside the tell block: there Pages would resolve them itself and
  -- its sandbox refuses ("Pages couldn't read the file").
  set docxFile to POSIX file docxPath
  set pdfFile to POSIX file pdfPath
  tell application "Pages"
    open docxFile
    -- Pages imports Word files asynchronously; wait (up to 30 s) until the document is listed.
    set theDoc to missing value
    repeat 150 times
      repeat with candidate in documents
        if name of candidate is docName then set theDoc to contents of candidate
      end repeat
      if theDoc is not missing value then exit repeat
      delay 0.2
    end repeat
    if theDoc is missing value then error "Pages did not open " & docName
    export theDoc to pdfFile as PDF
    close theDoc saving no
  end tell
end run
"""

WINDOWS_WORD_EXPORT = """
param([string]$Docx, [string]$Pdf)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open($Docx, $false, $true)
  try { $doc.ExportAsFixedFormat($Pdf, 17) } finally { $doc.Close(0) }
} finally { $word.Quit() }
"""


def export_pdf(docx: Path) -> Path:
    pdf = docx.with_suffix(".pdf")
    pdf.unlink(missing_ok=True)
    system = platform.system()
    if system == "Darwin":
        command = ["osascript", "-e", MAC_PAGES_EXPORT, str(docx), str(pdf), docx.stem]
    elif system == "Windows":
        script = OUTPUT / "_export.ps1"
        script.write_text(WINDOWS_WORD_EXPORT, encoding="utf-8")
        command = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), str(docx), str(pdf)]
    else:
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if not soffice:
            raise SystemExit("PDF export needs Pages (macOS), Microsoft Word (Windows) or LibreOffice (Linux); "
                             "rerun with --no-pdf.")
        command = [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(docx.parent), str(docx)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or not pdf.exists():
        raise SystemExit(f"Could not export {docx.name}: {result.stderr.strip()}")
    return pdf


def pdf_page_count(pdf: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))


# --------------------------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--role", action="append", choices=ROLES, help="build only this role (repeatable)")
    parser.add_argument("--no-pdf", action="store_true", help="build DOCX files only")
    parser.add_argument("--publish", type=Path, metavar="DIR", help="also copy every PDF into DIR")
    parser.add_argument("--strict", action="store_true", help="fail if a one-page CV runs over one page")
    args = parser.parse_args()

    # Write every DOCX first: Pages cannot read a file handed to it the moment it is saved.
    variants = [(role, short) for role in args.role or ROLES for short in (True, False)]
    built = [(role, short, Resume(role, short).build()) for role, short in variants]
    if args.no_pdf:
        for _, _, docx in built:
            print(f"Built  {docx.relative_to(HERE)}")
        return
    time.sleep(2)
    overflow = []
    for role, short, docx in built:
        pdf = export_pdf(docx)
        pages = pdf_page_count(pdf)
        warning = ""
        if short and pages > 1:
            overflow.append(pdf.name)
            warning = "  <-- one-page CV runs over one page"
        print(f"Built  {pdf.relative_to(HERE)}  ({pages} page{'s' if pages != 1 else ''}){warning}")
        if (role, short) == PUBLIC_VARIANT:
            shutil.copyfile(pdf, PUBLIC_CV)
            print(f"Public {PUBLIC_CV.relative_to(HERE)}")
        if args.publish:
            args.publish.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf, args.publish / pdf.name)
    if args.strict and overflow:
        raise SystemExit(f"One-page CVs run over one page: {', '.join(overflow)}")

if __name__ == "__main__":
    sys.exit(main())
