#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectraimportmodels


classStockPicking(models.Model):
    _inherit='stock.picking'

    defaction_view_stock_valuation_layers(self):
        self.ensure_one()
        scraps=self.env['stock.scrap'].search([('picking_id','=',self.id)])
        domain=[('id','in',(self.move_lines+scraps.move_id).stock_valuation_layer_ids.ids)]
        action=self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
        context=literal_eval(action['context'])
        context.update(self.env.context)
        context['no_at_date']=True
        returndict(action,domain=domain,context=context)

