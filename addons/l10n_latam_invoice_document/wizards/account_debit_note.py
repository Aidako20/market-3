fromflectraimportmodels


classAccountDebitNote(models.TransientModel):

    _inherit='account.debit.note'

    defcreate_debit(self):
        """Properlycomputethelatamdocumenttypeoftypedebitnote."""
        res=super().create_debit()
        new_move_id=res.get('res_id')
        ifnew_move_id:
            new_move=self.env['account.move'].browse(new_move_id)
            new_move._compute_l10n_latam_document_type()
        returnres
