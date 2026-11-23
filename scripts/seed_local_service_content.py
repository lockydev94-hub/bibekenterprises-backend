"""Seed per-service includes, excludes and FAQs for local overrides.

Fills `includes_json`, `excludes_json` and `faqs_json` on every
`domain_service_overrides` row for the local domain. Content is matched by
service name and the FAQ copy mentions the domain's brand and service cities.

Only EMPTY fields are filled, so Admin Dashboard edits are never overwritten.

Run AFTER `scripts.seed_local_service_overrides`:
    PYTHONIOENCODING=utf-8 PYTHONUTF8=1 venv/Scripts/python -m scripts.seed_local_service_content
"""
import asyncio
import json

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.domain import Domain, DomainService, DomainServiceOverride
from app.models.service import Service

SITES = {
    "bibekenterprises": "Bibek Enterprises",
}

AREAS = "Bhubaneswar, Cuttack, Puri and Berhampur"

CONTENT = {
    "Air Conditioner Repair": {
        "includes": [
            "Doorstep technician visit and fault diagnosis",
            "Inspection of cooling, electrical and drainage components",
            "Minor adjustments and performance testing",
            "Transparent estimate before any part replacement",
            "Post-service test and work-area cleanup",
        ],
        "excludes": [
            "Replacement parts and refrigerant (quoted separately)",
            "Major PCB or compressor replacement",
            "Wall cutting, civil or carpentry work",
            "Workshop transport for sealed-system repair",
            "Extended warranty on spare parts",
        ],
        "faqs": [
            ("What is covered in an AC repair visit?",
             "A certified technician diagnoses the unit, checks cooling, electrical and drainage components, performs minor adjustments, and shares a clear estimate before any paid part replacement."),
            ("How long does an AC repair take?",
             "Most visits take 45–90 minutes. Compressor or PCB issues may need a follow-up visit and parts."),
            ("Do you repair all AC brands?",
             "Yes — split, window and cassette units from all major brands."),
            ("Which areas do you cover?",
             f"{SITES['bibekenterprises']} provides doorstep AC repair across {AREAS}."),
        ],
    },
    "AC Installation": {
        "includes": [
            "Site inspection and indoor/outdoor unit placement",
            "Standard bracket or stand fitting",
            "Refrigerant line and drain connection",
            "Electrical connection to an existing point",
            "Leak test, vacuuming and trial run",
        ],
        "excludes": [
            "Outdoor unit stand or bracket cost (if not supplied)",
            "Copper piping beyond the standard length",
            "New electrical wiring, MCB or stabilizer",
            "Additional wall drilling or civil work",
            "Consumables such as tape and insulation",
        ],
        "faqs": [
            ("What is included in AC installation?",
             "Standard indoor/outdoor placement, bracket fitting, refrigerant line and drain connection, electrical hookup to an existing point, vacuuming and a full trial run."),
            ("How long does installation take?",
             "Typically 2–4 hours for a standard split AC, depending on site conditions."),
            ("Is extra copper piping included?",
             "No. Piping beyond the standard length is measured and quoted separately before work starts."),
            ("Is a stabilizer included?",
             "No. Stabilizers and other accessories are not part of the installation price."),
        ],
    },
    "AC Uninstallation": {
        "includes": [
            "Safe pump-down and refrigerant recovery",
            "Indoor and outdoor unit removal",
            "Bracket, stand and pipe disconnection",
            "Wall and floor protection during removal",
            "Handover of all removed accessories",
        ],
        "excludes": [
            "Reinstallation at a new location",
            "New copper piping, bracket or stand",
            "Wall repair, painting or civil work",
            "Transport beyond the local service area",
            "Gas refill after reinstallation",
        ],
        "faqs": [
            ("Is gas recovered during AC uninstallation?",
             "Yes. The technician pumps down and recovers the refrigerant safely before disconnecting the units."),
            ("How long does uninstallation take?",
             "A standard split AC takes about 45–90 minutes, depending on access and pipe routing."),
            ("Can you reinstall the AC at my new home?",
             "Yes. Reinstallation is quoted separately based on the site, piping length and accessories required."),
            ("What happens to the bracket and pipes?",
             "All removed accessories are handed over to you unless you ask us to dispose of them."),
        ],
    },
    "AC PCB Repair": {
        "includes": [
            "Doorstep PCB diagnosis with a multimeter",
            "Component-level inspection and fault tracing",
            "Repair of common board faults",
            "Refitting and power-on test",
            "Cooling performance verification",
        ],
        "excludes": [
            "New PCB replacement cost",
            "Compressor or fan motor replacement",
            "Water damage restoration",
            "Warranty on repaired boards beyond 30 days",
            "Stabilizer or electrical wiring changes",
        ],
        "faqs": [
            ("Can every AC PCB be repaired?",
             "Many common faults are repairable, but badly burnt or water-damaged boards may need replacement; the technician confirms after diagnosis."),
            ("Do you repair the PCB at my home?",
             "Most boards are diagnosed and repaired at your doorstep. Complex boards may need a workshop visit."),
            ("How long does a PCB repair take?",
             "Diagnosis takes 30–45 minutes; a straightforward repair is usually completed the same day."),
            ("Is there a warranty on PCB repair?",
             "Yes, repaired boards carry a 30-day service warranty on the repair work."),
        ],
    },
    "AC Compressor Repair": {
        "includes": [
            "Compressor electrical and pressure testing",
            "Start capacitor and relay inspection",
            "Terminal and winding check",
            "Minor compressor repairs where possible",
            "Post-repair cooling and current test",
        ],
        "excludes": [
            "New compressor cost",
            "Refrigerant and piping replacement",
            "PCB or fan motor replacement",
            "Workshop transport if the unit must be removed",
            "Extended manufacturer warranty",
        ],
        "faqs": [
            ("How do I know the compressor has failed?",
             "The AC may blow warm air, trip the breaker or make a humming sound without starting. A technician confirms with pressure and electrical tests."),
            ("Do you replace compressors?",
             "Yes. If repair is not viable, we quote a replacement with the compatible compressor and warranty terms."),
            ("How long does the repair take?",
             "Testing takes about an hour. Replacement or workshop repair may take 1–3 days depending on parts."),
            ("Is a gas refill included?",
             "No. Refrigerant is charged separately after the compressor repair and leak test."),
        ],
    },
    "AC Gas Refill": {
        "includes": [
            "Leak check and pressure test",
            "System vacuuming before charging",
            "Refrigerant charging (R22, R32 or R410A)",
            "Cooling performance test",
            "Service report with gas type and pressure",
        ],
        "excludes": [
            "Replacement of leaking pipes, valves or joints",
            "Compressor or PCB repair",
            "Additional refrigerant beyond the standard charge",
            "Dismantling or relocation",
            "Spare parts and consumables",
        ],
        "faqs": [
            ("How do I know my AC needs a gas refill?",
             "Weak cooling, ice on the indoor coil, or a hissing sound can indicate low refrigerant. The technician confirms with a pressure test first."),
            ("How long does a gas refill take?",
             "Usually 60–90 minutes, including leak testing, vacuuming and a cooling test."),
            ("Which refrigerant do you use?",
             "The refrigerant specified for your unit — R22, R32 or R410A."),
            ("Is the gas covered by a warranty?",
             "No. If a leak is found, the repair is quoted separately; a refill alone will not fix a leaking system."),
        ],
    },
    "AC Deep Cleaning": {
        "includes": [
            "Indoor unit cover and filter cleaning",
            "Evaporator coil and blower jet cleaning",
            "Drain tray and drain pipe flush",
            "Outdoor unit coil cleaning",
            "Performance and water-drainage test",
        ],
        "excludes": [
            "Gas refill or leak repair",
            "Installation or dismantling",
            "Spare parts and electrical components",
            "Wall or civil work",
            "Chemical treatment for heavily corroded coils",
        ],
        "faqs": [
            ("How often should an AC be deep cleaned?",
             "Every 6–12 months for most homes; more often in dusty areas or if the unit runs daily."),
            ("How long does deep cleaning take?",
             "About 60–90 minutes per unit, including coil, blower and drain cleaning."),
            ("Will cleaning improve cooling?",
             "Yes. Removing dust and blockages improves airflow and cooling efficiency, and reduces electricity use."),
            ("Do you use a water-protection cover?",
             "Yes. The indoor unit is covered to protect walls and furnishings during jet cleaning."),
        ],
    },
    "Refrigerator Repair": {
        "includes": [
            "Doorstep diagnosis of cooling and electrical faults",
            "Thermostat, sensor and defrost checks",
            "Compressor startup and gas pressure test",
            "Minor adjustments and door alignment",
            "Post-repair cooling test",
        ],
        "excludes": [
            "Gas charging and replacement parts",
            "Compressor replacement",
            "Workshop transport for sealed-system repair",
            "Cabinet insulation or body work",
            "Extended warranty on spare parts",
        ],
        "faqs": [
            ("Which refrigerator types do you repair?",
             "Single door, double door, side-by-side and convertible models."),
            ("How long does a repair visit take?",
             "Most diagnoses and minor repairs take 45–90 minutes."),
            ("Is gas charging included?",
             "No. Refrigerant and leak repairs are quoted separately after diagnosis."),
            ("What should I do with the food during repair?",
             "Keep the door closed as much as possible and move perishables to a cooler for longer repairs."),
        ],
    },
    "Washing Machine Repair": {
        "includes": [
            "Doorstep diagnosis of wash, drain and spin faults",
            "Inlet/drain hose and filter checks",
            "Motor, belt and control checks",
            "Minor adjustments and a test cycle",
            "Water-leak inspection",
        ],
        "excludes": [
            "Replacement parts such as drum, motor or PCB",
            "Installation or relocation",
            "Plumbing or electrical rewiring",
            "Cabinet or body repair",
            "Descaling chemicals and consumables",
        ],
        "faqs": [
            ("Do you repair both front-load and top-load machines?",
             "Yes — front-load, top-load and semi-automatic washing machines."),
            ("How long does a repair take?",
             "Most visits take 45–90 minutes; parts-dependent repairs may need a follow-up."),
            ("What causes water leakage?",
             "Common causes include a loose inlet hose, blocked drain, worn door seal or damaged tub — the technician confirms on site."),
            ("Are spare parts included?",
             "No. Parts are quoted separately and replaced only after your approval."),
        ],
    },
    "Water Purifier Repair": {
        "includes": [
            "Doorstep diagnosis of flow, taste and leakage issues",
            "Filter and membrane condition check",
            "Pump, valve and electrical inspection",
            "Basic cleaning and sanitisation",
            "TDS and flow test after service",
        ],
        "excludes": [
            "Replacement filters, membrane or pump",
            "New tap, tank or housing",
            "Plumbing changes beyond the unit",
            "AMC or extended warranty",
            "Water-quality laboratory testing",
        ],
        "faqs": [
            ("Which purifier brands do you service?",
             "RO, UV, UF and gravity purifiers from all major brands, including wall-mounted and under-sink models."),
            ("How often should filters be replaced?",
             "Typically every 6–12 months depending on inlet water quality and usage; the technician checks TDS and flow first."),
            ("Why is water flow low?",
             "A clogged filter, weak pump or blocked tubing are common causes. The technician identifies the exact cause on site."),
            ("Do you carry spare filters?",
             "Common filters are usually available. Brand-specific membranes may be arranged after the visit."),
        ],
    },
    "Microwave Repair": {
        "includes": [
            "Doorstep diagnosis of heating and power faults",
            "Magnetron, transformer and fuse checks",
            "Door interlock and safety switch inspection",
            "Turntable and control panel testing",
            "Post-repair heating and leakage check",
        ],
        "excludes": [
            "Replacement magnetron, transformer or control board",
            "Cabinet or door glass replacement",
            "Built-in cabinet or civil work",
            "Extended warranty on spare parts",
            "Commercial or industrial microwave ovens",
        ],
        "faqs": [
            ("Which microwave types do you repair?",
             "Solo, grill and convection microwaves from all major home brands."),
            ("Why is the microwave not heating?",
             "Common causes include a failed magnetron, diode, fuse or door interlock. The technician tests the high-voltage circuit safely."),
            ("Is it safe to use after repair?",
             "Yes. We check door interlocks, earthing and microwave leakage before handing the unit back."),
            ("Do you repair built-in microwaves?",
             "We service the appliance itself; cabinet removal and carpentry work are not included."),
        ],
    },
    "Dishwasher Repair": {
        "includes": [
            "Doorstep diagnosis of wash, drain and heating faults",
            "Inlet, drain and filter inspection",
            "Spray arm and detergent dispenser check",
            "Door seal and leakage inspection",
            "Test wash cycle after repair",
        ],
        "excludes": [
            "Replacement pumps, boards or heating elements",
            "New plumbing or electrical points",
            "Cabinet modification or countertop cutting",
            "Descaling chemicals and consumables",
            "Commercial dishwasher service",
        ],
        "faqs": [
            ("Which dishwasher brands do you repair?",
             "Freestanding and built-in dishwashers from all major home appliance brands."),
            ("Why is water not draining?",
             "A blocked filter, kinked drain hose or faulty drain pump are common causes; the technician checks each on site."),
            ("Do you install new dishwashers?",
             "We provide standard installation and connection; carpentry and new plumbing points are quoted separately."),
            ("How long does a repair take?",
             "Most visits take 60–90 minutes. Parts-dependent repairs may need a follow-up visit."),
        ],
    },
    "Geyser Repair": {
        "includes": [
            "Doorstep diagnosis of heating and water-flow faults",
            "Thermostat and heating element check",
            "Safety valve and leakage inspection",
            "Electrical connection and earthing check",
            "Post-repair heating test",
        ],
        "excludes": [
            "Replacement element, thermostat or tank",
            "New plumbing or electrical wiring",
            "Wall opening or civil work",
            "Descaling beyond a standard flush",
            "Warranty on manufacturer parts",
        ],
        "faqs": [
            ("Which geyser types do you repair?",
             "Electric storage and instant geysers from all major brands."),
            ("How long does a geyser repair take?",
             "Usually 45–75 minutes, including a heating and safety test."),
            ("Why is there no hot water?",
             "Common causes are a failed heating element, tripped thermostat or faulty safety cut-out; the technician tests each on site."),
            ("Is the repair safe?",
             "Yes. The technician checks earthing, the safety valve and electrical connections before returning the unit to service."),
        ],
    },
}


