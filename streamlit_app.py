import jinja2
import tempfile
import streamlit as st

# File uploader
xlsx = st.file_uploader(label = "Fai l'upload del file struttura qui, dopodiché clicca su 'Download CRF'.",
                        type = ["xlsx"],
                        accept_multiple_files = False)

if xlsx is not None:
    struc = tempfile.NamedTemporaryFile(suffix = '.xlsx')
    out = tempfile.NamedTemporaryFile(suffix = '.xlsx')
    strucfile = struc.name
    outfile = out.name
    # salvo per comodità il file in un file
    with open(strucfile, "wb") as f:
        f.write(xlsx.getbuffer())
    crf = CRF()
    crf.read_structure(strucfile)
    crf.create(outfile)
    with open(outfile, "rb") as f:
        btn = st.download_button(
            label = "Download CRF",
            data = f,
            file_name = "crf.xlsx")
    
# Include README
with open('frontpage.md', 'r') as fp:
    frontpage = fp.read()
st.markdown(frontpage)
        


# https://realpython.com/primer-on-jinja-templating/
from pathlib import Path
import datetime as dt
import subprocess
import tempfile

path = Path("jinja_templates") / "spirit2025.md"
with open(path, "r") as f:
    content = f.read()


variables = {
    "TODAY": dt.date.today().isoformat(),
    "ACRONIMO_STUDIO": "ACRONIMORCT"
}

environment = jinja2.Environment()
template = environment.from_string(content)
result = template.render(**variables)

tmpf = tempfile.mkstemp()
tmpfname = tmpf[1]

with open(tmpfname, "w") as f:
    print(result, file=f)
    print(f"file {tmpfname} created")


outfile = Path(f"/tmp/{variables["ACRONIMO_STUDIO"]}_study_protocol.docx")
subprocess.run(["pandoc", tmpfname, "-f", "gfm", "-t", "docx", "-o", str(outfile)])
