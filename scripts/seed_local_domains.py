"""Seed the local Bibek Enterprises domain row (idempotent).

Creates the `domains` + `domain_seo` rows the Bibek website resolves via
NEXT_PUBLIC_DOMAIN_SLUG=bibekenterprises, so the site renders domain data
from the database instead of built-in fallbacks.

Safe to re-run: existing domains are left untouched so Admin Dashboard edits
are never overwritten.

Run from the backend directory:
    PYTHONIOENCODING=utf-8 PYTHONUTF8=1 venv/Scripts/python -m scripts.seed_local_domains
"""
import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.domain import Domain, DomainSeo

DOMAINS = [
    {
        "name": "Bibek Enterprises",
        "slug": "bibekenterprises",
        "description": (
            "Professional home appliance repair and maintenance services — "
            "AC, refrigerator, washing machine, geyser, microwave and more, "
            "at your doorstep."
        ),
        "primary_color": "#1A3FA4",
        "meta_title": "Bibek Enterprises — Home Appliance Repair & Service",
        "meta_desc": (
            "Professional home appliance repair and maintenance services. "
            "AC, Refrigerator, Washing Machine, Geyser, Microwave & more — "
            "at your doorstep."
        ),
        "sort_order": 0,
    },
]


async def main() -> None:
    created = 0
    async with AsyncSessionLocal() as session:
        for data in DOMAINS:
            existing = (await session.execute(
                select(Domain).where(Domain.slug == data["slug"])
            )).scalar_one_or_none()
            if existing:
                print(f"[SKIP] Domain already exists: {existing.slug}")
                continue

            domain = Domain(**data)
            session.add(domain)
            await session.flush()
            session.add(DomainSeo(domain_id=domain.id))
            created += 1
            print(f"[OK] Domain created: {domain.slug}")

        if created:
            await session.commit()
        print(f"[DONE] {created} domain(s) created, {len(DOMAINS) - created} skipped")


if __name__ == "__main__":
    asyncio.run(main())
