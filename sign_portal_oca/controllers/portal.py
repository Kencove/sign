# Copyright 2025 Kencove
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.sign_oca.controllers.main import PortalSign


class PortalSign(PortalSign):
    def get_sign_requests_domain(self, request):
        domain = [
            ("request_id.state", "=", "sent"),
            ("partner_id", "child_of", [request.env.user.partner_id.id]),
            ("signed_on", "=", False),
        ]
        return domain

    def _prepare_sign_portal_rendering_values(self, page=1, sign_page=False, **kwargs):
        SignRequests = request.env["sign.oca.request.signer"].sudo()
        domain = self.get_sign_requests_domain(request)

        self._items_per_page = 10
        pager_values = portal_pager(
            url="/my/sign_requests",
            total=SignRequests.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={},
        )
        sign_requests = SignRequests.search(
            domain,
            order="id desc",
            limit=self._items_per_page,
            offset=pager_values["offset"],
        )
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "sign_requests": sign_requests.sudo() if sign_page else SignRequests,
                "page_name": "My Sign Requests",
                "pager": pager_values,
                "default_url": "/my/sign_requests",
            }
        )

        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "sign_oca_count" in counters:
            domain = self.get_sign_requests_domain(request)
            SignRequests = request.env["sign.oca.request.signer"].sudo()
            values["sign_oca_count"] = SignRequests.search_count(domain)
        return values

    @route(
        ["/my/sign_requests", "/my/sign_requests/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
    )
    def sign_requests(self, **kwargs):
        values = self._prepare_sign_portal_rendering_values(sign_page=True, **kwargs)
        return request.render(
            "sign_portal_oca.sign_requests",
            values,
        )
