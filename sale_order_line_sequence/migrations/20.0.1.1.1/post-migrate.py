# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Renumber the orders with combo lines, which no longer take a line number"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    lines = (
        env["sale.order.line"]
        .with_context(active_test=False)
        .search([("product_id.type", "=", "combo")])
        .order_id.order_line
    )
    env.add_to_compute(lines._fields["visible_sequence"], lines)
    lines._recompute_recordset(["visible_sequence"])
