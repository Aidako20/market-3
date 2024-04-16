#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api


classRegistrationEditor(models.TransientModel):
    _name="registration.editor"
    _description='EditAttendeeDetailsonSalesConfirmation'

    sale_order_id=fields.Many2one('sale.order','SalesOrder',required=True,ondelete='cascade')
    event_registration_ids=fields.One2many('registration.editor.line','editor_id',string='RegistrationstoEdit')

    @api.model
    defdefault_get(self,fields):
        res=super(RegistrationEditor,self).default_get(fields)
        ifnotres.get('sale_order_id'):
            sale_order_id=res.get('sale_order_id',self._context.get('active_id'))
            res['sale_order_id']=sale_order_id
        sale_order=self.env['sale.order'].browse(res.get('sale_order_id'))
        registrations=self.env['event.registration'].search([
            ('sale_order_id','=',sale_order.id),
            ('event_ticket_id','in',sale_order.mapped('order_line.event_ticket_id').ids),
            ('state','!=','cancel')])

        attendee_list=[]
        forso_linein[lforlinsale_order.order_lineifl.event_ticket_id]:
            existing_registrations=[rforrinregistrationsifr.event_ticket_id==so_line.event_ticket_id]
            forreginexisting_registrations:
                attendee_list.append([0,0,{
                    'event_id':reg.event_id.id,
                    'event_ticket_id':reg.event_ticket_id.id,
                    'registration_id':reg.id,
                    'name':reg.name,
                    'email':reg.email,
                    'phone':reg.phone,
                    'mobile':reg.mobile,
                    'sale_order_line_id':so_line.id,
                }])
            forcountinrange(int(so_line.product_uom_qty)-len(existing_registrations)):
                attendee_list.append([0,0,{
                    'event_id':so_line.event_id.id,
                    'event_ticket_id':so_line.event_ticket_id.id,
                    'sale_order_line_id':so_line.id,
                    'name':so_line.order_partner_id.name,
                    'email':so_line.order_partner_id.email,
                    'phone':so_line.order_partner_id.phone,
                    'mobile':so_line.order_partner_id.mobile,
                }])
        res['event_registration_ids']=attendee_list
        res=self._convert_to_write(res)
        returnres

    defaction_make_registration(self):
        self.ensure_one()
        registrations_to_create=[]
        forregistration_lineinself.event_registration_ids:
            values=registration_line.get_registration_data()
            ifregistration_line.registration_id:
                registration_line.registration_id.write(values)
            else:
                registrations_to_create.append(values)

        self.env['event.registration'].create(registrations_to_create)
        self.sale_order_id.order_line._update_registrations(confirm=self.sale_order_id.amount_total==0)

        return{'type':'ir.actions.act_window_close'}


classRegistrationEditorLine(models.TransientModel):
    """EventRegistration"""
    _name="registration.editor.line"
    _description='EditAttendeeLineonSalesConfirmation'
    _order="iddesc"

    editor_id=fields.Many2one('registration.editor')
    sale_order_line_id=fields.Many2one('sale.order.line',string='SalesOrderLine')
    event_id=fields.Many2one('event.event',string='Event',required=True)
    registration_id=fields.Many2one('event.registration','OriginalRegistration')
    event_ticket_id=fields.Many2one('event.event.ticket',string='EventTicket')
    email=fields.Char(string='Email')
    phone=fields.Char(string='Phone')
    mobile=fields.Char(string='Mobile')
    name=fields.Char(string='Name',index=True)

    defget_registration_data(self):
        self.ensure_one()
        return{
            'event_id':self.event_id.id,
            'event_ticket_id':self.event_ticket_id.id,
            'partner_id':self.editor_id.sale_order_id.partner_id.id,
            'name':self.nameorself.editor_id.sale_order_id.partner_id.name,
            'phone':self.phoneorself.editor_id.sale_order_id.partner_id.phone,
            'mobile':self.mobileorself.editor_id.sale_order_id.partner_id.mobile,
            'email':self.emailorself.editor_id.sale_order_id.partner_id.email,
            'sale_order_id':self.editor_id.sale_order_id.id,
            'sale_order_line_id':self.sale_order_line_id.id,
        }
