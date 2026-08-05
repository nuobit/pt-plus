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
    #
    # The swap is SQL over the WHOLE translation jsonb, never the ORM: an ORM
    # read/write pair (tax.description / tax.invoice_label) resolves in the
    # context language only, so every OTHER language's variant is dropped on
    # write. Both columns are jsonb at this point of the migration, and in an
    # UPDATE the right-hand side reads the OLD row values, so the two
    # assignments are a true simultaneous swap with every language preserved.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax t
           SET description = t.invoice_label,
               invoice_label = t.description
          FROM res_company c
          JOIN res_partner p ON p.id = c.partner_id
          JOIN res_country co ON co.id = p.country_id
         WHERE c.id = t.company_id
           AND co.code = 'PT'
        """,
    )
