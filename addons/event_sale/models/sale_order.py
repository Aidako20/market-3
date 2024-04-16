#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_


classSaleOrder(models.Model):
    _inherit="sale.order"

    attendee_count=fields.Integer('AttendeeCount',compute='_compute_attendee_count')

    defwrite(self,vals):
        """SynchronizepartnerfromSOtoregistrations.Thisisdonenotably
        inwebsite_salecontrollershop/addressthatupdatescustomer,butnot
        only."""
        result=super(SaleOrder,self).write(vals)
        ifvals.get('partner_id'):
            registrations_toupdate=self.env['event.registration'].search([('sale_order_id','in',self.ids)])
            registrations_toupdate.write({'partner_id':vals['partner_id']})
        returnresult

    defaction_confirm(self):
        res=super(SaleOrder,self).action_confirm()
        forsoinself:
            #confirmregistrationifitwasfree(otherwiseitwillbeconfirmedonceinvoicefullypaid)
            so.order_line._update_registrations(confirm=so.amount_total==0,cancel_to_draft=False)
            ifany(line.event_idforlineinso.order_line):
                returnself.env['ir.actions.act_window']\
                    .with_context(default_sale_order_id=so.id)\
                    ._for_xml_id('event_sale.action_sale_order_event_registration')
        returnres

    def_action_cancel(self):
        self.order_line._cancel_associated_registrations()
        returnsuper()._action_cancel()

    defaction_view_attendee_list(self):
        action=self.env["ir.actions.actions"]._for_xml_id("event.event_registration_action_tree")
        action['domain']=[('sale_order_id','in',self.ids)]
        returnaction

    def_compute_attendee_count(self):
        sale_orders_data=self.env['event.registration'].read_group(
            [('sale_order_id','in',self.ids),
             ('state','!=','cancel')],
            ['sale_order_id'],['sale_order_id']
        )
        attendee_count_data={
            sale_order_data['sale_order_id'][0]:
            sale_order_data['sale_order_id_count']
            forsale_order_datainsale_orders_data
        }
        forsale_orderinself:
            sale_order.attendee_count=attendee_count_data.get(sale_order.id,0)

    defunlink(self):
        self.mapped('order_line')._unlink_associated_registrations()
        returnsuper(SaleOrder,self).unlink()


classSaleOrderLine(models.Model):

    _inherit='sale.order.line'

    event_id=fields.Many2one(
        'event.event',string='Event',
        help="Chooseaneventanditwillautomaticallycreatearegistrationforthisevent.")
    event_ticket_id=fields.Many2one(
        'event.event.ticket',string='EventTicket',
        help="Chooseaneventticketanditwillautomaticallycreatearegistrationforthiseventticket.")
    event_ok=fields.Boolean(related='product_id.event_ok',readonly=True)

    @api.depends('state','event_id')
    def_compute_product_uom_readonly(self):
        event_lines=self.filtered(lambdaline:line.event_id)
        event_lines.update({'product_uom_readonly':True})
        super(SaleOrderLine,self-event_lines)._compute_product_uom_readonly()

    def_update_registrations(self,confirm=True,cancel_to_draft=False,registration_data=None,mark_as_paid=False):
        """Createorupdateregistrationslinkedtoasalesorderline.Asale
        orderlinehasaproduct_uom_qtyattributethatwillbethenumberof
        registrationslinkedtothisline.Thismethodupdateexistingregistrations
        andcreatenewoneformissingone."""
        RegistrationSudo=self.env['event.registration'].sudo()
        registrations=RegistrationSudo.search([('sale_order_line_id','in',self.ids)])
        registrations_vals=[]
        forso_lineinself.filtered('event_id'):
            existing_registrations=registrations.filtered(lambdaself:self.sale_order_line_id.id==so_line.id)
            ifconfirm:
                existing_registrations.filtered(lambdaself:self.statenotin['open','cancel']).action_confirm()
            ifmark_as_paid:
                existing_registrations.filtered(lambdaself:notself.is_paid)._action_set_paid()
            ifcancel_to_draft:
                existing_registrations.filtered(lambdaself:self.state=='cancel').action_set_draft()

            forcountinrange(int(so_line.product_uom_qty)-len(existing_registrations)):
                values={
                    'sale_order_line_id':so_line.id,
                    'sale_order_id':so_line.order_id.id
                }
                #TDECHECK:autoconfirmation
                ifregistration_data:
                    values.update(registration_data.pop())
                registrations_vals.append(values)

        ifregistrations_vals:
            RegistrationSudo.create(registrations_vals)
        returnTrue

    @api.onchange('product_id')
    def_onchange_product_id(self):
        #Weresettheeventwhenkeepingitwouldleadtoaninconstitentstate.
        #Weneedtodoitthiswaybecausetheonlyrelationbetweentheproductandtheeventisthroughthecorrespondingtickets.
        ifself.event_idand(notself.product_idorself.product_id.idnotinself.event_id.mapped('event_ticket_ids.product_id.id')):
            self.event_id=None

    @api.onchange('event_id')
    def_onchange_event_id(self):
        #Weresettheticketwhenkeepingitwouldleadtoaninconstitentstate.
        ifself.event_ticket_idand(notself.event_idorself.event_id!=self.event_ticket_id.event_id):
            self.event_ticket_id=None

    @api.onchange('product_uom','product_uom_qty')
    defproduct_uom_change(self):
        ifnotself.event_ticket_id:
            super(SaleOrderLine,self).product_uom_change()

    @api.onchange('event_ticket_id')
    def_onchange_event_ticket_id(self):
        #wecallthistoforceupdatethedefaultname
        self.product_id_change()

    defunlink(self):
        self._unlink_associated_registrations()
        returnsuper(SaleOrderLine,self).unlink()

    def_cancel_associated_registrations(self):
        self.env['event.registration'].search([('sale_order_line_id','in',self.ids)]).action_cancel()

    def_unlink_associated_registrations(self):
        self.env['event.registration'].search([('sale_order_line_id','in',self.ids)]).unlink()

    defget_sale_order_line_multiline_description_sale(self,product):
        """Weoverridethismethodbecausewedecidedthat:
                Thedefaultdescriptionofasalesorderlinecontainingaticketmustbedifferentthanthedefaultdescriptionwhennoticketispresent.
                Sointhatcaseweusethedescriptioncomputedfromtheticket,insteadofthedescriptioncomputedfromtheproduct.
                Weneedthisoverridetobedefinedhereinsalesorderline(andnotinproduct)becausehereistheonlyplacewheretheevent_ticket_idisreferenced.
        """
        ifself.event_ticket_id:
            ticket=self.event_ticket_id.with_context(
                lang=self.order_id.partner_id.lang,
            )

            returnticket._get_ticket_multiline_description()+self._get_sale_order_line_multiline_description_variants()
        else:
            returnsuper(SaleOrderLine,self).get_sale_order_line_multiline_description_sale(product)

    def_get_display_price(self,product):
        ifself.event_ticket_idandself.event_id:
            returnself.event_ticket_id.with_context(pricelist=self.order_id.pricelist_id.id,uom=self.product_uom.id).price_reduce
        else:
            returnsuper()._get_display_price(product)
