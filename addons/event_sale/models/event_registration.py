#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.toolsimportfloat_is_zero


classEventRegistration(models.Model):
    _inherit='event.registration'

    is_paid=fields.Boolean('IsPaid')
    #TDEFIXME:maybeaddanonchangeonsale_order_id
    sale_order_id=fields.Many2one('sale.order',string='SalesOrder',ondelete='cascade',copy=False)
    sale_order_line_id=fields.Many2one('sale.order.line',string='SalesOrderLine',ondelete='cascade',copy=False)
    payment_status=fields.Selection(string="PaymentStatus",selection=[
            ('to_pay','NotPaid'),
            ('paid','Paid'),
            ('free','Free'),
        ],compute="_compute_payment_status",compute_sudo=True)
    utm_campaign_id=fields.Many2one(compute='_compute_utm_campaign_id',readonly=False,store=True)
    utm_source_id=fields.Many2one(compute='_compute_utm_source_id',readonly=False,store=True)
    utm_medium_id=fields.Many2one(compute='_compute_utm_medium_id',readonly=False,store=True)

    @api.depends('is_paid','sale_order_id.currency_id','sale_order_line_id.price_total')
    def_compute_payment_status(self):
        forrecordinself:
            so=record.sale_order_id
            so_line=record.sale_order_line_id
            ifnotsoorfloat_is_zero(so_line.price_total,precision_digits=so.currency_id.rounding):
                record.payment_status='free'
            elifrecord.is_paid:
                record.payment_status='paid'
            else:
                record.payment_status='to_pay'

    @api.depends('sale_order_id')
    def_compute_utm_campaign_id(self):
        forregistrationinself:
            ifregistration.sale_order_id.campaign_id:
                registration.utm_campaign_id=registration.sale_order_id.campaign_id
            elifnotregistration.utm_campaign_id:
                registration.utm_campaign_id=False

    @api.depends('sale_order_id')
    def_compute_utm_source_id(self):
        forregistrationinself:
            ifregistration.sale_order_id.source_id:
                registration.utm_source_id=registration.sale_order_id.source_id
            elifnotregistration.utm_source_id:
                registration.utm_source_id=False

    @api.depends('sale_order_id')
    def_compute_utm_medium_id(self):
        forregistrationinself:
            ifregistration.sale_order_id.medium_id:
                registration.utm_medium_id=registration.sale_order_id.medium_id
            elifnotregistration.utm_medium_id:
                registration.utm_medium_id=False

    defaction_view_sale_order(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['views']=[(False,'form')]
        action['res_id']=self.sale_order_id.id
        returnaction

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            ifvals.get('sale_order_line_id'):
                so_line_vals=self._synchronize_so_line_values(
                    self.env['sale.order.line'].browse(vals['sale_order_line_id'])
                )
                vals.update(so_line_vals)
        registrations=super(EventRegistration,self).create(vals_list)
        forregistrationinregistrations:
            ifregistration.sale_order_id:
                registration.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self':registration,'origin':registration.sale_order_id},
                    subtype_id=self.env.ref('mail.mt_note').id)
        returnregistrations

    defwrite(self,vals):
        ifvals.get('sale_order_line_id'):
            so_line_vals=self._synchronize_so_line_values(
                self.env['sale.order.line'].browse(vals['sale_order_line_id'])
            )
            vals.update(so_line_vals)

        ifvals.get('event_ticket_id'):
            self.filtered(
                lambdaregistration:registration.event_ticket_idandregistration.event_ticket_id.id!=vals['event_ticket_id']
            )._sale_order_ticket_type_change_notify(self.env['event.event.ticket'].browse(vals['event_ticket_id']))

        returnsuper(EventRegistration,self).write(vals)

    def_synchronize_so_line_values(self,so_line):
        ifso_line:
            return{
                'partner_id':so_line.order_id.partner_id.id,
                'event_id':so_line.event_id.id,
                'event_ticket_id':so_line.event_ticket_id.id,
                'sale_order_id':so_line.order_id.id,
                'sale_order_line_id':so_line.id,
            }
        return{}

    def_sale_order_ticket_type_change_notify(self,new_event_ticket):
        fallback_user_id=self.env.user.idifnotself.env.user._is_public()elseself.env.ref("base.user_admin").id
        forregistrationinself:
            render_context={
                'registration':registration,
                'old_ticket_name':registration.event_ticket_id.name,
                'new_ticket_name':new_event_ticket.name
            }
            user_id=registration.event_id.user_id.idorregistration.sale_order_id.user_id.idorfallback_user_id
            registration.sale_order_id._activity_schedule_with_view(
                'mail.mail_activity_data_warning',
                user_id=user_id,
                views_or_xmlid='event_sale.event_ticket_id_change_exception',
                render_context=render_context)

    def_action_set_paid(self):
        self.write({'is_paid':True})

    def_get_registration_summary(self):
        res=super(EventRegistration,self)._get_registration_summary()
        res.update({
            'payment_status':self.payment_status,
            'payment_status_value':dict(self._fields['payment_status']._description_selection(self.env))[self.payment_status],
            'has_to_pay':self.payment_status=='to_pay',
        })
        returnres
