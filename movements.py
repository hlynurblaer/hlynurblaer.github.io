"""
Movement arrow definitions for the Iceland Fisheries map.

Each entry in MOVEMENTS defines an arrow drawn on the map during
the slideshow or at a given year.  The generator resolves port names
to coordinates via iceland_towns_coordinates.csv automatically —
you only need to type the port name exactly as it appears in that file.

Fields
------
  year     : int
      The data-year this movement is associated with.
      The arrow is visible when the map shows this year.
  species  : str
      Fish species name shown on the arrow label.
  vessel   : str or None
      Vessel name (optional context, shown in tooltip).
  company  : str or None
      Company name (optional context, shown in tooltip).
  share    : float
      Numeric share/amount — displayed on the arrow label.
      Use whatever unit makes sense (tonnes, %, etc.).
  unit     : str
      Unit string for the share value (e.g. "tonnes", "%", "th. ISK").
  origin   : str
      Port name where the arrow starts (must match coords file).
  destination : str
      Port name where the arrow ends (must match coords file).
  color    : str or None
      Optional hex color for this arrow.  If None the generator
      picks a default based on species.

Body text and share are displayed as a label on the arrow midpoint:
    "Herring · 8,871 tonnes"

You can paste entries freely — triple-quote strings if you like.
Reorder, add, or remove entries and the HTML updates automatically.
"""

