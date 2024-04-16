#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classLunchOrder(models.Model):
    _name='lunch.order'
    _description='LunchOrder'
    _order='iddesc'
    _display_name='product_id'

    name=fields.Char(related='product_id.name',string="ProductName",readonly=True) #toremove
    topping_ids_1=fields.Many2many('lunch.topping','lunch_order_topping','order_id','topping_id',string='Extras1',domain=[('topping_category','=',1)])
    topping_ids_2=fields.Many2many('lunch.topping','lunch_order_topping','order_id','topping_id',string='Extras2',domain=[('topping_category','=',2)])
    topping_ids_3=fields.Many2many('lunch.topping','lunch_order_topping','order_id','topping_id',string='Extras3',domain=[('topping_category','=',3)])
    product_id=fields.Many2one('lunch.product',string="Product",required=True)
    category_id=fields.Many2one(
        string='ProductCategory',related='product_id.category_id',store=True)
    date=fields.Date('OrderDate',required=True,readonly=True,
                       states={'new':[('readonly',False)]},
                       default=fields.Date.context_today)
    supplier_id=fields.Many2one(
        string='Vendor',related='product_id.supplier_id',store=True,index=True)
    user_id=fields.Many2one('res.users','User',readonly=True,
                              states={'new':[('readonly',False)]},
                              default=lambdaself:self.env.uid)
    note=fields.Text('Notes')
    price=fields.Float('TotalPrice',compute='_compute_total_price',readonly=True,store=True,
                         digits='Account')
    active=fields.Boolean('Active',default=True)
    state=fields.Selection([('new','ToOrder'),
                              ('ordered','Ordered'),
                              ('confirmed','Received'),
                              ('cancelled','Cancelled')],
                             'Status',readonly=True,index=True,default='new')
    company_id=fields.Many2one('res.company',default=lambdaself:self.env.company.id)
    currency_id=fields.Many2one(related='company_id.currency_id',store=True)
    quantity=fields.Float('Quantity',required=True,default=1)

    display_toppings=fields.Text('Extras',compute='_compute_display_toppings',store=True)

    product_description=fields.Text('Description',related='product_id.description')
    topping_label_1=fields.Char(related='product_id.category_id.topping_label_1')
    topping_label_2=fields.Char(related='product_id.category_id.topping_label_2')
    topping_label_3=fields.Char(related='product_id.category_id.topping_label_3')
    topping_quantity_1=fields.Selection(related='product_id.category_id.topping_quantity_1')
    topping_quantity_2=fields.Selection(related='product_id.category_id.topping_quantity_2')
    topping_quantity_3=fields.Selection(related='product_id.category_id.topping_quantity_3')
    image_1920=fields.Image(compute='_compute_product_images')
    image_128=fields.Image(compute='_compute_product_images')

    available_toppings_1=fields.Boolean(help='Areextrasavailableforthisproduct',compute='_compute_available_toppings')
    available_toppings_2=fields.Boolean(help='Areextrasavailableforthisproduct',compute='_compute_available_toppings')
    available_toppings_3=fields.Boolean(help='Areextrasavailableforthisproduct',compute='_compute_available_toppings')

    @api.depends('product_id')
    def_compute_product_images(self):
        forlineinself:
            line.image_1920=line.product_id.image_1920orline.category_id.image_1920
            line.image_128=line.product_id.image_128orline.category_id.image_128

    @api.depends('category_id')
    def_compute_available_toppings(self):
        forlineinself:
            line.available_toppings_1=bool(line.env['lunch.topping'].search_count([('category_id','=',line.category_id.id),('topping_category','=',1)]))
            line.available_toppings_2=bool(line.env['lunch.topping'].search_count([('category_id','=',line.category_id.id),('topping_category','=',2)]))
            line.available_toppings_3=bool(line.env['lunch.topping'].search_count([('category_id','=',line.category_id.id),('topping_category','=',3)]))

    definit(self):
        self._cr.execute("""CREATEINDEXIFNOTEXISTSlunch_order_user_product_dateON%s(user_id,product_id,date)"""
            %self._table)

    def_extract_toppings(self,values):
        """
            Ifcalledinapi.multithenitwillpoptopping_ids_1,2,3fromvalues
        """
        ifself.ids:
            #TODOThisisnottakingintoaccountallthetoppingsforeachindividualorder,thisisusuallynotaproblem
            #sinceintheinterfaceyouusuallydon'tupdatemorethanoneorderatatimebutthisisabugnonetheless
            topping_1=values.pop('topping_ids_1')[0][2]if'topping_ids_1'invalueselseself[:1].topping_ids_1.ids
            topping_2=values.pop('topping_ids_2')[0][2]if'topping_ids_2'invalueselseself[:1].topping_ids_2.ids
            topping_3=values.pop('topping_ids_3')[0][2]if'topping_ids_3'invalueselseself[:1].topping_ids_3.ids
        else:
            topping_1=values['topping_ids_1'][0][2]if'topping_ids_1'invalueselse[]
            topping_2=values['topping_ids_2'][0][2]if'topping_ids_2'invalueselse[]
            topping_3=values['topping_ids_3'][0][2]if'topping_ids_3'invalueselse[]

        returntopping_1+topping_2+topping_3

    @api.constrains('topping_ids_1','topping_ids_2','topping_ids_3')
    def_check_topping_quantity(self):
        errors={
            '1_more':_('Youshouldorderatleastone%s'),
            '1':_('Youhavetoorderoneandonlyone%s'),
        }
        forlineinself:
            forindexinrange(1,4):
                availability=line['available_toppings_%s'%index]
                quantity=line['topping_quantity_%s'%index]
                toppings=line['topping_ids_%s'%index].filtered(lambdax:x.topping_category==index)
                label=line['topping_label_%s'%index]

                ifavailabilityandquantity!='0_more':
                    check=bool(len(toppings)==1ifquantity=='1'elsetoppings)
                    ifnotcheck:
                        raiseValidationError(errors[quantity]%label)

    @api.model
    defcreate(self,values):
        lines=self._find_matching_lines({
            **values,
            'toppings':self._extract_toppings(values),
        })
        iflines:
            #YTIFIXMEThiswillupdatemultiplelinesinthecasetherearemultiple
            #matchinglineswhichshouldnothappenthroughtheinterface
            lines.update_quantity(1)
            returnlines[:1]
        returnsuper().create(values)

    defwrite(self,values):
        merge_needed='note'invaluesor'topping_ids_1'invaluesor'topping_ids_2'invaluesor'topping_ids_3'invalues

        ifmerge_needed:
            lines_to_deactivate=self.env['lunch.order']
            forlineinself:
                #Onlywriteontopping_ids_1becausetheyallsharethesametable
                #andwedon'twanttoremovealltherecords
                #_extract_toppingswillpoptopping_ids_1,topping_ids_2andtopping_ids_3fromvalues
                #Thisalsoforcesustoinvalidatethecachefortopping_ids_2andtopping_ids_3that
                #couldhavechangedthroughtopping_ids_1withoutthecacheknowingaboutit
                toppings=self._extract_toppings(values)
                self.invalidate_cache(['topping_ids_2','topping_ids_3'])
                values['topping_ids_1']=[(6,0,toppings)]
                matching_lines=self._find_matching_lines({
                    'user_id':values.get('user_id',line.user_id.id),
                    'product_id':values.get('product_id',line.product_id.id),
                    'note':values.get('note',line.noteorFalse),
                    'toppings':toppings,
                })
                ifmatching_lines:
                    lines_to_deactivate|=line
                    #YTITODOTrytobatchit,becarefultheremightbemultiplematching
                    #linesforthesameorderhencequantityshouldnotalwaysbe
                    #line.quantity,butratherasum
                    matching_lines.update_quantity(line.quantity)
            lines_to_deactivate.write({'active':False})
            returnsuper(LunchOrder,self-lines_to_deactivate).write(values)
        returnsuper().write(values)

    @api.model
    def_find_matching_lines(self,values):
        domain=[
            ('user_id','=',values.get('user_id',self.default_get(['user_id'])['user_id'])),
            ('product_id','=',values.get('product_id',False)),
            ('date','=',fields.Date.today()),
            ('note','=',values.get('note',False)),
        ]
        toppings=values.get('toppings',[])
        returnself.search(domain).filtered(lambdaline:(line.topping_ids_1|line.topping_ids_2|line.topping_ids_3).ids==toppings)

    @api.depends('topping_ids_1','topping_ids_2','topping_ids_3','product_id','quantity')
    def_compute_total_price(self):
        forlineinself:
            line.price=line.quantity*(line.product_id.price+sum((line.topping_ids_1|line.topping_ids_2|line.topping_ids_3).mapped('price')))

    @api.depends('topping_ids_1','topping_ids_2','topping_ids_3')
    def_compute_display_toppings(self):
        forlineinself:
            toppings=line.topping_ids_1|line.topping_ids_2|line.topping_ids_3
            line.display_toppings='+'.join(toppings.mapped('name'))

    defupdate_quantity(self,increment):
        forlineinself.filtered(lambdaline:line.state!='confirmed'):
            ifline.quantity<=-increment:
                #TODO:maybeunlinktheorder?
                line.active=False
            else:
                line.quantity+=increment
        self._check_wallet()

    defadd_to_cart(self):
        """
            Thismethodcurrentlydoesnothing,wecurrentlyneeditinorderto
            beabletoreusethismodelinplaceofawizard
        """
        #YTIFIXME:Findawaytodropthis.
        returnTrue

    def_check_wallet(self):
        self.flush()
        forlineinself:
            ifself.env['lunch.cashmove'].get_wallet_balance(line.user_id)<0:
                raiseValidationError(_('Yourwalletdoesnotcontainenoughmoneytoorderthat.Toaddsomemoneytoyourwallet,pleasecontactyourlunchmanager.'))

    defaction_order(self):
        ifself.filtered(lambdaline:notline.product_id.active):
            raiseValidationError(_('Productisnolongeravailable.'))
        self.write({'state':'ordered'})
        self._check_wallet()

    defaction_confirm(self):
        self.write({'state':'confirmed'})

    defaction_cancel(self):
        self.write({'state':'cancelled'})
