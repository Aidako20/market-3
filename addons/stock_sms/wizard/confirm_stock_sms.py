#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classConfirmStockSms(models.TransientModel):
    _name='confirm.stock.sms'
    _description='ConfirmStockSMS'

    pick_ids=fields.Many2many('stock.picking','stock_picking_sms_rel')

    defsend_sms(self):
        self.ensure_one()
        forcompanyinself.pick_ids.company_id:
            ifnotcompany.has_received_warning_stock_sms:
                company.sudo().write({'has_received_warning_stock_sms':True})
        pickings_to_validate=self.env['stock.picking'].browse(self.env.context.get('button_validate_picking_ids'))
        returnpickings_to_validate.button_validate()

    defdont_send_sms(self):
        self.ensure_one()
        forcompanyinself.pick_ids.company_id:
            ifnotcompany.has_received_warning_stock_sms:
                company.sudo().write({
                    'has_received_warning_stock_sms':True,
                    'stock_move_sms_validation':False,
                })
        pickings_to_validate=self.env['stock.picking'].browse(self.env.context.get('button_validate_picking_ids'))
        returnpickings_to_validate.button_validate()

