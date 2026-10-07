# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderLineSequenceUI(HttpCase):
    """Browser check of the quotation form: the stored line number column is shown and
    the native running-counter column is hidden, whatever the company setting is.
    The portal prints the stored numbers too."""

    CODE = """
        (async () => {
        const wait = async (cond, label) => {
            for (let i = 0; i < 100; i++) {
                if (cond()) { return; }
                await new Promise((r) => setTimeout(r, 200));
            }
            throw new Error("timeout waiting for " + label);
        };
        const lines = () => document.querySelector(".o_field_widget[name=order_line]");
        await wait(() => lines() && lines().querySelector("tr.o_data_row"), "order lines");
        const hasOwn = !!lines().querySelector("th[data-name=visible_sequence]");
        const hasNative = !!lines().querySelector(".o_line_number");
        if (hasOwn !== %(own)s || hasNative !== %(native)s) {
            throw new Error("unexpected columns: visible_sequence=" + hasOwn + " native=" + hasNative);
        }
        console.log("test successful");
        })().catch((e) => console.error(e.message || e));
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env["product.product"].create({"name": "UI line product"})
        cls.order = cls.env["sale.order"].create({
            "partner_id": cls.env["res.partner"].create({"name": "UI customer"}).id,
            "order_line": [
                (0, 0, {"product_id": product.id, "product_uom_qty": 1}),
                (0, 0, {"product_id": product.id, "product_uom_qty": 2}),
            ],
        })

    def _check(self, show_native):
        self.env.company.show_sol_numbers = show_native
        code = self.CODE % {
            "own": "true",  # the stored number column is always shown
            "native": "false",  # the native counter column is hidden
        }
        self.browser_js(
            f"/odoo/action-sale.action_orders/{self.order.id}",
            code,
            login="admin",
        )

    def test_own_column(self):
        self._check(False)

    def test_native_column(self):
        self._check(True)

    def test_portal_numbers(self):
        from lxml import html as lxml_html

        self.env.company.show_sol_numbers = True
        order = self.env["sale.order"].create({
            "partner_id": self.order.partner_id.id,
            "order_line": [
                (0, 0, {"display_type": "line_section", "name": "Section", "sequence": 10}),
                (0, 0, {"product_id": self.order.order_line[0].product_id.id, "product_uom_qty": 1, "sequence": 30}),
                (0, 0, {"product_id": self.order.order_line[0].product_id.id, "product_uom_qty": 1, "sequence": 20}),
                (0, 0, {"display_type": "line_note", "name": "Note", "sequence": 40}),
            ],
        })
        response = self.url_open(order.get_portal_url())
        self.assertEqual(response.status_code, 200)
        tree = lxml_html.fromstring(response.content)
        for kind, expected in (("product", ["1", "2"]), ("section", [""]), ("note", [""])):
            texts = [
                "".join(td.itertext()).strip()
                for td in tree.xpath(f"//td[@name='td_{kind}_line_no']")
            ]
            self.assertEqual(texts, expected, kind)
