from django.core.management.base import BaseCommand
from django.db import transaction

from manuals.models import Manual, Section

MANUALS = [
    {
        "title": "Forma One 3D Printer - Quick Start Guide",
        "description": "User guide for the Forma One 3D printer.",
        "sections": [
            ("Installation", "Place the printer on a flat, stable surface, away from drafts. Connect the 24 V power supply and turn on the switch at the back. On first start-up the printer runs an automatic bed calibration that takes about 3 minutes."),
            ("Loading filament", "The Forma One supports 1.75 mm PLA and PETG filaments. Heat the nozzle to 210 degrees for PLA or 240 degrees for PETG, then push the filament into the extruder until it comes out of the nozzle. Do not use ABS: the printer has no enclosed chamber."),
            ("First print", "Copy the G-code file to a microSD card and insert it into the front slot. From the menu, select Print and choose the file. For test parts, a layer height of 0.2 mm is recommended."),
            ("Troubleshooting", "If the part does not stick to the bed, clean the bed with isopropyl alcohol and repeat the calibration. If the nozzle clogs, heat it to 250 degrees and run the cleaning procedure from the Maintenance menu. Error code E04 means the temperature sensor is disconnected."),
        ],
    },
    {
        "title": "NetBox X2 Router - User Manual",
        "description": "Setting up and using the NetBox X2 Wi-Fi router.",
        "sections": [
            ("First login", "Connect your computer to the router with a network cable or to the NetBox-X2 Wi-Fi network. Open a browser at 192.168.50.1. The default credentials are admin / netbox2024 and must be changed at first login."),
            ("Wi-Fi setup", "The router broadcasts on 2.4 GHz and 5 GHz. From the Wireless menu you can change the network name and password. WPA3 security is recommended; a mixed WPA2/WPA3 mode is available for older devices."),
            ("Guest network", "The guest network gives visitors Internet access without exposing the devices on your main network. Enable it from Wireless > Guests; access can be limited to between 1 and 24 hours."),
            ("Factory reset", "To restore the router to factory settings, hold the Reset button on the back for 10 seconds until the lights flash. All settings will be erased."),
        ],
    },
    {
        "title": "ShiftPro - Administrator Guide",
        "description": "Managing work shifts with the ShiftPro application.",
        "sections": [
            ("Creating a department", "From Settings > Departments, click New department and enter its name and manager. Each employee can belong to only one department at a time."),
            ("Planning shifts", "In the Calendar view, drag an employee onto the desired time slot. ShiftPro highlights in red any shift longer than 10 hours a day or with less than 11 hours of rest between shifts."),
            ("Leave requests", "Employees send leave requests from the mobile app. The administrator receives a notification and can approve or reject them from the Requests section. Approved leave is automatically blocked out in the calendar."),
            ("Exporting data", "From the Reports section you can export hours worked as CSV or Excel, filtered by department and period. Export is only available to users with the Administrator role."),
        ],
    },
]


class Command(BaseCommand):
    help = "Create sample manuals with sections for development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing manuals before creating new ones.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = Manual.objects.all().delete()
            self.stdout.write(f"Deleted {deleted} existing objects.")

        for data in MANUALS:
            manual, created = Manual.objects.get_or_create(
                title=data["title"],
                defaults={"description": data["description"]},
            )
            if not created:
                self.stdout.write(f"Already exists, skipping: {manual.title}")
                continue

            for order, (title, content) in enumerate(data["sections"], start=1):
                Section.objects.create(manual=manual, title=title, content=content, order=order)

            self.stdout.write(self.style.SUCCESS(f"Created: {manual.title}"))