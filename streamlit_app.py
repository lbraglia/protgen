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


# utility for selection box on the sidebar
def sidebar_selbox_value(tit, d):
    sel = st.sidebar.selectbox(tit, d.keys())
    return d[sel]


# ---------
# Sidebar
# ---------
st.sidebar.text_input("**Study Title**", key="TITOLO_STUDIO")
titolo_studio = st.session_state.TITOLO_STUDIO

st.sidebar.text_input("**Study Acronym**", key="ACRONIMO_STUDIO")
acronimo_studio = st.session_state.ACRONIMO_STUDIO

templates = {
    "Protocol | SPIRIT 2025": "protocol_spirit2025.md",
    "Protocol | STROBE 2007": "protocol_strobe2007.md",
    "Protocol | STARD 2015": "protocol_stard2015.md",
    "Protocol | CTSU (old)": "protocol_old_ctsu.md",
    "Article | STROBE 2007": "article_strobe2007.md",
    "Article | STARD 2015": "article_stard2015.md",
    "Article | CHEERS 2022": "article_cheers2022.md",
    "Other | SAP": "other_sap.md",
    "Other | HEAP": "other_heap.md",
}
template_fname = sidebar_selbox_value("**Template**", templates)
template_path = template_dir / template_fname

# monomulti = {
#     "Monocentrico": "monocentrico",
#     "Multicentrico": "multicentrico"
# }
# monomulti_sel = sidebar_selbox_value("**Mono/multicentrico**", monomulti)

# retroprosp = {
#     "Retrospettivo": "retrospettivo",
#     "Retrospettivo e Prospettico": "retrospettivo_e_prospettico",
#     "Prospettico": "prospettico",
# }
# retroprosp_sel = sidebar_selbox_value("**Retrospettivo/Prospettico**",
                                      # retroprosp)

formato = {
    "MS Word": "docx",
    "Markdown": "md"
}
formato_sel = sidebar_selbox_value("**File format**", formato)

user_input = {
    "TITOLO_STUDIO": titolo_studio,
    "ACRONIMO_STUDIO": acronimo_studio  # ,
    # "MONOMULTI": monomulti_sel,
    # "RETROPROSPETTICO": retroprosp_sel,
}


# ----------
# MAIN PAGE
# ----------
# Include README
with open(frontpage_file, 'r') as fp:
    frontpage = fp.read()

st.markdown(frontpage)

# --------------------------------------
# Code useful for template customization
# --------------------------------------
its_a_protocol = template_fname.startswith("protocol_")
chosen_format = formato_sel
acronimo_prefix = f"{acronimo_studio}_" if acronimo_studio != "" else ""
doctype = "study_protocol" if its_a_protocol else "article"
outfile_md = Path(f"/tmp/{acronimo_prefix}{doctype}.md")
outfile_docx = Path(f"/tmp/{acronimo_prefix}{doctype}.docx")


# -------------------------
# Document creation
# -------------------------
# 1) raw template
with open(template_path, "r") as f:
    template_content = f.read()

# 2) Adding intro if needed
# 
# - On one hand protocols have a common intro (administrative info etc) that
#   are imported
# - On the other article are taken vanilla, without prefixing intros

if its_a_protocol:
    protocols_intros_templates = [
        "administrative_info.md",
        "revision_chronology.md",
        "signature_page.md",
        "abbreviations.md",
        # https://github.com/jgm/pandoc/discussions/10609#discussioncomment-13461868
        "toc.md"]
    protocol_intro = []
    for intropart in protocols_intros_templates:
        with open(commond_dir / intropart, "r") as f:
            protocol_intro.append(f.read())
    protocol_intro = "\n".join(protocol_intro)
    created_template = protocol_intro + template_content
else:
    created_template = template_content

# 4) passing the content to Jinja
jinja_variables = common | user_input
environment = jinja2.Environment()
template = environment.from_string(created_template)
result = template.render(**jinja_variables)

# 5) output markdown to file
tmpfname = tempfile.mkstemp()[1]
with open(outfile_md, "w") as f:
    print(result, file=f)
    print(f"file {tmpfname} created")

# 6) if a docx is needed use pandoc
# pandoc = f"pandoc {tmpfname} --filter=pandoc-docx-pagebreakpy -f markdown -t docx -o {outfile}"
# pandoc = f"pandoc {tmpfname} --lua-filter filters/pagebreak.lua --toc -f markdown -t docx -o {outfile}"

if chosen_format == "docx":
    pandoc = f"pandoc {outfile_md} --lua-filter filters/pagebreak.lua" \
        f" --lua-filter=filters/toc-inject.lua" \
        f" -f markdown -t docx -o {outfile_docx}"
    subprocess.run(pandoc.split(" "))


# 7) prepare download
if chosen_format == "md":
    outfile = outfile_md
elif chosen_format == "docx":
    outfile = outfile_docx
else:
    raise Warning("Formato file non contemplato.")

with open(outfile, "rb") as f:
    btn = st.sidebar.download_button(
        label="Download",
        data=f,
        file_name=outfile.name)
