"""Seed common service localities for the local Bibek Enterprises database.

Adds a practical starting set of areas/localities for each serviceable city.
Safe to re-run: areas already present in a city (matched case-insensitively by
name) are skipped, so Admin Dashboard edits and later additions are preserved.

Run from the backend directory:
    PYTHONIOENCODING=utf-8 PYTHONUTF8=1 venv/Scripts/python -m scripts.seed_local_areas
"""
import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.city import Area, City

AREAS = {
    "Bhubaneswar": [
        ("Patia", "751024"),
        ("Chandrasekharpur", "751016"),
        ("Jaydev Vihar", "751013"),
        ("Saheed Nagar", "751007"),
        ("Satya Nagar", "751007"),
        ("Nayapalli", "751012"),
        ("Unit 8", "751012"),
        ("Khandagiri", "751030"),
        ("Old Town", "751002"),
        ("Sundarpada", "751002"),
        ("Rasulgarh", "751010"),
        ("Tamando", "752054"),
    ],
    "Cuttack": [
        ("Badambadi", "753012"),
        ("College Square", "753003"),
        ("Buxi Bazaar", "753001"),
        ("Choudhury Bazaar", "753001"),
        ("Link Road", "753012"),
        ("Ranihat", "753007"),
        ("Bidanasi", "753014"),
        ("Madhupatna", "753010"),
        ("Tulsipur", "753008"),
    ],
    "Puri": [
        ("Grand Road", "752001"),
        ("Sea Beach Road", "752001"),
        ("Station Road", "752001"),
        ("VIP Road", "752001"),
        ("Mangalabag", "752001"),
        ("Baliapanda", "752001"),
        ("Chakratirtha Road", "752002"),
    ],
    "Berhampur": [
        ("Gandhi Nagar", "760001"),
        ("Bada Bazar", "760002"),
        ("Gosaninuagaon", "760003"),
        ("Kamapalli", "760004"),
        ("Hillpatna", "760005"),
        ("Lanjipalli", "760008"),
        ("Ankuli", "760010"),
        ("Engineering School Road", "760010"),
    ],
}


async def main() -> None:
    created_total = 0
    skipped_total = 0

    async with AsyncSessionLocal() as session:
        for city_name, localities in AREAS.items():
            city = (await session.execute(
                select(City).where(City.name == city_name)
            )).scalar_one_or_none()
            if not city:
                print(f"[WARN] City not found, skipped: {city_name}")
                continue

            existing = {
                name.casefold()
                for name in (await session.execute(
                    select(Area.name).where(Area.city_id == city.id)
                )).scalars()
            }

            created = 0
            skipped = 0
            for name, pincode in localities:
                if name.casefold() in existing:
                    skipped += 1
                    continue
                session.add(Area(
                    city_id=city.id,
                    name=name,
                    pincode=pincode,
                    is_active=True,
                ))
                existing.add(name.casefold())
                created += 1

            created_total += created
            skipped_total += skipped
            print(f"[OK] {city_name}: {created} created, {skipped} already present")

        if created_total:
            await session.commit()

    print(f"[DONE] {created_total} area(s) created, {skipped_total} skipped")


if __name__ == "__main__":
    asyncio.run(main())
