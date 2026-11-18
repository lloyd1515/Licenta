"""Functii comune: extrag fragmente exacte din fisiere si le marcheaza cu <mark>."""
import html
import os
import re
import sys


def rx(t):
    return r"\s+".join(re.escape(w) for w in t.split())

IDF = os.path.expanduser("~/esp/esp-idf/components")
DOCS = os.path.expanduser("~/esp/esp-idf/docs/en/api-guides")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().split("\n")


def src(rel):
    return os.path.join(IDF, rel)


# Fiecare snippet: titlu, eticheta sursei, fisier, intervale [(a, b)] cu numere de linie (1 = prima),
# marcaje [(text_cautat_in_linie, text_de_marcat, explicatie)]
def snippet(title, label, path, ranges, marks, numbered=True, intro=None):
    lines = read(path)
    shown = []
    for i, (a, b) in enumerate(ranges):
        if i:
            shown.append((None, "..."))
        for n in range(a, b + 1):
            shown.append((n, lines[n - 1]))
    out_lines, notes, cursor = [], [], 0
    pending = list(marks)
    width = len(str(max(n for n, _ in shown if n))) if numbered else 0
    for idx, (n, text) in enumerate(shown):
        esc = html.escape(text)
        tags = []
        while pending:
            find, hl, expl = pending[0]
            if re.search(rx(find), text) and re.search(rx(html.escape(hl)), esc):
                esc = re.sub(rx(html.escape(hl)), lambda m: "<mark>" + m.group(0) + "</mark>", esc, count=1)
                notes.append(expl)
                tags.append("[%d]" % len(notes))
                pending.pop(0)
            else:
                break
        prefix = ("%*s | " % (width, n if n else "")) if numbered else ""
        out_lines.append(prefix + esc + ("  " + " ".join(tags) if tags else ""))
    if pending:
        raise SystemExit("marcaj negasit in %s: %r" % (title, pending[0][0]))
    md = ["### " + title, "", "Sursa: `%s`" % label, ""]
    if intro:
        md += [intro, ""]
    md += ["<pre>"] + out_lines + ["</pre>", ""]
    md += ["%d. %s" % (i + 1, t) for i, t in enumerate(notes)] + [""]
    return "\n".join(md)




def whole(path):
    return [(1, len([l for l in read(path)]) - (1 if read(path)[-1] == "" else 0))]
