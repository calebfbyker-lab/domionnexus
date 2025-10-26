// TSG (Triune Symbolic Glyph) Parser
export function parseTSG(src) {
  const lines = src.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
  const out = [];
  let cur = null;
  
  for (const ln of lines) {
    if (ln.startsWith("SEAL ")) {
      if (cur) out.push(cur);
      cur = { name: ln.replace(/^SEAL\s+/, ""), props: {} };
      continue;
    }
    if (!cur) continue;
    if (ln === "}" || ln === "};") {
      out.push(cur);
      cur = null;
      continue;
    }
    const m = ln.match(/^([A-Z_]+)\s*:\s*(.+)$/);
    if (m) cur.props[m[1]] = m[2];
  }
  if (cur) out.push(cur);
  return out;
}

export function compileTSG(ast) {
  return ast.map(seal => {
    const lines = [`SEAL ${seal.name}`];
    for (const [key, val] of Object.entries(seal.props)) {
      lines.push(`  ${key}: ${val}`);
    }
    lines.push('};');
    return lines.join('\n');
  }).join('\n\n');
}
