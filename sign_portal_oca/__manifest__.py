# Copyright 2025 Kencove
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sign Oca Portal",
    "summary": """
        Allow to sign documents inside Odoo Portal CE""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Kencove, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sign",
    "depends": ["sign_oca", "portal"],
    "data": [
        "views/sign_portal_oca_templates.xml",
        "views/portal_templates.xml",
    ],
    "demo": [],
    "maintainers": ["kobros-tech", "dnplkndll"],
}
