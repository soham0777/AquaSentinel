#!/usr/bin/env python3
"""Read-only link and asset checker for the AquaSentinel repository.

It never modifies anything. It scans the files Git tracks (falls back to a directory walk outside a Git
checkout) and reports references that do not resolve:

  1. HTML / CSS / JS / Markdown links and embeds that point at a repo-relative file (href, src, srcset, url(...),
     markdown [text](path) and ![alt](path)).
  2. Absolute links to this repository: github.com/soham0777/AquaSentinel/(blob|tree|raw)/main/<path> and the
     GitHub Pages site soham0777.github.io/AquaSentinel/<path> (served from docs/).
  3. Backtick-quoted paths in Markdown (`docs/index.html`, `mechanical/src/build.py`) that look like repo paths.

Usage:   python tools/check_links.py [repo_root] [--json out.json] [--quiet]
Exit code: 0 = no broken references, 1 = at least one broken reference.
Only the Python standard library is used.
"""
import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote

SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".mp4", ".pdf", ".zip", ".glb", ".stl", ".step", ".stp", ".docx",
            ".sldprt", ".sldasm", ".ico", ".woff", ".woff2", ".ttf"}
TEXT_EXT = {".md", ".html", ".htm", ".css", ".js", ".py", ".ini", ".yml", ".yaml", ".json", ".txt", ".csv", ".h",
            ".cpp", ".c", ".sh", ".bat", ".ps1", ".toml", ".kicad_sch"}
PATH_EXT = r"(?:md|html|htm|css|js|py|ini|yml|yaml|json|csv|txt|h|cpp|png|jpg|jpeg|gif|mp4|pdf|zip|glb|stl|step|docx|sldprt|kicad_sch|sh)"
REPO = "soham0777/AquaSentinel"

RE_MD_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
RE_ATTR = re.compile(r"""(?:href|src|data-src|poster|data)\s*=\s*["']([^"']+)["']""", re.I)
RE_SRCSET = re.compile(r"""srcset\s*=\s*["']([^"']+)["']""", re.I)
RE_CSS_URL = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", re.I)
RE_JS_LOC = re.compile(r"""(?:fetch|import|Image\(\)\.src\s*=|window\.open|location\.href\s*=)\s*\(?\s*["']([^"']+)["']""")
RE_BACKTICK = re.compile(r"`([A-Za-z0-9_.\-/]+/[A-Za-z0-9_.\-]+\." + PATH_EXT + r")`")
RE_ABS = re.compile(r"https?://(?:www\.)?github\.com/" + REPO + r"/(?:blob|tree|raw)/[^/]+/([^\s)\"'>#?]+)", re.I)
RE_PAGES = re.compile(r"https?://soham0777\.github\.io/AquaSentinel/?([^\s)\"'>#?]*)", re.I)


