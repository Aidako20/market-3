#-*-coding:utf-8-*-

fromflectraimportmodels,fields


classAccountMove(models.Model):
    _inherit='account.move'

    repair_ids=fields.One2many('repair.order','invoice_id',readonly=True,copy=False)

    defunlink(self):
        repairs=self.sudo().repair_ids.filtered(lambdarepair:repair.state!='cancel')
        ifrepairs:
            repairs.sudo(False).state='2binvoiced'
        returnsuper().unlink()


classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    repair_line_ids=fields.One2many('repair.line','invoice_line_id',readonly=True,copy=False)
    repair_fee_ids=fields.One2many('repair.fee','invoice_line_id',readonly=True,copy=False)
