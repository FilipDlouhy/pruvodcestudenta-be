# Reference data: two cities and the eight sections of the live site (pruvodcestudenta.utb.cz, October 2026).

from dataclasses import dataclass

from django.db import transaction

from apps.guide.dtos import SeedResult
from apps.guide.models import Location, Section

LOCATION_NAMES = ["Zlín", "Uherské Hradiště"]


@dataclass(frozen=True)
class SectionSeed:
    """Text of one seeded section."""

    title: str
    slug: str
    description: str
    color: str
    icon: str


SECTION_SEEDS = [
    SectionSeed(
        title="Software univerzity",
        slug="software",
        description="",
        color="#ffdec9",
        icon="https://pruvodcestudenta.utb.cz/backend/public/icons/software-univerzity.svg",
    ),
    SectionSeed(
        title="Volný čas",
        slug="zivot-ve-zline",
        description="<p>Trávit čas jen ve škole a v knihovně není to pravé. Pokud chceš podniknout i něco dalšího, v této sekci narazíš na různé možnosti, co ve Zlíně podnikat.</p>",
        color="#fda6a4",
        icon="https://pruvodcestudenta.utb.cz/backend/public/icons/volny-cas.svg",
    ),
    SectionSeed(
        title="Studentské organizace",
        slug="studentske-organizace",
        description="<p>Chceš být vedle své výuky i součástí něčeho dalšího? Pak je tu řada studentských organizací, které na naší univerzitě působí a jejichž součástí můžeš být.</p>",
        color="#ffe793",
        icon="https://pruvodcestudenta.utb.cz/backend/public/icons/studentske-organizace.svg",
    ),
    SectionSeed(
        title="Kam na jídlo, kávu či pivo",
        slug="kam-na-jidlo",
        description="<p>Všemi milovaná menza bohužel nemá otevřeno neustále a tak Ti tady přinášíme výběr podniků, které stojí za to navštívit.</p>",
        color="#e9c6ff",
        icon="https://pruvodcestudenta.utb.cz/backend/public/icons/jidlo-kava-pivo.svg",
    ),
    SectionSeed(
        title="Praktické rady",
        slug="prakticke-rady",
        description="<p>Zde jsme pro tebe nachystali další informace užitečné do začátku studia.</p>",
        color="#ffe4f3",
        icon="https://pruvodcestudenta.utb.cz/backend/public/icons/prakticke-rady.svg",
    ),
    SectionSeed(
        title="Život na univerzitě",
        slug="zivot-na-univerzite",
        description="<p>Jako novopečený vysokoškolák by ses měl seznámit s&nbsp;tím, kdo univerzitu řídí, jak funguje a co vše je součástí univerzity.</p>",
        color="#acf0f9",
        icon="https://pruvodcestudenta.utb.cz/backend/public/icons/zivot-na-univerzite.svg",
    ),
    SectionSeed(
        title="Akademické poradny",
        slug="akademicke-poradny",
        description="<p>Univerzita není jen vzdělávací centrum. Pokud se během studia dostaneš do problémů, nabízí ti v rámci Univerzitního poradenského centra několik poraden, kde ti naši odborníci pomohou tvůj problém řešit.</p>",
        color="#bdf7b4",
        icon="https://pruvodcestudenta.utb.cz/backend/public/icons/akademicke-poradny.svg",
    ),
    SectionSeed(
        title="Studium",
        slug="studium",
        description="<p>Studium je to, proč jsi tady. Se studiem je spojena řada pojmů a pravidel. A právě zde jsme pro tebe nachystali přehled toho nejdůležitějšího.</p>",
        color="#f7567c",
        icon="https://pruvodcestudenta.utb.cz/backend/public/icons/studium.svg",
    ),
]


class SeedService:
    """Loads reference data into empty tables, so later admin edits and deletes are never overwritten."""

    def __init__(self, *, section_repository, location_repository):
        self.section_repository = section_repository
        self.location_repository = location_repository

    @transaction.atomic
    def seed_reference_data(self):
        location_count = 0
        if self.location_repository.count() == 0:
            for name in LOCATION_NAMES:
                self.location_repository.save(Location(name=name))
                location_count += 1
        section_count = 0
        if self.section_repository.count() == 0:
            for seed in SECTION_SEEDS:
                section = Section(
                    title=seed.title,
                    slug=seed.slug,
                    description=seed.description,
                    color=seed.color,
                    icon=seed.icon,
                )
                self.section_repository.save(section)
                section_count += 1
        return SeedResult(section_count=section_count, location_count=location_count)
