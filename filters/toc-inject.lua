--[[
  toc-inject.lua
  Version: v0.1
  Author: ChatGPT (OpenAI)
  Description:
    Pandoc Lua filter to inject a live, updatable Word Table of Contents
    at the “[TOC]” placeholder in your Markdown when exporting to DOCX.
    Honors a `toc-heading-depth` metadata field (default 3).

  Features:
    - Replaces a paragraph containing exactly “[TOC]” with a true Word TOC field
      (`<w:fldSimple>`) marked dirty so Word prompts “Update fields?” on open
    - `toc-heading-start` and `toc-heading-stop` control the TOC levels (default 1-3)

  Usage example:
    pandoc input.md \
      --lua-filter=toc-inject.lua \
      --reference-doc=reference.docx \
      -M toc-heading-start=4 \
      -M toc-heading-depth=4 \
      -o output.docx
]]

local DEFAULT_LEVEL_START = 1
local DEFAULT_LEVEL_STOP = 3

function Pandoc(doc)
  start = DEFAULT_LEVEL_START
  stop = DEFAULT_LEVEL_STOP

  local hstart = doc.meta["toc-heading-start"]
  if hstart then start = tonumber(pandoc.utils.stringify(hstart)) end
  local hstop = doc.meta["toc-heading-stop"]
  if hstop then stop = tonumber(pandoc.utils.stringify(hstop)) end
  --print("DEBUG Pandoc: %s-%s", start, stop)

  local newblocks = {}
  for _, blk in ipairs(doc.blocks) do
    if blk.t == "Para" and pandoc.utils.stringify(blk) == "[TOC]" then
      -- build the TOC field with the chosen depth
      local raw = string.format([[
<w:p>
  <w:fldSimple w:instr="TOC \o &quot;%d-%d&quot; \h \z \u" w:dirty="true">
    <w:r>
      <w:rPr><w:noProof/></w:rPr>
      <w:t>Table of Contents</w:t>
    </w:r>
  </w:fldSimple>
</w:p>
]], start, stop)
      table.insert(newblocks, pandoc.RawBlock("openxml", raw))
    else
      table.insert(newblocks, blk)
    end
  end

  -- replace the document's blocks and return
  doc.blocks = newblocks
  return doc
end