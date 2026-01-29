# https://realpython.com/primer-on-jinja-templating/
import datetime as dt
import jinja2
import streamlit as st
import subprocess
import tempfile
from pathlib import Path

# ----------
# PARAMETERS
# ----------
template_dir = Path("templates")
commond_dir = Path("common")
frontpage_file = Path('frontpage.md')
common = {
    "TODAY": dt.date.today().isoformat(),
    "PROTOCOL_VERSION": 1,
}


# utility for selection box
def sitebar_selbox_value(tit, d):
    sel = st.sidebar.selectbox(tit, d.keys())
    return d[sel]


# ---------
# Sidebar
# ---------
st.sidebar.text_input("**Titolo studio**", key="TITOLO_STUDIO")
titolo_studio = st.session_state.TITOLO_STUDIO

st.sidebar.text_input("**Acronimo studio**", key="ACRONIMO_STUDIO")
acronimo_studio = st.session_state.ACRONIMO_STUDIO

templates = {
    "Protocol | SPIRIT 2025 (studi sperimentali)": "protocol_spirit2025.md",
    "Protocol | STROBE 2007 (studi osservazionali)": "protocol_strobe2007.md",
    "Protocol | STARD 2015 (studi diagnostici)": "protocol_stard2015.md",
    # "Template agnostico, italiano, semplice": "old_ctsu.md"
    "Protocol | SAP (statistical analysis plan)": "protocol_sap.md",
}
template_fname = sitebar_selbox_value("**Template adottato**", templates)
template_path = template_dir / template_fname

monomulti = {
    "Monocentrico": "monocentrico",
    "Multicentrico": "multicentrico"
}
monomulti_sel = sitebar_selbox_value("**Mono/multicentrico**", monomulti)

retroprosp = {
    "Retrospettivo": "retrospettivo",
    "Retrospettivo e Prospettico": "retrospettivo_e_prospettico",
    "Prospettico": "prospettico",
}
retroprosp_sel = sitebar_selbox_value("**Retrospettivo/Prospettico**",
                                      retroprosp)

user_input = {
    "TITOLO_STUDIO": titolo_studio,
    "ACRONIMO_STUDIO": acronimo_studio,
    "MONOMULTI": monomulti_sel,
    "RETROPROSPETTICO": retroprosp_sel,
}


# ----------
# MAIN PAGE
# ----------
# Include README
with open(frontpage_file, 'r') as fp:
    frontpage = fp.read()

st.markdown(frontpage)


# Protocol actual creation
# -------------------------
common_intros = ["administrative_info.md", "revision_chronology.md",
                 "signature_page.md", "abbreviations.md", "toc.md"]

# Per la toc si è adottata la soluzione di questo eroe
# https://github.com/jgm/pandoc/discussions/10609#discussioncomment-13461868

# common intro
intro = []
for intropart in common_intros:
    with open(commond_dir / intropart, "r") as f:
        intro.append(f.read())

intro = "\n".join(intro)

# different template
with open(template_path, "r") as f:
    content = f.read()

# # common outro
# with open(commond_dir / "outro.md", "r") as f:
#     outro = f.read()

created_template = intro + content# + outro


# Jinja magic
# -----------
jinja_variables = common | user_input
environment = jinja2.Environment()
template = environment.from_string(created_template)
result = template.render(**jinja_variables)

tmpf = tempfile.mkstemp()
tmpfname = tmpf[1]

with open(tmpfname, "w") as f:
    print(result, file=f)
    print(f"file {tmpfname} created")


# pandoc
# ------
acronimo_prefix = f"{acronimo_studio}_" if acronimo_studio != "" else ""
outfile = Path(f"/tmp/{acronimo_prefix}study_protocol.docx")
# pandoc = f"pandoc {tmpfname} --filter=pandoc-docx-pagebreakpy -f markdown -t docx -o {outfile}".split(" ")
# pandoc = f"pandoc {tmpfname} --lua-filter filters/pagebreak.lua --toc -f markdown -t docx -o {outfile}".split(" ")
pandoc = f"pandoc {tmpfname} --lua-filter filters/pagebreak.lua --lua-filter=filters/toc-inject.lua -f markdown -t docx -o {outfile}".split(" ")
subprocess.run(pandoc)


with open(outfile, "rb") as f:
    btn = st.download_button(
        label="Download Protocol",
        data=f,
        file_name=outfile.name)
