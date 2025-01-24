from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, route

from odoo.addons.base.models.assetsbundle import AssetsBundle
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class SignController(http.Controller):
    @http.route("/sign_oca/get_assets.<any(css,js):ext>", type="http", auth="public")
    def get_sign_resources(self, ext):
        bundle = "sign_oca.sign_assets"
        files, _ = request.env["ir.qweb"]._get_asset_content(bundle)
        asset = AssetsBundle(bundle, files)
        mock_attachment = getattr(asset, ext)()
        if isinstance(
            mock_attachment, list
        ):  # suppose that CSS asset will not required to be split in pages
            mock_attachment = mock_attachment[0]
        stream = request.env["ir.binary"]._get_stream_from(mock_attachment)
        response = stream.get_response()
        return response


class PortalSign(CustomerPortal):
    @http.route(
        ["/sign_oca/document/<int:signer_id>/<string:access_token>"],
        type="http",
        auth="public",
        website=True,
    )
    def get_sign_oca_access(self, signer_id, access_token, **kwargs):
        try:
            signer_sudo = self._document_check_access(
                "sign.oca.request.signer", signer_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        if signer_sudo.signed_on:
            return request.render(
                "sign_oca.portal_sign_document_signed",
                {
                    "signer": signer_sudo,
                    "company": signer_sudo.request_id.company_id,
                },
            )
        return request.render(
            "sign_oca.portal_sign_document",
            {
                "doc": signer_sudo.request_id,
                "partner": signer_sudo.partner_id,
                "signer": signer_sudo,
                "access_token": access_token,
                "sign_oca_backend_info": {
                    "access_token": access_token,
                    "signer_id": signer_sudo.id,
                    "lang": signer_sudo.partner_id.lang,
                },
            },
        )

    @http.route(
        ["/sign_oca/content/<int:signer_id>/<string:access_token>"],
        type="http",
        auth="public",
        website=True,
    )
    def get_sign_oca_content_access(self, signer_id, access_token):
        try:
            signer_sudo = self._document_check_access(
                "sign.oca.request.signer", signer_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        return http.Stream.from_binary_field(
            signer_sudo.request_id, "data"
        ).get_response(mimetype="application/pdf")

    @http.route(
        ["/sign_oca/info/<int:signer_id>/<string:access_token>"],
        type="json",
        auth="public",
        website=True,
    )
    def get_sign_oca_info_access(self, signer_id, access_token):
        try:
            signer_sudo = self._document_check_access(
                "sign.oca.request.signer", signer_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        return signer_sudo.get_info(access_token=access_token)

    @http.route(
        ["/sign_oca/sign/<int:signer_id>/<string:access_token>"],
        type="json",
        auth="public",
        website=True,
    )
    def get_sign_oca_sign_access(
        self, signer_id, access_token, items, latitude=False, longitude=False
    ):
        try:
            signer_sudo = self._document_check_access(
                "sign.oca.request.signer", signer_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        return signer_sudo.action_sign(
            items, access_token=access_token, latitude=latitude, longitude=longitude
        )

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
            "sign_oca.sign_requests",
            values,
        )
