# https://realpython.com/primer-on-jinja-templating/
import datetime as dt
import jinja2
import streamlit as st
import subprocess
import tempfile

from pathlib import Path


# Include README
with open('frontpage.md', 'r') as fp:
    frontpage = fp.read()
st.markdown(frontpage)

# Parameters
template_dir = Path("templates")
commond_dir = Path("common")

common = {
    "TODAY": dt.date.today().isoformat(),
    "PROTOCOL_VERSION": 1,
}

templates = {
    "SPIRIT 2025 (studi sperimentali)": "spirit2025.md",
    "STROBE 2007 (studi osservazionali)": "strobe2007.md",
    "STARD 2015 (studi diagnostici)": "stard2015.md",
    "Template agnostico, italiano, semplice": "old_ctsu.md"
}

monomulti = {
    "Monocentrico": "monocentrico",
    "Multicentrico": "multicentrico"
}

retroprospettico = {
    "Retrospettivo": "retrospettivo",
    "Retrospettivo e Prospettico": "retrospettivo_e_prospettico",
    "Prospettico": "prospettico",
}

# User data input
# ----------------
st.text_input("**Titolo studio**", key="TITOLO_STUDIO")
titolo_studio = st.session_state.TITOLO_STUDIO
st.text_input("**Acronimo studio**", key="ACRONIMO_STUDIO")
acronimo_studio = st.session_state.ACRONIMO_STUDIO


def selbox_value(tit, d):
    sel = st.selectbox(tit, d.keys())
    return d[sel]


template_fname = selbox_value("**Template adottato**", templates)
template_path = template_dir / template_fname
monomulti_sel = selbox_value("**Mono/multicentrico**", monomulti)
retroprospettico_sel = selbox_value("**Retrospettivo/Prospettico**", retroprospettico)

# st.markdown("**Opzioni**")
# farmacologico = st.checkbox("Farmacologico")


user_input = {
    "TITOLO_STUDIO": titolo_studio,
    "ACRONIMO_STUDIO": acronimo_studio,
    "MONOMULTI": monomulti_sel,
    "RETROPROSPETTICO": retroprospettico_sel,
}



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
