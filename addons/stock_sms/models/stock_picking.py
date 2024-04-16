#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_

importthreading


classPicking(models.Model):
    _inherit='stock.picking'

    def_pre_action_done_hook(self):
        res=super()._pre_action_done_hook()
        ifresisTrueandnotself.env.context.get('skip_sms'):
            pickings_to_warn_sms=self._check_warn_sms()
            ifpickings_to_warn_sms:
                returnpickings_to_warn_sms._action_generate_warn_sms_wizard()
        returnres

    def_check_warn_sms(self):
        warn_sms_pickings=self.browse()
        forpickinginself:
            is_delivery=picking.company_id.stock_move_sms_validation\
                    andpicking.picking_type_id.code=='outgoing'\
                    and(picking.partner_id.mobileorpicking.partner_id.phone)
            ifis_deliveryandnotgetattr(threading.currentThread(),'testing',False)\
                    andnotself.env.registry.in_test_mode()\
                    andnotpicking.company_id.has_received_warning_stock_sms\
                    andpicking.company_id.stock_move_sms_validation:
                warn_sms_pickings|=picking
        returnwarn_sms_pickings

    def_action_generate_warn_sms_wizard(self):
        view=self.env.ref('stock_sms.view_confirm_stock_sms')
        wiz=self.env['confirm.stock.sms'].create({'pick_ids':[(4,p.id)forpinself]})
        return{
            'name':_('SMS'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'confirm.stock.sms',
            'views':[(view.id,'form')],
            'view_id':view.id,
            'target':'new',
            'res_id':wiz.id,
            'context':self.env.context,
        }

    def_sms_get_number_fields(self):
        """Thismethodreturnsthefieldstousetofindthenumbertouseto
        sendanSMSonarecord."""
        return['mobile','phone']

    def_send_confirmation_email(self):
        super(Picking,self)._send_confirmation_email()
        ifnotself.env.context.get('skip_sms')andnotgetattr(threading.currentThread(),'testing',False)andnotself.env.registry.in_test_mode():
            pickings=self.filtered(lambdap:p.company_id.stock_move_sms_validationandp.picking_type_id.code=='outgoing'and(p.partner_id.mobileorp.partner_id.phone))
            forpickinginpickings:
                #Sudoastheuserhasnotalwaystherighttoreadthissmstemplate.
                template=picking.company_id.sudo().stock_sms_confirmation_template_id
                picking._message_sms_with_template(
                    template=template,
                    partner_ids=picking.partner_id.ids,
                    put_in_queue=False
                )
