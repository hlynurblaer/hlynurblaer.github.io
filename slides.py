"""
Slideshow slide definitions for the Iceland Fisheries map.

Each entry in SLIDES is one slide in the intro slideshow.
The generator reads this list in order — reorder, add, or remove
entries here and the HTML will update automatically.

Fields
------
  year  : int or None
      Which data-year to display on the map for this slide.
      Use None for intro/title slides that don't show a year or
      change the map state.
  title : str
      Heading shown in the narrative panel.
  body  : str
      Paragraph of explanatory text. Use triple-quoted strings
      so you can paste text straight in — the generator collapses
      all internal whitespace/newlines into a single space automatically.
"""

SLIDES = [
    {
        "year": None,
        "title": "Iceland's Fishing Heritage",
        "body": """
            The fishing industry has long been one of Iceland's main economic pillars. Over recent decades, the industry has undergone significant transformation driven by technological advances and shifts in governmental regulation. This visualization aims to provide a comprehensive view of that evolution.
        """,
    },
    {
        "year": None,
        "title": "Implementation of the Catch Quota System",
        "body": """
            After a turbulent period in the 1900s, marked by dramatic fluctuations in catch sizes and the disappearance of species due to overfishing and unsustainable practices, a new regulatory framework was introduced in 1984. The system assigned catch quotas to individual vessels, based on annual scientific assessments of species stock levels. Its motivation was to ensure both sustainability and stability for the industry. A highly controversial modification was implemented in 1990, permitting the free trade of these catch quotas and decoupling them from local communities. The result has been a concentration of quota ownership, leaving many smaller towns feeling abandoned. At the same time, this has introduced efficiencies of scale and enabled the industry's economic sustainability.
        """,
    },
    {
        "year": None,
        "title": "Prevaling Tensions",
        "body": """
            Still a topic of heated debate in Icelandic politics and culture, opponents portray the system as unjust, arguing that it favours economic elites at the expense of smaller, traditional fishing towns that have borne the consequences. Meanwhile, proponents point to the industry's increased overall revenue, as well as greater stability and predictability. Here we investigate the evolution of the industry, considering these diverse perspectives.
        """,
    },
    {
        "year": 1991,
        "title": "Free Trade of Catch Quotas Permitted",
        "body": """
            In 1990, free trade of catch quotas was permitted and in 1991 the first quota trades where perfomed. Until then, quotas had been tied to local communities and remained unchanged since the system's introduction, resulting in a relatively even distribution across the country.
        """,
    },
    {
        "year": 2007,
        "title": "Large Trades of Catch Quotas",
        "body": """
            In the years following the turn of the millennium, large-scale trades of catch quotas took place. The period was characterised by a significant concentration of quota ownership within fewer fishing companies.
        """,
    },
{
        "year": 2010,
        "title": "Catch Sizes Remain Volatile",
        "body": """
            Twenty years after its implementation, the catch quota system has not eliminated the volatility it was designed to address. Allocated stock sizes vary considerably, and the catch sizes of fishing companies follow.
        """,
    },
        {
        "year": 2016,
        "title": "Fishing Industry Enjoys Era of Steady Profits",
        "body": """
            Since the financial crisis of 2008, the industry has seen steady net profit and strong growth — a marked contrast to the pre-2005 period and the years before the catch quota system was introduced.
        """,
    },
    {
        "year": 2023,
        "title": "Catch Shifts to Eastern and South-Western Ports",
        "body": """
            From the mid-2010s and onward, catch volumes have increasingly concentrated around landing ports in the East and South-West. The shift becomes clear when comparing recent years like 2023 to the initial years of the 1980s and 1990s.
        """,
    },
]