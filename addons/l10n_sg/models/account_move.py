#-*-coding:utf-8-*-

fromflectraimportfields,models


classAccountMove(models.Model):
    _inherit='account.move'

    l10n_sg_permit_number=fields.Char(string="PermitNo.")

    l10n_sg_permit_number_date=fields.Date(string="Dateofpermitnumber")
