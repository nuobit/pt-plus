from openupgradelib import openupgrade

field_renames = [
    ("res.partner", "res_partner", "legal_name", "l10n_pt_legal_name"),
]


@openupgrade.migrate()
def migrate(env, version):
    if "l10n_pt_legal_name" not in env["res.partner"]._fields and not (
        openupgrade.column_exists(env.cr, "res_partner", "l10n_pt_legal_name")
    ):
        openupgrade.rename_fields(env, field_renames)
