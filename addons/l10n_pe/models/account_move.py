#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields
fromflectra.tools.sqlimportcolumn_exists,create_column


classAccountMoveLine(models.Model):
    _inherit="account.move.line"

    l10n_pe_group_id=fields.Many2one("account.group",related="account_id.group_id",store=True)

    def_auto_init(self):
        """
        CreatecolumntostopORMfromcomputingithimself(tooslow)
        """
        ifnotcolumn_exists(self.env.cr,self._table,'l10n_pe_group_id'):
            create_column(self.env.cr,self._table,'l10n_pe_group_id','int4')
            self.env.cr.execute("""
                UPDATEaccount_move_lineline
                SETl10n_pe_group_id=account.group_id
                FROMaccount_accountaccount
                WHEREaccount.id=line.account_id
            """)
        returnsuper()._auto_init()
