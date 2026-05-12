"""
Map highlight-box definitions for the Iceland Fisheries map.

Each entry in ANNOTATIONS places a rounded, transparent highlight
box centred on a port, with a small "*" star in the top-left corner.
No text is rendered inside the box — it is purely a visual callout.

The generator resolves port names to coordinates via
iceland_towns_coordinates.csv — you only need the port name.

Fields
------
  year : int
      The data-year this highlight is visible for.
  port : str
      Port name (must match the coords file exactly).
  size : int
      Box width and height in pixels. Tweak this per entry to
      get the right visual coverage on the map (default ~80).
"""

ANNOTATIONS = [
        {
        "slide": 7,
        "port": "Vestmannaeyjar",
        "size": 80,
    },
            {
        "slide": 7,
        "port": "Neskaupstaður",
        "size": 100,
    },
    # ── Add more entries below ─────────────────────────────────────────
    # {
    #     "slide": 2,       # slides.py index 2 → "Turn of the Millennium" (2000)
    #     "port": "Akureyri",
    #     "size": 80,
    # },
]