MOVEMENTS = [
    {
        "year": 2007,
        "species": "Herring",
        "vessel": None,
        "company": "Síldarvinnslan hf. → Samherji hf.",
        "share": 8.870579,
        "unit": "%",
        "origin": "Neskaupstaður",
        "destination": "Akureyri",
        "color": None,
    },
    {
        "year": 2022,
        "species": "Capelin",
        "vessel": None,
        "company": "Brim hf. → Útgerðarfélag Reykjavíkur hf.",
        "share": 5.840000,
        "unit": "%",
        "origin": "Reykjavík",
        "destination": "Reykjavík",
        "color": None,
    },
    {
        "year": 2001,
        "species": "Herring",
        "vessel": None,
        "company": "Skinney-Þinganes hf. → Þingey ehf.",
        "share": 5.662441,
        "unit": "%",
        "origin": "Höfn",
        "destination": "Húsavík",
        "color": None,
    },
    {
        "year": 2016,
        "species": "Herring",
        "vessel": None,
        "company": "Vinnslustöðin hf. → Brim hf.",
        "share": 5.545482,
        "unit": "%",
        "origin": "Vopnafjörður",
        "destination": "Reykjavík",
        "color": None,
    },
    {
        "year": 2022,
        "species": "Herring",
        "vessel": None,
        "company": "Vinnslustöðin hf. → Síldarvinnslan hf.",
        "share": 5.545387,
        "unit": "%",
        "origin": "Vopnafjörður",
        "destination": "Neskaupstaður",
        "color": None,
    },
    {
        "year": 2004,
        "species": "Herring",
        "vessel": None,
        "company": "Festarfell ehf → Gjögur hf.",
        "share": 3.577336,
        "unit": "%",
        "origin": "Reyðarfjörður",
        "destination": "Norðurfjörður",
        "color": None,
    },
    {
        "year": 2007,
        "species": "Herring",
        "vessel": None,
        "company": "Þingey ehf. → Langanes hf",
        "share": 3.444148,
        "unit": "%",
        "origin": "Húsavík",
        "destination": "Þórshöfn",
        "color": None,
    },
    {
        "year": 2008,
        "species": "Herring",
        "vessel": None,
        "company": "Skinney-Þinganes hf. → Síldarvinnslan hf.",
        "share": 3.345482,
        "unit": "%",
        "origin": "Höfn",
        "destination": "Neskaupstaður",
        "color": None,
    },
    {
        "year": 2005,
        "species": "Herring",
        "vessel": None,
        "company": "Þingey ehf. → Skinney-Þinganes hf.",
        "share": 3.327389,
        "unit": "%",
        "origin": "Húsavík",
        "destination": "Höfn",
        "color": None,
    },
    {
        "year": 2004,
        "species": "Herring",
        "vessel": None,
        "company": "Síldarvinnslan hf. → Þingey ehf.",
        "share": 3.327289,
        "unit": "%",
        "origin": "Neskaupstaður",
        "destination": "Húsavík",
        "color": None,
    },
    {
        "year": 2001,
        "species": "Herring",
        "vessel": None,
        "company": "Skinney-Þinganes hf. → Thorfish ehf.",
        "share": 3.327289,
        "unit": "%",
        "origin": "Höfn",
        "destination": "Grindavík",
        "color": None,
    },
    {
        "year": 2010,
        "species": "Herring",
        "vessel": None,
        "company": "Skinney-Þinganes hf. → Vinnslustöðin hf.",
        "share": 3.327289,
        "unit": "%",
        "origin": "Höfn",
        "destination": "Vopnafjörður",
        "color": None,
    },
    {
        "year": 2005,
        "species": "Capelin",
        "vessel": None,
        "company": "Gjögur hf. → Þingey ehf.",
        "share": 3.122792,
        "unit": "%",
        "origin": "Norðurfjörður",
        "destination": "Húsavík",
        "color": None,
    },
    {
        "year": 2022,
        "species": "Mackerel",
        "vessel": None,
        "company": "Runólfur Hallfreðsson ehf. → Síldarvinnslan hf.",
        "share": 3.042398,
        "unit": "%",
        "origin": "Vestmannaeyjar",
        "destination": "Neskaupstaður",
        "color": None,
    },
    {
        "year": 2021,
        "species": "Mackerel",
        "vessel": None,
        "company": "Ísfélag hf. → Fiskistofa",
        "share": 3.000000,
        "unit": "%",
        "origin": "Akureyri",
        "destination": "Hafnarfjörður",
        "color": None,
    },
    {
        "year": 2016,
        "species": "Haddock",
        "vessel": None,
        "company": "Útgerðarfélag Reykjavíkur hf. → KG Fiskverkun ehf.",
        "share": 2.855746,
        "unit": "%",
        "origin": "Reykjavík",
        "destination": "Keflavík",
        "color": None,
    },
    {
        "year": 2012,
        "species": "Cod",
        "vessel": None,
        "company": "Útgerðarfélag Reykjavíkur hf. → Útgerðarfélag Akureyringa ehf.",
        "share": 2.332279,
        "unit": "%",
        "origin": "Reykjavík",
        "destination": "Akureyri",
        "color": None,
    },
    {
        "year": 1999,
        "species": "Herring",
        "vessel": None,
        "company": "Arney ehf → Haraldur Böðvarsson hf",
        "share": 2.218193,
        "unit": "%",
        "origin": "Ísafjörður",
        "destination": "Bolungarvík",
        "color": None,
    },
    {
        "year": 2020,
        "species": "Herring",
        "vessel": None,
        "company": "Vinnslustöðin hf. → Huginn ehf.",
        "share": 2.218193,
        "unit": "%",
        "origin": "Vopnafjörður",
        "destination": "Dalvík",
        "color": None,
    },
    {
        "year": 2003,
        "species": "Herring",
        "vessel": None,
        "company": "Skinney-Þinganes hf. → Pétur Stefánsson",
        "share": 2.218193,
        "unit": "%",
        "origin": "Höfn",
        "destination": "Siglufjörður",
        "color": None,
    },
    {
        "year": 1999,
        "species": "Herring",
        "vessel": None,
        "company": "Arney ehf → Samherji hf.",
        "share": 2.218193,
        "unit": "%",
        "origin": "Ísafjörður",
        "destination": "Akureyri",
        "color": None,
    },
    {
        "year": 2001,
        "species": "Herring",
        "vessel": None,
        "company": "BGB-Snæfell hf → Samherji hf.",
        "share": 2.218193,
        "unit": "%",
        "origin": "Grundarfjörður",
        "destination": "Akureyri",
        "color": None,
    },
    {
        "year": 2019,
        "species": "Herring",
        "vessel": None,
        "company": "Huginn ehf. → Vinnslustöðin hf.",
        "share": 2.218193,
        "unit": "%",
        "origin": "Dalvík",
        "destination": "Vopnafjörður",
        "color": None,
    },
    {
        "year": 1991,
        "species": "Cod",
        "vessel": None,
        "company": "Hólanes hf → Miðfell hf",
        "share": 0.137037,
        "unit": "%",
        "origin": "Ólafsfjörður",
        "destination": "Akranes",
        "color": None,
    },
    {
        "year": 1991,
        "species": "Haddock",
        "vessel": None,
        "company": "Nökkvi → Fáfnir ehf",
        "share": 0.119430,
        "unit": "%",
        "origin": "Reykjavík",
        "destination": "Þingeyri",
        "color": None,
    },
    {
        "year": 1991,
        "species": "Cod",
        "vessel": None,
        "company": "Farsæll ehf → Ísfélag hf.",
        "share": 0.099406,
        "unit": "%",
        "origin": "Vestmannaeyjar",
        "destination": "Akureyri",
        "color": None,
    },
]