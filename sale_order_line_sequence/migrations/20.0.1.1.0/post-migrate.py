# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """19.0 -> 20.0: the SO report and portal columns added by this module were
    removed in favour of the native Odoo 20 line numbers (``show_sol_numbers``).
    Enable the native setting so the printed/portal documents keep their numbering."""
    cr.execute("UPDATE res_company SET show_sol_numbers = TRUE WHERE show_sol_numbers IS NOT TRUE")
