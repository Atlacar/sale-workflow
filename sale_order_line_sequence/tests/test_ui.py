# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderLineSequenceUI(HttpCase):
    """Browser check of the quotation form: the stored line number column is shown,
    unless the native Odoo 20 numbering (company setting) is enabled."""

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
            "own": "false" if show_native else "true",
            "native": "true" if show_native else "false",
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
