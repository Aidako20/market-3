#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,fields,models

_logger=logging.getLogger(__name__)


classEventTemplateTicket(models.Model):
    _inherit='event.type.ticket'

    def_default_product_id(self):
        returnself.env.ref('event_sale.product_product_event',raise_if_not_found=False)

    description=fields.Text(compute='_compute_description',readonly=False,store=True)
    #product
    product_id=fields.Many2one(
        'product.product',string='Product',required=True,
        domain=[("event_ok","=",True)],default=_default_product_id)
    price=fields.Float(
        string='Price',compute='_compute_price',
        digits='ProductPrice',readonly=False,store=True)
    price_reduce=fields.Float(
        string="PriceReduce",compute="_compute_price_reduce",
        compute_sudo=True,digits='ProductPrice')

    @api.depends('product_id')
    def_compute_price(self):
        forticketinself:
            ifticket.product_idandticket.product_id.lst_price:
                ticket.price=ticket.product_id.lst_priceor0
            elifnotticket.price:
                ticket.price=0

    @api.depends('product_id')
    def_compute_description(self):
        forticketinself:
            ifticket.product_idandticket.product_id.description_sale:
                ticket.description=ticket.product_id.description_sale
            #initialize,i.eforembeddedtreeviews
            ifnotticket.description:
                ticket.description=False

    @api.depends('product_id','price')
    def_compute_price_reduce(self):
        forticketinself:
            product=ticket.product_id
            discount=(product.lst_price-product.price)/product.lst_priceifproduct.lst_priceelse0.0
            ticket.price_reduce=(1.0-discount)*ticket.price

    def_init_column(self,column_name):
        ifcolumn_name!="product_id":
            returnsuper(EventTemplateTicket,self)._init_column(column_name)

        #fetchvoidcolumns
        self.env.cr.execute("SELECTidFROM%sWHEREproduct_idISNULL"%self._table)
        ticket_type_ids=self.env.cr.fetchall()
        ifnotticket_type_ids:
            return

        #updateexistingcolumns
        _logger.debug("Table'%s':settingdefaultvalueofnewcolumn%stouniquevaluesforeachrow",
                      self._table,column_name)
        default_event_product=self.env.ref('event_sale.product_product_event',raise_if_not_found=False)
        ifdefault_event_product:
            product_id=default_event_product.id
        else:
            product_id=self.env['product.product'].create({
                'name':'GenericRegistrationProduct',
                'list_price':0,
                'standard_price':0,
                'type':'service',
            }).id
            self.env['ir.model.data'].create({
                'name':'product_product_event',
                'module':'event_sale',
                'model':'product.product',
                'res_id':product_id,
            })
        self.env.cr._obj.execute(
            f'UPDATE{self._table}SETproduct_id=%sWHEREidIN%s;',
            (product_id,tuple(ticket_type_ids))
        )

    @api.model
    def_get_event_ticket_fields_whitelist(self):
        """Addsalespecificfieldstocopyfromtemplatetoticket"""
        returnsuper(EventTemplateTicket,self)._get_event_ticket_fields_whitelist()+['product_id','price']


classEventTicket(models.Model):
    _inherit='event.event.ticket'
    _order="event_id,price"

    #product
    price_reduce_taxinc=fields.Float(
        string='PriceReduceTaxinc',compute='_compute_price_reduce_taxinc',
        compute_sudo=True)

    def_compute_price_reduce_taxinc(self):
        foreventinself:
            #sudonecessaryheresincethefieldismostprobablyaccessedthroughthewebsite
            tax_ids=event.product_id.taxes_id.filtered(lambdar:r.company_id==event.event_id.company_id)
            taxes=tax_ids.compute_all(event.price_reduce,event.event_id.company_id.currency_id,1.0,product=event.product_id)
            event.price_reduce_taxinc=taxes['total_included']

    @api.depends('product_id.active')
    def_compute_sale_available(self):
        inactive_product_tickets=self.filtered(lambdaticket:notticket.product_id.active)
        forticketininactive_product_tickets:
            ticket.sale_available=False
        super(EventTicket,self-inactive_product_tickets)._compute_sale_available()

    def_get_ticket_multiline_description(self):
        """Ifpeoplesetadescriptionontheirproductithasmorepriority
        thantheticketnameitselffortheSOdescription."""
        self.ensure_one()
        ifself.product_id.description_sale:
            return'%s\n%s'%(self.product_id.description_sale,self.event_id.display_name)
        returnsuper(EventTicket,self)._get_ticket_multiline_description()
