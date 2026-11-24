"""Rebuild events/index.html and events/live.html from src/ (run from airtribune-redesign/)."""
H = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
for src, out, body in [("src/season-calendar.html", "events/index.html", False), ("src/live-tracker.html", "events/live.html", True)]:
    s = open(src).read().rstrip("\n") + "\n"
    b = H + s
    if body:
        b = b.replace("</style>", "</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n"
    else:
        b += "</html>\n"
    open(out, "w").write(b)
    print("wrote", out)
