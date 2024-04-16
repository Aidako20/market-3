#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError

fromdateutil.relativedeltaimportrelativedelta

classFleetVehicleLogContract(models.Model):
    _inherit=['mail.thread','mail.activity.mixin']
    _name='fleet.vehicle.log.contract'
    _description='VehicleContract'
    _order='statedesc,expiration_date'

    defcompute_next_year_date(self,strdate):
        oneyear=relativedelta(years=1)
        start_date=fields.Date.from_string(strdate)
        returnfields.Date.to_string(start_date+oneyear)

    vehicle_id=fields.Many2one('fleet.vehicle','Vehicle',required=True,help='Vehicleconcernedbythislog')
    cost_subtype_id=fields.Many2one('fleet.service.type','Type',help='Costtypepurchasedwiththiscost',domain=[('category','=','contract')])
    amount=fields.Monetary('Cost')
    date=fields.Date(help='Datewhenthecosthasbeenexecuted')
    company_id=fields.Many2one('res.company','Company',default=lambdaself:self.env.company)
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')
    name=fields.Char(string='Name',compute='_compute_contract_name',store=True)
    active=fields.Boolean(default=True)
    user_id=fields.Many2one('res.users','Responsible',default=lambdaself:self.env.user,index=True)
    start_date=fields.Date('ContractStartDate',default=fields.Date.context_today,
        help='Datewhenthecoverageofthecontractbegins')
    expiration_date=fields.Date('ContractExpirationDate',default=lambdaself:
        self.compute_next_year_date(fields.Date.context_today(self)),
        help='Datewhenthecoverageofthecontractexpirates(bydefault,oneyearafterbegindate)')
    days_left=fields.Integer(compute='_compute_days_left',string='WarningDate')
    insurer_id=fields.Many2one('res.partner','Vendor')
    purchaser_id=fields.Many2one(related='vehicle_id.driver_id',string='CurrentDriver')
    ins_ref=fields.Char('Reference',size=64,copy=False)
    state=fields.Selection([
        ('futur','Incoming'),
        ('open','InProgress'),
        ('expired','Expired'),
        ('closed','Closed')
        ],'Status',default='open',readonly=True,
        help='Choosewhetherthecontractisstillvalidornot',
        tracking=True,
        copy=False)
    notes=fields.Text('TermsandConditions',help='Writehereallsupplementaryinformationrelativetothiscontract',copy=False)
    cost_generated=fields.Monetary('RecurringCost')
    cost_frequency=fields.Selection([
        ('no','No'),
        ('daily','Daily'),
        ('weekly','Weekly'),
        ('monthly','Monthly'),
        ('yearly','Yearly')
        ],'RecurringCostFrequency',default='monthly',help='Frequencyoftherecuringcost',required=True)
    service_ids=fields.Many2many('fleet.service.type',string="IncludedServices")

    @api.depends('vehicle_id.name','cost_subtype_id')
    def_compute_contract_name(self):
        forrecordinself:
            name=record.vehicle_id.name
            ifnameandrecord.cost_subtype_id.name:
                name=record.cost_subtype_id.name+''+name
            record.name=name

    @api.depends('expiration_date','state')
    def_compute_days_left(self):
        """returnadictwithasvalueforeachcontractaninteger
        ifcontractisinanopenstateandisoverdue,return0
        ifcontractisinaclosedstate,return-1
        otherwisereturnthenumberofdaysbeforethecontractexpires
        """
        forrecordinself:
            ifrecord.expiration_dateandrecord.statein['open','expired']:
                today=fields.Date.from_string(fields.Date.today())
                renew_date=fields.Date.from_string(record.expiration_date)
                diff_time=(renew_date-today).days
                record.days_left=diff_time>0anddiff_timeor0
            else:
                record.days_left=-1

    defwrite(self,vals):
        res=super(FleetVehicleLogContract,self).write(vals)
        ifvals.get('expiration_date')orvals.get('user_id'):
            self.activity_reschedule(['fleet.mail_act_fleet_contract_to_renew'],date_deadline=vals.get('expiration_date'),new_user_id=vals.get('user_id'))
        returnres

    defcontract_close(self):
        forrecordinself:
            record.state='closed'

    defcontract_draft(self):
        forrecordinself:
            record.state='futur'

    defcontract_open(self):
        forrecordinself:
            record.state='open'

    @api.model
    defscheduler_manage_contract_expiration(self):
        #Thismethodiscalledbyacrontask
        #Itmanagesthestateofacontract,possiblybypostingamessageonthevehicleconcernedandupdatingitsstatus
        params=self.env['ir.config_parameter'].sudo()
        delay_alert_contract=int(params.get_param('hr_fleet.delay_alert_contract',default=30))
        date_today=fields.Date.from_string(fields.Date.today())
        outdated_days=fields.Date.to_string(date_today+relativedelta(days=+delay_alert_contract))
        reminder_activity_type=self.env.ref('fleet.mail_act_fleet_contract_to_renew',raise_if_not_found=False)orself.env['mail.activity.type']
        nearly_expired_contracts=self.search([
            ('state','=','open'),
            ('expiration_date','<',outdated_days),
            ('user_id','!=',False)
        ]
        ).filtered(
            lambdanec:reminder_activity_typenotinnec.activity_ids.activity_type_id
        )

        forcontractinnearly_expired_contracts:
            contract.activity_schedule(
                'fleet.mail_act_fleet_contract_to_renew',contract.expiration_date,
                user_id=contract.user_id.id)

        expired_contracts=self.search([('state','notin',['expired','closed']),('expiration_date','<',fields.Date.today())])
        expired_contracts.write({'state':'expired'})

        futur_contracts=self.search([('state','notin',['futur','closed']),('start_date','>',fields.Date.today())])
        futur_contracts.write({'state':'futur'})

        now_running_contracts=self.search([('state','=','futur'),('start_date','<=',fields.Date.today())])
        now_running_contracts.write({'state':'open'})

    defrun_scheduler(self):
        self.scheduler_manage_contract_expiration()

