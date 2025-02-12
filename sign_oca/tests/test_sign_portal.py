# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from unittest.mock import Mock, patch

import requests

from odoo.tests import users
from odoo.tests.common import HttpCase, tagged
from odoo.tools import misc

from ..controllers.main import PortalSign


@tagged("post_install", "-at_install")
class TestSignPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.data = base64.b64encode(
            open(
                misc.file_path(f"{cls.test_module}/tests/empty.pdf"),
                "rb",
            ).read()
        )
        cls.signer = cls.env["res.partner"].create({"name": "Signer"})
        cls.portal_user = cls.env.ref("base.demo_user0")
        cls.portal_partner = cls.portal_user.partner_id
        cls.request = cls.env["sign.oca.request"].create(
            {
                "data": cls.data,
                "name": "Demo template",
                "signer_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.signer.id,
                            "role_id": cls.env.ref("sign_oca.sign_role_customer").id,
                        },
                    ),
                ],
            }
        )
        cls.request2 = cls.env["sign.oca.request"].create(
            {
                "data": cls.data,
                "name": "Demo template",
                "signer_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.portal_partner.id,
                            "role_id": cls.env.ref("sign_oca.sign_role_customer").id,
                        },
                    ),
                ],
            }
        )
        cls.item = cls.request.add_item(
            {
                "role_id": cls.env.ref("sign_oca.sign_role_customer").id,
                "field_id": cls.env.ref("sign_oca.sign_field_name").id,
                "page": 1,
                "position_x": 10,
                "position_y": 10,
                "width": 10,
                "height": 10,
            }
        )
        cls.item2 = cls.request2.add_item(
            {
                "role_id": cls.env.ref("sign_oca.sign_role_customer").id,
                "field_id": cls.env.ref("sign_oca.sign_field_name").id,
                "page": 1,
                "position_x": 10,
                "position_y": 10,
                "width": 10,
                "height": 10,
            }
        )
        cls.portal_sign = PortalSign()

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    def test_portal(self):
        self.authenticate("portal", "portal")
        self.request.action_send()
        self.url_open(self.request.signer_ids.access_url).raise_for_status()
        self.assertEqual(
            base64.b64decode(self.data),
            self.url_open(
                f"/sign_oca/content/{self.request.signer_ids.id}/{self.request.signer_ids.access_token}"
            ).content,
        )
        self.assertEqual(
            self.url_open(
                f"/sign_oca/info/{self.request.signer_ids.id}/{self.request.signer_ids.access_token}",
                data="{}",
                headers={"Content-Type": "application/json"},
            ).json()["result"]["items"][str(self.item["id"])],
            self.item,
        )
        data = {}
        for key in self.request.signer_ids.get_info()["items"]:
            val = self.request.signer_ids.get_info()["items"][key].copy()
            val["value"] = "My Name"
            data[key] = val

    def test_get_sign_requests_domain(self):
        self.domain = self.portal_sign.get_sign_requests_domain(request=self)
        expected_domain = [
            ("request_id.state", "=", "sent"),
            ("partner_id", "child_of", [self.env.user.partner_id.id]),
            ("signed_on", "=", False),
        ]
        self.assertEqual(sorted(self.domain), sorted(expected_domain))

    def test_mocked_portal_methods(self):
        domain = [("partner_id", "in", [self.signer.id])]
        SignRequests = self.env["sign.oca.request.signer"].sudo()
        sign_requests = SignRequests.search(domain)
        expected_values = {
            "sales_user": self.env["res.users"],
            "page_name": "My Sign Requests",
            "sign_requests": sign_requests,
            "pager": {
                "page_count": 2,
                "offset": 0,
                "page": {"url": "/my/sign_requests", "num": 1},
                "page_first": {"url": "/my/sign_requests", "num": 1},
                "page_start": {"url": "/my/sign_requests", "num": 1},
                "page_previous": {"url": "/my/sign_requests", "num": 1},
                "page_next": {"url": "/my/sign_requests/page/2", "num": 1},
                "page_end": {"url": "/my/sign_requests/page/2", "num": 1},
                "page_last": {"url": "/my/sign_requests/page/2", "num": 1},
                "pages": [{"url": "/my/sign_requests", "num": 1}],
            },
            "default_url": "/my/sign_requests",
        }
        expected_domain = [
            ("request_id.state", "=", "sent"),
            ("partner_id", "child_of", [self.env.user.partner_id.id]),
            ("signed_on", "=", False),
        ]
        expected_home_values = {"sign_oca_count": 1}

        class Capture:
            mock_response = Mock()

            def get_sign_requests_domain(cls, request):
                cls.mock_response.domain = expected_domain
                return cls.mock_response

            def _prepare_sign_portal_rendering_values(
                cls, request, page=1, sign_page=False, **kwargs
            ):
                cls.mock_response.values = expected_values
                return cls.mock_response

            def _prepare_home_portal_values(cls, counters):
                cls.mock_response.home_values = {"sign_oca_count": len(sign_requests)}
                return cls.mock_response

        capture = Capture()

        with patch(
            "odoo.addons.sign_oca.controllers.main.PortalSign.get_sign_requests_domain",
            capture.get_sign_requests_domain,
        ):
            response = self.portal_sign.get_sign_requests_domain(capture.mock_response)
            self.assertEqual(response.domain, expected_domain)

        with patch(
            "odoo.addons.sign_oca.controllers.main.PortalSign._prepare_sign_portal_rendering_values",
            capture._prepare_sign_portal_rendering_values,
        ):
            response = self.portal_sign._prepare_sign_portal_rendering_values(
                request=capture.mock_response, page=1, sign_page=False, kwargs={}
            )
            self.assertEqual(response.values, expected_values)

        with patch(
            "odoo.addons.sign_oca.controllers.main.PortalSign._prepare_home_portal_values",
            capture._prepare_home_portal_values,
        ):
            response = self.portal_sign._prepare_home_portal_values(
                counters=["sign_oca_count"]
            )
            self.assertEqual(response.home_values, expected_home_values)

    @users("portal")
    def test_sign_requests(self):
        self.authenticate("portal", "portal")
        self.request2.action_send()
        self.url_open("/my/sign_requests").raise_for_status()
        response = self.url_open("/my/sign_requests")
        assert response.status_code == 200
        html = response.text
        assert "Sign Requests" in html
        assert "To be Signed" in html
        assert "Demo template" in html