def tracked_files(root):
    try:
        out = subprocess.check_output(["git", "-C", root, "ls-files", "-z"], stderr=subprocess.DEVNULL)
        return [p for p in out.decode("utf-8", "replace").split("\0") if p]
    except Exception:
        files = []
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in {".git", ".pio", "__pycache__", "private", "node_modules"}]
            for f in fs:
                files.append(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/"))
        return files


def is_external(ref):
    return bool(re.match(r"^(?:[a-z][a-z0-9+.\-]*:|//|#|\{\{|\$\{|%)", ref, re.I))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = os.path.abspath(args[0]) if args else os.getcwd()
    json_out = None
    if "--json" in sys.argv:
        json_out = sys.argv[sys.argv.index("--json") + 1]
        if json_out in args:
            args.remove(json_out)
            root = os.path.abspath(args[0]) if args else os.getcwd()
    quiet = "--quiet" in sys.argv

    files = tracked_files(root)
    fileset = set(files)
    dirset = set()
    for f in files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            dirset.add("/".join(parts[:i]))

    def exists(p):
        p = os.path.normpath(p).replace(os.sep, "/")
        if p in (".", ""):
            return True
        return p in fileset or p in dirset

    broken = []

    def check(src, kind, ref, base_dir=None, repo_rooted=False):
        ref0 = ref
        ref = unquote(ref.split("#")[0].split("?")[0]).strip()
        if not ref:
            return
        if repo_rooted:
            target = ref
        elif ref.startswith("/"):
            target = ref.lstrip("/")
        else:
            target = os.path.join(base_dir, ref)
        target = os.path.normpath(target).replace(os.sep, "/")
        if target.startswith(".."):
            broken.append((src, kind, ref0, "escapes repo"))
            return
        if not exists(target):
            broken.append((src, kind, ref0, target))

    for f in sorted(files):
        ext = os.path.splitext(f)[1].lower()
        if ext in SKIP_EXT or ext not in TEXT_EXT:
            continue
        if f.startswith("mechanical/cad/") and ext not in {".md"}:
            continue
        if f == "docs/viewer.html":
            continue  # generated; embeds a 1.4 MB model, scanned separately below for attributes only
        try:
            text = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        d = os.path.dirname(f)
        if ext == ".md":
            for m in RE_MD_LINK.finditer(text):
                r = m.group(1)
                if not is_external(r):
                    check(f, "md-link", r, d)
            for m in RE_ATTR.finditer(text):
                r = m.group(1)
                if not is_external(r):
                    check(f, "html-attr", r, d)
            for m in RE_BACKTICK.finditer(text):
                r = m.group(1)
                # backticked paths are written either from the repo root or relative to the file
                rr = os.path.normpath(r).replace(os.sep, "/")
                rel = os.path.normpath(os.path.join(d, r)).replace(os.sep, "/")
                if not (exists(rr) or exists(rel)):
                    broken.append((f, "backtick-path", r, "not at repo root or relative to file"))
        elif ext in {".html", ".htm"}:
            for m in RE_ATTR.finditer(text):
                r = m.group(1)
                if not is_external(r):
                    check(f, "html-attr", r, d)
            for m in RE_SRCSET.finditer(text):
                for part in m.group(1).split(","):
                    r = part.strip().split(" ")[0]
                    if r and not is_external(r):
                        check(f, "srcset", r, d)
            for m in RE_CSS_URL.finditer(text):
                r = m.group(1)
                if not is_external(r) and not r.startswith("data:"):
                    check(f, "css-url", r, d)
            for m in RE_JS_LOC.finditer(text):
                r = m.group(1)
                if not is_external(r) and re.search(r"\.[a-z0-9]{2,5}$", r.split("?")[0], re.I):
                    check(f, "js-ref", r, d)
        elif ext == ".css":
            for m in RE_CSS_URL.finditer(text):
                r = m.group(1)
                if not is_external(r) and not r.startswith("data:"):
                    check(f, "css-url", r, d)
        elif ext == ".js":
            for m in RE_JS_LOC.finditer(text):
                r = m.group(1)
                if not is_external(r) and re.search(r"\.[a-z0-9]{2,5}$", r.split("?")[0], re.I):
                    check(f, "js-ref", r, d)
        # absolute links to this repo / its Pages site
        for m in RE_ABS.finditer(text):
            check(f, "github-abs", m.group(1), repo_rooted=True)
        for m in RE_PAGES.finditer(text):
            sub = m.group(1)
            check(f, "pages-abs", ("docs/" + sub) if sub else "docs/index.html", repo_rooted=True)

    # docs/viewer.html is generated and large: check only its src/href attributes and absolute links
    vf = "docs/viewer.html"
    if vf in fileset:
        text = open(os.path.join(root, vf), encoding="utf-8", errors="replace").read()
        for m in RE_ATTR.finditer(text):
            r = m.group(1)
            if not is_external(r) and len(r) < 200:
                check(vf, "html-attr", r, "docs")
        for m in RE_ABS.finditer(text):
            check(vf, "github-abs", m.group(1), repo_rooted=True)

    broken = sorted(set(broken))
    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            json.dump([dict(file=b[0], kind=b[1], ref=b[2], target=b[3]) for b in broken], fh, indent=1)
    if not quiet:
        for b in broken:
            print(f"BROKEN [{b[1]}] {b[0]}: {b[2]}  ->  {b[3]}")
    print(f"checked {len(files)} tracked files; broken references: {len(broken)}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
