#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp,_
fromflectra.addons.website_event.controllers.mainimportWebsiteEventController
fromflectra.httpimportrequest


classWebsiteEventSaleController(WebsiteEventController):

    @http.route()
    defevent_register(self,event,**post):
        event=event.with_context(pricelist=request.website.id)
        ifnotrequest.context.get('pricelist'):
            pricelist=request.website.get_current_pricelist()
            ifpricelist:
                event=event.with_context(pricelist=pricelist.id)
        returnsuper(WebsiteEventSaleController,self).event_register(event,**post)

    def_process_tickets_form(self,event,form_details):
        """Addpriceinformationonticketorder"""
        res=super(WebsiteEventSaleController,self)._process_tickets_form(event,form_details)
        foriteminres:
            item['price']=item['ticket']['price']ifitem['ticket']else0
        returnres

    def_create_attendees_from_registration_post(self,event,registration_data):
        #wehaveatleastoneregistrationlinkedtoaticket->salemodeactivate
        ifany(info.get('event_ticket_id')forinfoinregistration_data):
            order=request.website.sale_get_order(force_create=1)

        forinfoin[rforrinregistration_dataifr.get('event_ticket_id')]:
            ticket=request.env['event.event.ticket'].sudo().browse(info['event_ticket_id'])
            cart_values=order.with_context(event_ticket_id=ticket.id,fixed_price=True)._cart_update(product_id=ticket.product_id.id,add_qty=1)
            info['sale_order_id']=order.id
            info['sale_order_line_id']=cart_values.get('line_id')

        returnsuper(WebsiteEventSaleController,self)._create_attendees_from_registration_post(event,registration_data)

    @http.route()
    defregistration_confirm(self,event,**post):
        res=super(WebsiteEventSaleController,self).registration_confirm(event,**post)

        registrations=self._process_attendees_form(event,post)

        #wehaveatleastoneregistrationlinkedtoaticket->salemodeactivate
        ifany(info['event_ticket_id']forinfoinregistrations):
            order=request.website.sale_get_order(force_create=False)
            iforder.amount_total:
                returnrequest.redirect("/shop/checkout")
            #freetickets->orderwithamount=0:auto-confirm,nocheckout
            eliforder:
                order.action_confirm() #tdenotsure:emailsending?
                request.website.sale_reset()

        returnres

    def_add_event(self,event_name="NewEvent",context=None,**kwargs):
        product=request.env.ref('event_sale.product_product_event',raise_if_not_found=False)
        ifproduct:
            context=dict(contextor{},default_event_ticket_ids=[[0,0,{
                'name':_('Registration'),
                'product_id':product.id,
                'end_sale_date':False,
                'seats_max':1000,
                'price':0,
            }]])
        returnsuper(WebsiteEventSaleController,self)._add_event(event_name,context,**kwargs)