async def main() -> None:
    filled_total = 0
    async with AsyncSessionLocal() as session:
        for slug, brand in SITES.items():
            domain = (await session.execute(
                select(Domain).where(Domain.slug == slug)
            )).scalar_one_or_none()
            if not domain:
                raise SystemExit(
                    f"Domain '{slug}' not found — run scripts.seed_local_domains first"
                )

            rows = (await session.execute(
                select(DomainService, Service)
                .join(Service, Service.id == DomainService.service_id)
                .where(
                    DomainService.domain_id == domain.id,
                    DomainService.is_active == True,  # noqa: E712
                )
            )).all()

            for link, service in rows:
                content = CONTENT.get(service.name)
                if not content:
                    raise SystemExit(
                        f"No content defined for service '{service.name}' — add it to CONTENT"
                    )

                override = (await session.execute(
                    select(DomainServiceOverride).where(
                        DomainServiceOverride.domain_service_id == link.id
                    )
                )).scalar_one_or_none()
                if not override:
                    raise SystemExit(
                        f"Override missing for '{service.name}' — run scripts.seed_local_service_overrides first"
                    )

                faqs = [
                    {"q": q.replace("{brand}", brand), "a": a.replace("{brand}", brand)}
                    for q, a in content["faqs"]
                ]
                values = {
                    "includes_json": json.dumps(content["includes"], ensure_ascii=False),
                    "excludes_json": json.dumps(content["excludes"], ensure_ascii=False),
                    "faqs_json": json.dumps(faqs, ensure_ascii=False),
                }
                filled = 0
                for field, value in values.items():
                    if not getattr(override, field):
                        setattr(override, field, value)
                        filled += 1
                filled_total += filled
            print(f"[OK] {slug}: {len(rows)} linked service(s) processed")

        await session.commit()
        print(f"[DONE] {filled_total} content field(s) filled")


if __name__ == "__main__":
    asyncio.run(main())
