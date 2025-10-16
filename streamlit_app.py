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

# User data input
st.text_input("**Acronimo studio**", key="ACRONIMO_STUDIO")


available_templates = {
    "SPIRIT2025 (studi sperimentali)": "spirit2025.md",
    "STROBE (studi osservazionali)": "strobe2010.md",
    "STARD (studi diagnostici)": "stard2015.md"
}
chosen_template = st.selectbox("**Template adottato**", available_templates.keys())
template_path = template_dir / available_templates[chosen_template]
with open(template_path, "r") as f:
    content = f.read()


# Jinja magic
variables = {
    "TODAY": dt.date.today().isoformat(),
    "ACRONIMO_STUDIO": st.session_state.ACRONIMO_STUDIO
}
environment = jinja2.Environment()
template = environment.from_string(content)
result = template.render(**variables)

tmpf = tempfile.mkstemp()
tmpfname = tmpf[1]

with open(tmpfname, "w") as f:
    print(result, file=f)
    print(f"file {tmpfname} created")


# pandoc
outfile = Path(f"/tmp/{variables["ACRONIMO_STUDIO"]}_study_protocol.docx")
pandoc = ["pandoc", tmpfname, "-f", "gfm", "-t", "docx", "-o", str(outfile)]
subprocess.run(pandoc)


with open(outfile, "rb") as f:
    btn = st.download_button(
        label="Download Protocol",
        data=f,
        file_name="protocol_template.docx")


