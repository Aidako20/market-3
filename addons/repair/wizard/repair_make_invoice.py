#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMakeInvoice(models.TransientModel):
    _name='repair.order.make_invoice'
    _description='CreateMassInvoice(repair)'

    group=fields.Boolean('Groupbypartnerinvoiceaddress')

    defmake_invoices(self):
        ifnotself._context.get('active_ids'):
            return{'type':'ir.actions.act_window_close'}
        new_invoice={}
        forwizardinself:
            repairs=self.env['repair.order'].browse(self._context['active_ids'])
            new_invoice=repairs._create_invoices(group=wizard.group)

            #Wehavetoudpatethestateofthegivenrepairs,otherwisetheyremain'tobeinvoiced'.
            #Notethatthiswilltriggeranothercalltothemethod'_create_invoices',
            #butthatsecondcallwillnotdoanything,sincetherepairsarealreadyinvoiced.
            repairs.action_repair_invoice_create()
        return{
            'domain':[('id','in',list(new_invoice.values()))],
            'name':'Invoices',
            'view_mode':'tree,form',
            'res_model':'account.move',
            'view_id':False,
            'views':[(self.env.ref('account.view_move_tree').id,'tree'),(self.env.ref('account.view_move_form').id,'form')],
            'context':"{'move_type':'out_invoice'}",
            'type':'ir.actions.act_window'
        }
