"""Fill the local Bibek Enterprises domain profile (idempotent).

Populates support contact, office address and social links so the website's
header, footer, contact sections and LocalBusiness schema render from the DB.

Only EMPTY fields are filled — existing Admin Dashboard values are never
overwritten. Re-running is therefore safe.

NOTE: the contact details and social URLs below match the supplied homepage
design and are local-development values. Verify them in Admin Dashboard ->
Domains -> Profile before production.

Run AFTER `scripts.seed_local_domains`:
    PYTHONIOENCODING=utf-8 PYTHONUTF8=1 venv/Scripts/python -m scripts.seed_local_profiles
"""
import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.domain import Domain, DomainProfile

PROFILES = {
    "bibekenterprises": {
        "support_phone": "+91 9777260631",
        "support_email": "support@bibekenterprises.com",
        "office_address": "Plot No. 977/962, Jagyeswara Patana, Kapila Prasad, Old Town, Bhubaneswar",
        "office_city": "Bhubaneswar",
        "office_state": "Odisha",
        "office_pincode": "751002",
        "office_country": "India",
        "facebook_url": "https://www.facebook.com/bibekenterprises",
        "instagram_url": "https://www.instagram.com/bibekenterprises",
        "youtube_url": "https://www.youtube.com/@bibekenterprises",
        "linkedin_url": "https://www.linkedin.com/company/bibekenterprises",
    },
}


async def main() -> None:
    filled_total = 0
    async with AsyncSessionLocal() as session:
        for slug, values in PROFILES.items():
            domain = (await session.execute(
                select(Domain).where(Domain.slug == slug)
            )).scalar_one_or_none()
            if not domain:
                raise SystemExit(
                    f"Domain '{slug}' not found — run scripts.seed_local_domains first"
                )

            profile = (await session.execute(
                select(DomainProfile).where(DomainProfile.domain_id == domain.id)
            )).scalar_one_or_none()
            if not profile:
                profile = DomainProfile(domain_id=domain.id)
                session.add(profile)
                await session.flush()

            filled = 0
            for field, value in values.items():
                if value and not getattr(profile, field):
                    setattr(profile, field, value)
                    filled += 1
            filled_total += filled
            print(f"[OK] {slug}: filled {filled} empty profile field(s)")

        await session.commit()
        print(f"[DONE] {filled_total} profile field(s) filled")


if __name__ == "__main__":
    asyncio.run(main())
