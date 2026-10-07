# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    """Odoo 20 prints line numbers on the quotation form, the report and the portal
    only when the company setting "Line Numbers" (``show_sol_numbers``) is enabled.
    Before 20 this module always displayed the numbers, so enable the native setting
    on the existing companies when the module is installed."""
    env["res.company"].search([("show_sol_numbers", "=", False)]).show_sol_numbers = True
