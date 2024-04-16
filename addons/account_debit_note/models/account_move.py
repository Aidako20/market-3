#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_

classAccountMove(models.Model):
    _inherit="account.move"

    debit_origin_id=fields.Many2one('account.move','OriginalInvoiceDebited',readonly=True,copy=False)
    debit_note_ids=fields.One2many('account.move','debit_origin_id','DebitNotes',
                                     help="Thedebitnotescreatedforthisinvoice")
    debit_note_count=fields.Integer('NumberofDebitNotes',compute='_compute_debit_count')

    @api.depends('debit_note_ids')
    def_compute_debit_count(self):
        debit_data=self.env['account.move'].read_group([('debit_origin_id','in',self.ids)],
                                                        ['debit_origin_id'],['debit_origin_id'])
        data_map={datum['debit_origin_id'][0]:datum['debit_origin_id_count']fordatumindebit_data}
        forinvinself:
            inv.debit_note_count=data_map.get(inv.id,0.0)

    defaction_view_debit_notes(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_window',
            'name':_('DebitNotes'),
            'res_model':'account.move',
            'view_mode':'tree,form',
            'domain':[('debit_origin_id','=',self.id)],
        }
