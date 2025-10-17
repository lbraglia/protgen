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

active_templates = {
    "SPIRIT 2025 (studi sperimentali)": "spirit2025.md",
    "STROBE 2007 (studi osservazionali)": "strobe2007.md",
    "STARD 2015 (studi diagnostici)": "stard2015.md",
    "Template agnostico, italiano, semplice": "old_ctsu.md"
}

# statistici_attivi = {
#     "": "",
#     "Debora": "Debora Formisano",
#     "Luca": "Luca Braglia"
# }

# User data input
# ----------------
st.text_input("**Acronimo studio**", key="ACRONIMO_STUDIO")

chosen_template = st.selectbox("**Template adottato**",
                               active_templates.keys())
template_path = template_dir / active_templates[chosen_template]
with open(template_path, "r") as f:
    content = f.read()

st.markdown("**Opzioni**")
farmacologico = st.checkbox("Farmacologico")


# statistico = st.selectbox("**Statistico**", statistici_attivi.keys())


template_specific = {}

# Jinja magic
# -----------
acronimo_studio = st.session_state.ACRONIMO_STUDIO
user_input = {
    "ACRONIMO_STUDIO": acronimo_studio
}
common = {
    "TODAY": dt.date.today().isoformat(),
    "PROTOCOL_VERSION": 1,
    "STUDIO_FARMACOLOGICO": farmacologico,
    # "STATISTICO": statistico
}

jinja_variables = user_input | common | template_specific
environment = jinja2.Environment()
template = environment.from_string(content)
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
pandoc = f"pandoc {tmpfname} -f gfm -t docx -o {outfile}".split(" ")
subprocess.run(pandoc)


with open(outfile, "rb") as f:
    btn = st.download_button(
        label="Download Protocol",
        data=f,
        file_name=outfile.name)
