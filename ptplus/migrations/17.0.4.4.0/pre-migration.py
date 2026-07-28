from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # OpenUpgrade's account 17.0.1.2 pre-migration renames
    # account_tax.description -> invoice_label (the <=16 description WAS the
    # label printed on documents). For the Portuguese localization that column
    # historically carries the long legal wording instead, so this script swaps
    # the two fields back. The swap is only valid for companies running the PT
    # localization: unscoped, it also swaps the taxes of every OTHER
    # localization sharing the database, wiping their invoice labels
    # (invoice_label <- the freshly recreated, empty description) and
    # misplacing the label text in description.
    # company.chart_template cannot be used to scope here: at this point of the
    # 16->17 migration vendor chart codes are not remapped yet and read NULL,
    # so the company country is the stable marker.
    env.cr.execute(
        """
        SELECT c.id
        FROM res_company c
        JOIN res_partner p ON p.id = c.partner_id
        JOIN res_country co ON co.id = p.country_id
        WHERE co.code = 'PT'
        """
    )
    pt_company_ids = [r[0] for r in env.cr.fetchall()]
    if not pt_company_ids:
        return
    taxes = (
        env["account.tax"]
        .with_context({"active_test": False})
        .search([("company_id", "in", pt_company_ids)])
    )
    for tax in taxes:
        tax.write({"invoice_label": tax.description, "description": tax.invoice_label})
