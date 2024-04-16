#-*-coding:utf-8-*-

fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression


classSaleOrder(models.Model):
    _inherit="sale.order"

    def_cart_find_product_line(self,product_id=None,line_id=None,**kwargs):
        self.ensure_one()
        lines=super(SaleOrder,self)._cart_find_product_line(product_id,line_id,**kwargs)
        ifline_id:
            returnlines
        domain=[('id','in',lines.ids)]
        ifself.env.context.get("event_ticket_id"):
            domain.append(('event_ticket_id','=',self.env.context.get("event_ticket_id")))
        returnself.env['sale.order.line'].sudo().search(domain)

    def_website_product_id_change(self,order_id,product_id,qty=0):
        order=self.env['sale.order'].sudo().browse(order_id)
        ifself._context.get('pricelist')!=order.pricelist_id.id:
            self=self.with_context(pricelist=order.pricelist_id.id)

        values=super(SaleOrder,self)._website_product_id_change(order_id,product_id,qty=qty)
        event_ticket_id=None
        ifself.env.context.get("event_ticket_id"):
            event_ticket_id=self.env.context.get("event_ticket_id")
        else:
            product=self.env['product.product'].browse(product_id)
            ifproduct.event_ticket_ids:
                event_ticket_id=product.event_ticket_ids[0].id

        ifevent_ticket_id:
            ticket=self.env['event.event.ticket'].browse(event_ticket_id)
            ifproduct_id!=ticket.product_id.id:
                raiseUserError(_("Theticketdoesn'tmatchwiththisproduct."))

            values['product_id']=ticket.product_id.id
            values['event_id']=ticket.event_id.id
            values['event_ticket_id']=ticket.id
            iforder.pricelist_id.discount_policy=='without_discount':
                values['price_unit']=ticket.price
            else:
                values['price_unit']=ticket.price_reduce
            values['name']=ticket._get_ticket_multiline_description()

        #avoidwritingrelatedvaluesthatenduplockingtheproductrecord
        values.pop('event_ok',None)

        returnvalues

    def_cart_update(self,product_id=None,line_id=None,add_qty=0,set_qty=0,**kwargs):
        OrderLine=self.env['sale.order.line']

        try:
            ifadd_qty:
                add_qty=float(add_qty)
        exceptValueError:
            add_qty=1
        try:
            ifset_qty:
                set_qty=float(set_qty)
        exceptValueError:
            set_qty=0

        ifline_id:
            line=OrderLine.browse(line_id)
            ticket=line.event_ticket_id
            old_qty=int(line.product_uom_qty)
            ifticket.id:
                self=self.with_context(event_ticket_id=ticket.id,fixed_price=1)
        else:
            ticket_domain=[('product_id','=',product_id)]
            ifself.env.context.get("event_ticket_id"):
                ticket_domain=expression.AND([ticket_domain,[('id','=',self.env.context['event_ticket_id'])]])
            ticket=self.env['event.event.ticket'].search(ticket_domain,limit=1)
            old_qty=0
        new_qty=set_qtyifset_qtyelse(add_qtyor0+old_qty)

        #case:buyingticketsforasoldoutticket
        values={}
        increased_quantity=new_qty>old_qty
        ifticketandticket.seats_limitedandticket.seats_available<=0andincreased_quantity:
            values['warning']=_('Sorry,The%(ticket)sticketsforthe%(event)seventaresoldout.')%{
                'ticket':ticket.name,
                'event':ticket.event_id.name}
            new_qty,set_qty,add_qty=0,0,-old_qty
        #case:buyingtickets,toomuchattendees
        elifticketandticket.seats_limitedandnew_qty>ticket.seats_availableandincreased_quantity:
            values['warning']=_('Sorry,only%(remaining_seats)dseatsarestillavailableforthe%(ticket)sticketforthe%(event)sevent.')%{
                'remaining_seats':ticket.seats_available,
                'ticket':ticket.name,
                'event':ticket.event_id.name}
            new_qty,set_qty,add_qty=ticket.seats_available,ticket.seats_available,0
        values.update(super(SaleOrder,self)._cart_update(product_id,line_id,add_qty,set_qty,**kwargs))

        #removingattendees
        ifticketandnew_qty<old_qty:
            attendees=self.env['event.registration'].search([
                ('state','!=','cancel'),
                ('sale_order_id','in',self.ids), #Toavoidbreakonmultirecordset
                ('event_ticket_id','=',ticket.id),
            ],offset=new_qty,limit=(old_qty-new_qty),order='create_dateasc')
            attendees.action_cancel()
        #addingattendees
        elifticketandnew_qty>old_qty:
            #donotdoanything,attendeeswillbecreatedatSOconfirmationifnotgivenpreviously
            pass
        returnvalues


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    @api.depends('product_id.display_name','event_ticket_id.display_name')
    def_compute_name_short(self):
        """Ifthesaleorderlineconcernsaticket,wedon'twanttheproductname,buttheticketnameinstead.
        """
        super(SaleOrderLine,self)._compute_name_short()

        forrecordinself:
            ifrecord.event_ticket_id:
                record.name_short=record.event_ticket_id.display_name
