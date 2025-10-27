package codex.guard

default allow = false

# only owner may run glyphs in prod (example)
allow {
  input.role == "owner"
  input.route == "/glyph"
}
deny[msg] {
  contains(input.glyph, "DROP DATABASE")
  msg := "sql destructive pattern"
}
