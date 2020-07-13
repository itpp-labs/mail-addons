def migrate(cr, version):
    if not version:
        return

    cr.execute(
        "UPDATE ir_mail_server "
        "SET reply_to_method = 'alias' "
        "WHERE reply_to_alias IS TRUE"
    )