classFleetVehicleLogServices(models.Model):
    _name='fleet.vehicle.log.services'
    _inherit=['mail.thread','mail.activity.mixin']
    _rec_name='service_type_id'
    _description='Servicesforvehicles'

    active=fields.Boolean(default=True)
    vehicle_id=fields.Many2one('fleet.vehicle','Vehicle',required=True,help='Vehicleconcernedbythislog')
    amount=fields.Monetary('Cost')
    description=fields.Char('Description')
    odometer_id=fields.Many2one('fleet.vehicle.odometer','Odometer',help='Odometermeasureofthevehicleatthemomentofthislog')
    odometer=fields.Float(compute="_get_odometer",inverse='_set_odometer',string='OdometerValue',
        help='Odometermeasureofthevehicleatthemomentofthislog')
    odometer_unit=fields.Selection(related='vehicle_id.odometer_unit',string="Unit",readonly=True)
    date=fields.Date(help='Datewhenthecosthasbeenexecuted',default=fields.Date.context_today)
    company_id=fields.Many2one('res.company','Company',default=lambdaself:self.env.company)
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')
    purchaser_id=fields.Many2one('res.partner',string="Driver",compute='_compute_purchaser_id',readonly=False,store=True)
    inv_ref=fields.Char('VendorReference')
    vendor_id=fields.Many2one('res.partner','Vendor')
    notes=fields.Text()
    service_type_id=fields.Many2one(
        'fleet.service.type','ServiceType',required=True,
        default=lambdaself:self.env.ref('fleet.type_service_service_8',raise_if_not_found=False),
    )
    state=fields.Selection([
        ('todo','ToDo'),
        ('running','Running'),
        ('done','Done'),
        ('cancelled','Cancelled'),
    ],default='todo',string='Stage')

    def_get_odometer(self):
        self.odometer=0
        forrecordinself:
            ifrecord.odometer_id:
                record.odometer=record.odometer_id.value

    def_set_odometer(self):
        forrecordinself:
            ifnotrecord.odometer:
                raiseUserError(_('Emptyingtheodometervalueofavehicleisnotallowed.'))
            odometer=self.env['fleet.vehicle.odometer'].create({
                'value':record.odometer,
                'date':record.dateorfields.Date.context_today(record),
                'vehicle_id':record.vehicle_id.id
            })
            self.odometer_id=odometer

    @api.model_create_multi
    defcreate(self,vals_list):
        fordatainvals_list:
            if'odometer'indataandnotdata['odometer']:
                #ifreceivedvalueforodometeris0,thenremoveitfromthe
                #dataasitwouldresulttothecreationofa
                #odometerlogwith0,whichistobeavoided
                deldata['odometer']
        returnsuper(FleetVehicleLogServices,self).create(vals_list)

    @api.depends('vehicle_id')
    def_compute_purchaser_id(self):
        forserviceinself:
            service.purchaser_id=service.vehicle_id.driver_id
