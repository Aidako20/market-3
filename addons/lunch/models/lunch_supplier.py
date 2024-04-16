#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importmath
importpytz

fromdatetimeimportdatetime,time

fromflectraimportapi,fields,models
fromflectra.osvimportexpression
fromflectra.toolsimportfloat_round

fromflectra.addons.base.models.res_partnerimport_tz_get


WEEKDAY_TO_NAME=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

deffloat_to_time(hours,moment='am'):
    """Convertanumberofhoursintoatimeobject."""
    ifhours==12.0andmoment=='pm':
        returntime.max
    fractional,integral=math.modf(hours)
    ifmoment=='pm':
        integral+=12
    returntime(int(integral),int(float_round(60*fractional,precision_digits=0)),0)

deftime_to_float(t):
    returnfloat_round(t.hour+t.minute/60+t.second/3600,precision_digits=2)

classLunchSupplier(models.Model):
    _name='lunch.supplier'
    _description='LunchSupplier'
    _inherit=['mail.thread','mail.activity.mixin']

    partner_id=fields.Many2one('res.partner',string='Vendor',required=True)

    name=fields.Char('Name',related='partner_id.name',readonly=False)

    email=fields.Char(related='partner_id.email',readonly=False)
    email_formatted=fields.Char(related='partner_id.email_formatted',readonly=True)
    phone=fields.Char(related='partner_id.phone',readonly=False)
    street=fields.Char(related='partner_id.street',readonly=False)
    street2=fields.Char(related='partner_id.street2',readonly=False)
    zip_code=fields.Char(related='partner_id.zip',readonly=False)
    city=fields.Char(related='partner_id.city',readonly=False)
    state_id=fields.Many2one("res.country.state",related='partner_id.state_id',readonly=False)
    country_id=fields.Many2one('res.country',related='partner_id.country_id',readonly=False)
    company_id=fields.Many2one('res.company',related='partner_id.company_id',readonly=False,store=True)

    responsible_id=fields.Many2one('res.users',string="Responsible",domain=lambdaself:[('groups_id','in',self.env.ref('lunch.group_lunch_manager').id)],
                                     default=lambdaself:self.env.user,
                                     help="Theresponsibleisthepersonthatwillorderlunchforeveryone.Itwillbeusedasthe'from'whensendingtheautomaticemail.")

    send_by=fields.Selection([
        ('phone','Phone'),
        ('mail','Email'),
    ],'SendOrderBy',default='phone')
    automatic_email_time=fields.Float('OrderTime',default=12.0,required=True)

    recurrency_monday=fields.Boolean('Monday',default=True)
    recurrency_tuesday=fields.Boolean('Tuesday',default=True)
    recurrency_wednesday=fields.Boolean('Wednesday',default=True)
    recurrency_thursday=fields.Boolean('Thursday',default=True)
    recurrency_friday=fields.Boolean('Friday',default=True)
    recurrency_saturday=fields.Boolean('Saturday')
    recurrency_sunday=fields.Boolean('Sunday')

    recurrency_end_date=fields.Date('Until',help="Thisfieldisusedinorderto")

    available_location_ids=fields.Many2many('lunch.location',string='Location')
    available_today=fields.Boolean('ThisisTruewhenifthesupplierisavailabletoday',
                                     compute='_compute_available_today',search='_search_available_today')

    tz=fields.Selection(_tz_get,string='Timezone',required=True,default=lambdaself:self.env.user.tzor'UTC')

    active=fields.Boolean(default=True)

    moment=fields.Selection([
        ('am','AM'),
        ('pm','PM'),
    ],default='am',required=True)

    delivery=fields.Selection([
        ('delivery','Delivery'),
        ('no_delivery','NoDelivery')
    ],default='no_delivery')

    _sql_constraints=[
        ('automatic_email_time_range',
         'CHECK(automatic_email_time>=0ANDautomatic_email_time<=12)',
         'AutomaticEmailSendingTimeshouldbebetween0and12'),
    ]

    defname_get(self):
        res=[]
        forsupplierinself:
            ifsupplier.phone:
                res.append((supplier.id,'%s%s'%(supplier.name,supplier.phone)))
            else:
                res.append((supplier.id,supplier.name))
        returnres

    deftoggle_active(self):
        """Archivingrelatedlunchproduct"""
        res=super().toggle_active()
        Product=self.env['lunch.product'].with_context(active_test=False)
        all_products=Product.search([('supplier_id','in',self.ids)])
        all_products._sync_active_from_related()
        returnres

    @api.model
    def_auto_email_send(self):
        """
            Thismethodiscalledevery20minutesviaacron.
            Itsjobissimplytogetalltheordersmadeforeachsupplierandsendanemail
            automaticallytothesupplierifthesupplierisconfiguredforitandweareready
            tosendit(usuallyat11amorso)
        """
        records=self.search([('send_by','=','mail')])

        forsupplierinrecords:
            hours=float_to_time(supplier.automatic_email_time,supplier.moment)
            date_tz=pytz.timezone(supplier.tz).localize(datetime.combine(fields.Date.today(),hours))
            date_utc=date_tz.astimezone(pytz.UTC).replace(tzinfo=None)
            ifsupplier.available_todayandfields.Datetime.now()>date_utc:
                lines=self.env['lunch.order'].search([('supplier_id','=',supplier.id),
                                                             ('state','=','ordered'),('date','=',fields.Date.today())])

                iflines:
                    order={
                        'company_name':lines[0].company_id.name,
                        'currency_id':lines[0].currency_id.id,
                        'supplier_id':supplier.partner_id.id,
                        'supplier_name':supplier.name,
                        'email_from':supplier.responsible_id.email_formatted,
                    }

                    _lines=[{
                        'product':line.product_id.name,
                        'note':line.note,
                        'quantity':line.quantity,
                        'price':line.price,
                        'toppings':line.display_toppings,
                        'username':line.user_id.name,
                    }forlineinlines]

                    order['amount_total']=sum(line.priceforlineinlines)

                    self.env.ref('lunch.lunch_order_mail_supplier').with_context(order=order,lines=_lines).send_mail(supplier.id)

                    lines.action_confirm()

    @api.depends('recurrency_end_date','recurrency_monday','recurrency_tuesday',
                 'recurrency_wednesday','recurrency_thursday','recurrency_friday',
                 'recurrency_saturday','recurrency_sunday')
    def_compute_available_today(self):
        now=fields.Datetime.now().replace(tzinfo=pytz.UTC)

        forsupplierinself:
            now=now.astimezone(pytz.timezone(supplier.tz))

            ifsupplier.recurrency_end_dateandnow.date()>=supplier.recurrency_end_date:
                supplier.available_today=False
            else:
                fieldname='recurrency_%s'%(WEEKDAY_TO_NAME[now.weekday()])
                supplier.available_today=supplier[fieldname]

    def_search_available_today(self,operator,value):
        if(notoperatorin['=','!='])or(notvaluein[True,False]):
            return[]

        searching_for_true=(operator=='='andvalue)or(operator=='!='andnotvalue)

        now=fields.Datetime.now().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(self.env.user.tzor'UTC'))
        fieldname='recurrency_%s'%(WEEKDAY_TO_NAME[now.weekday()])

        recurrency_domain=expression.OR([
            [('recurrency_end_date','=',False)],
            [('recurrency_end_date','>'ifsearching_for_trueelse'<',now)]
        ])

        returnexpression.AND([
            recurrency_domain,
            [(fieldname,operator,value)]
        ])
