"""Seed geographic zones and assign existing local service areas (idempotent).

Creates a practical zone structure for each Bibek Enterprises service city and
links the seeded localities to their zone. Safe to re-run:

- Existing zones (matched by name within the city) are never modified.
- Only areas with no zone assignment are linked, so manual Admin Dashboard
  assignments are preserved.

Run from the backend directory:
    PYTHONIOENCODING=utf-8 PYTHONUTF8=1 venv/Scripts/python -m scripts.seed_local_zones
"""
import asyncio

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.city import Area, City, Zone

ZONES = {
    "Bhubaneswar": [
        {
            "name": "North Bhubaneswar",
            "description": "Patia, Chandrasekharpur, Jaydev Vihar and nearby neighbourhoods.",
            "areas": ["Patia", "Chandrasekharpur", "Jaydev Vihar", "Rasulgarh"],
        },
        {
            "name": "Central Bhubaneswar",
            "description": "Saheed Nagar, Satya Nagar, Unit 8 and the old city core.",
            "areas": ["Saheed Nagar", "Satya Nagar", "Unit 8", "Old Town"],
        },
        {
            "name": "West Bhubaneswar",
            "description": "Nayapalli, Khandagiri and adjoining western localities.",
            "areas": ["Nayapalli", "Khandagiri"],
        },
        {
            "name": "South Bhubaneswar",
            "description": "Sundarpada, Tamando and the southern approach areas.",
            "areas": ["Sundarpada", "Tamando"],
        },
    ],
    "Cuttack": [
        {
            "name": "North Cuttack",
            "description": "Badambadi, Madhupatna and the northern city belt.",
            "areas": ["Badambadi", "Madhupatna"],
        },
        {
            "name": "Central Cuttack",
            "description": "College Square, Buxi Bazaar and the central business areas.",
            "areas": ["College Square", "Buxi Bazaar", "Choudhury Bazaar", "Link Road", "Ranihat"],
        },
        {
            "name": "South Cuttack",
            "description": "Bidanasi, Tulsipur and the southern neighbourhoods.",
            "areas": ["Bidanasi", "Tulsipur"],
        },
    ],
    "Puri": [
        {
            "name": "Central Puri",
            "description": "Grand Road, Station Road and the town-centre localities.",
            "areas": ["Grand Road", "Station Road", "Mangalabag", "VIP Road"],
        },
        {
            "name": "Puri Beachside",
            "description": "Sea Beach Road, Baliapanda and Chakratirtha Road.",
            "areas": ["Sea Beach Road", "Baliapanda", "Chakratirtha Road"],
        },
    ],
    "Berhampur": [
        {
            "name": "North Berhampur",
            "description": "Gandhi Nagar, Hillpatna and Engineering School Road.",
            "areas": ["Gandhi Nagar", "Hillpatna", "Engineering School Road"],
        },
        {
            "name": "Central Berhampur",
            "description": "Bada Bazar, Kamapalli and the central market area.",
            "areas": ["Bada Bazar", "Kamapalli"],
        },
        {
            "name": "South Berhampur",
            "description": "Gosaninuagaon, Lanjipalli and Ankuli.",
            "areas": ["Gosaninuagaon", "Lanjipalli", "Ankuli"],
        },
    ],
}


async def main() -> None:
    zones_created = 0
    areas_linked = 0
    areas_skipped = 0

    async with AsyncSessionLocal() as session:
        for city_name, city_zones in ZONES.items():
            city = (await session.execute(
                select(City).where(City.name == city_name)
            )).scalar_one_or_none()
            if not city:
                print(f"[WARN] City not found, skipped: {city_name}")
                continue

            for data in city_zones:
                zone = (await session.execute(
                    select(Zone).where(
                        Zone.city_id == city.id,
                        func.lower(Zone.name) == data["name"].casefold(),
                    )
                )).scalar_one_or_none()

                if zone:
                    print(f"[SKIP] Zone already exists: {city_name} / {zone.name}")
                else:
                    zone = Zone(
                        city_id=city.id,
                        name=data["name"],
                        description=data["description"],
                        is_active=True,
                    )
                    session.add(zone)
                    await session.flush()
                    zones_created += 1
                    print(f"[OK] Zone created: {city_name} / {zone.name}")

                linked = 0
                skipped = 0
                for area_name in data["areas"]:
                    area = (await session.execute(
                        select(Area).where(
                            Area.city_id == city.id,
                            func.lower(Area.name) == area_name.casefold(),
                        )
                    )).scalar_one_or_none()
                    if not area:
                        print(f"[WARN] Area not found, skipped: {city_name} / {area_name}")
                        continue
                    if area.zone_id is None:
                        area.zone_id = zone.id
                        linked += 1
                    else:
                        skipped += 1

                areas_linked += linked
                areas_skipped += skipped
                print(f"     {linked} area(s) linked, {skipped} already zoned")

        if zones_created or areas_linked:
            await session.commit()

    print(
        f"[DONE] {zones_created} zone(s) created, {areas_linked} area(s) linked, "
        f"{areas_skipped} area(s) left in their existing zone"
    )


if __name__ == "__main__":
    asyncio.run(main())
