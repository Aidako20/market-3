#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression


classFleetVehicle(models.Model):
    _inherit=['mail.thread','mail.activity.mixin']
    _name='fleet.vehicle'
    _description='Vehicle'
    _order='license_plateasc,acquisition_dateasc'

    def_get_default_state(self):
        state=self.env.ref('fleet.fleet_vehicle_state_registered',raise_if_not_found=False)
        returnstateifstateandstate.idelseFalse

    name=fields.Char(compute="_compute_vehicle_name",store=True)
    description=fields.Text("VehicleDescription")
    active=fields.Boolean('Active',default=True,tracking=True)
    company_id=fields.Many2one('res.company','Company',default=lambdaself:self.env.company)
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')
    license_plate=fields.Char(tracking=True,
        help='Licenseplatenumberofthevehicle(i=platenumberforacar)')
    vin_sn=fields.Char('ChassisNumber',help='Uniquenumberwrittenonthevehiclemotor(VIN/SNnumber)',copy=False)
    driver_id=fields.Many2one('res.partner','Driver',tracking=True,help='Driverofthevehicle',copy=False)
    future_driver_id=fields.Many2one('res.partner','FutureDriver',tracking=True,help='NextDriverofthevehicle',copy=False,domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    model_id=fields.Many2one('fleet.vehicle.model','Model',
        tracking=True,required=True,help='Modelofthevehicle')
    manager_id=fields.Many2one('res.users',compute='_compute_manager_id',domain=lambdaself:[('groups_id','in',self.env.ref('fleet.fleet_group_manager').id)],store=True,readonly=False)

    @api.depends('model_id')
    def_compute_manager_id(self):
        forvehicleinself:
            ifvehicle.model_id:
                vehicle.manager_id=vehicle.model_id.manager_id
            else:
                vehicle.manager_id=None

    brand_id=fields.Many2one('fleet.vehicle.model.brand','Brand',related="model_id.brand_id",store=True,readonly=False)
    log_drivers=fields.One2many('fleet.vehicle.assignation.log','vehicle_id',string='AssignmentLogs')
    log_services=fields.One2many('fleet.vehicle.log.services','vehicle_id','ServicesLogs')
    log_contracts=fields.One2many('fleet.vehicle.log.contract','vehicle_id','Contracts')
    contract_count=fields.Integer(compute="_compute_count_all",string='ContractCount')
    service_count=fields.Integer(compute="_compute_count_all",string='Services')
    odometer_count=fields.Integer(compute="_compute_count_all",string='Odometer')
    history_count=fields.Integer(compute="_compute_count_all",string="DriversHistoryCount")
    next_assignation_date=fields.Date('AssignmentDate',help='Thisisthedateatwhichthecarwillbeavailable,ifnotsetitmeansavailableinstantly')
    acquisition_date=fields.Date('ImmatriculationDate',required=False,
        default=fields.Date.today,help='Datewhenthevehiclehasbeenimmatriculated')
    first_contract_date=fields.Date(string="FirstContractDate",default=fields.Date.today)
    color=fields.Char(help='Colorofthevehicle')
    state_id=fields.Many2one('fleet.vehicle.state','State',
        default=_get_default_state,group_expand='_read_group_stage_ids',
        tracking=True,
        help='Currentstateofthevehicle',ondelete="setnull")
    location=fields.Char(help='Locationofthevehicle(garage,...)')
    seats=fields.Integer('SeatsNumber',help='Numberofseatsofthevehicle')
    model_year=fields.Char('ModelYear',help='Yearofthemodel')
    doors=fields.Integer('DoorsNumber',help='Numberofdoorsofthevehicle',default=5)
    tag_ids=fields.Many2many('fleet.vehicle.tag','fleet_vehicle_vehicle_tag_rel','vehicle_tag_id','tag_id','Tags',copy=False)
    odometer=fields.Float(compute='_get_odometer',inverse='_set_odometer',string='LastOdometer',
        help='Odometermeasureofthevehicleatthemomentofthislog')
    odometer_unit=fields.Selection([
        ('kilometers','km'),
        ('miles','mi')
        ],'OdometerUnit',default='kilometers',help='Unitoftheodometer',required=True)
    transmission=fields.Selection([('manual','Manual'),('automatic','Automatic')],'Transmission',help='TransmissionUsedbythevehicle')
    fuel_type=fields.Selection([
        ('gasoline','Gasoline'),
        ('diesel','Diesel'),
        ('lpg','LPG'),
        ('electric','Electric'),
        ('hybrid','Hybrid')
        ],'FuelType',help='FuelUsedbythevehicle')
    horsepower=fields.Integer()
    horsepower_tax=fields.Float('HorsepowerTaxation')
    power=fields.Integer('Power',help='PowerinkWofthevehicle')
    co2=fields.Float('CO2Emissions',help='CO2emissionsofthevehicle')
    image_128=fields.Image(related='model_id.image_128',readonly=True)
    contract_renewal_due_soon=fields.Boolean(compute='_compute_contract_reminder',search='_search_contract_renewal_due_soon',
        string='HasContractstorenew')
    contract_renewal_overdue=fields.Boolean(compute='_compute_contract_reminder',search='_search_get_overdue_contract_reminder',
        string='HasContractsOverdue')
    contract_renewal_name=fields.Text(compute='_compute_contract_reminder',string='Nameofcontracttorenewsoon')
    contract_renewal_total=fields.Text(compute='_compute_contract_reminder',string='Totalofcontractsdueoroverdueminusone')
    car_value=fields.Float(string="CatalogValue(VATIncl.)",help='Valueoftheboughtvehicle')
    net_car_value=fields.Float(string="PurchaseValue",help="Purchasevalueofthevehicle")
    residual_value=fields.Float()
    plan_to_change_car=fields.Boolean(related='driver_id.plan_to_change_car',store=True,readonly=False)
    vehicle_type=fields.Selection(related='model_id.vehicle_type')

    @api.depends('model_id.brand_id.name','model_id.name','license_plate')
    def_compute_vehicle_name(self):
        forrecordinself:
            record.name=(record.model_id.brand_id.nameor'')+'/'+(record.model_id.nameor'')+'/'+(record.license_plateor_('NoPlate'))

    def_get_odometer(self):
        FleetVehicalOdometer=self.env['fleet.vehicle.odometer']
        forrecordinself:
            vehicle_odometer=FleetVehicalOdometer.search([('vehicle_id','=',record.id)],limit=1,order='valuedesc')
            ifvehicle_odometer:
                record.odometer=vehicle_odometer.value
            else:
                record.odometer=0

    def_set_odometer(self):
        forrecordinself:
            ifrecord.odometer:
                date=fields.Date.context_today(record)
                data={'value':record.odometer,'date':date,'vehicle_id':record.id}
                self.env['fleet.vehicle.odometer'].create(data)

    def_compute_count_all(self):
        Odometer=self.env['fleet.vehicle.odometer']
        LogService=self.env['fleet.vehicle.log.services']
        LogContract=self.env['fleet.vehicle.log.contract']
        forrecordinself:
            record.odometer_count=Odometer.search_count([('vehicle_id','=',record.id)])
            record.service_count=LogService.search_count([('vehicle_id','=',record.id)])
            record.contract_count=LogContract.search_count([('vehicle_id','=',record.id),('state','!=','closed')])
            record.history_count=self.env['fleet.vehicle.assignation.log'].search_count([('vehicle_id','=',record.id)])

    @api.depends('log_contracts')
    def_compute_contract_reminder(self):
        params=self.env['ir.config_parameter'].sudo()
        delay_alert_contract=int(params.get_param('hr_fleet.delay_alert_contract',default=30))
        forrecordinself:
            overdue=False
            due_soon=False
            total=0
            name=''
            forelementinrecord.log_contracts:
                ifelement.statein('open','expired')andelement.expiration_date:
                    current_date_str=fields.Date.context_today(record)
                    due_time_str=element.expiration_date
                    current_date=fields.Date.from_string(current_date_str)
                    due_time=fields.Date.from_string(due_time_str)
                    diff_time=(due_time-current_date).days
                    ifdiff_time<0:
                        overdue=True
                        total+=1
                    ifdiff_time<delay_alert_contract:
                        due_soon=True
                        total+=1
                    ifoverdueordue_soon:
                        log_contract=self.env['fleet.vehicle.log.contract'].search([
                            ('vehicle_id','=',record.id),
                            ('state','in',('open','expired'))
                            ],limit=1,order='expiration_dateasc')
                        iflog_contract:
                            #wedisplayonlythenameoftheoldestoverdue/duesooncontract
                            name=log_contract.name

            record.contract_renewal_overdue=overdue
            record.contract_renewal_due_soon=due_soon
            record.contract_renewal_total=total-1 #weremove1fromtherealtotalfordisplaypurposes
            record.contract_renewal_name=name

    def_get_analytic_name(self):
        #Thisfunctionisusedinfleet_accountandisoverridedinl10n_be_hr_payroll_fleet
        returnself.license_plateor_('Noplate')

    def_search_contract_renewal_due_soon(self,operator,value):
        params=self.env['ir.config_parameter'].sudo()
        delay_alert_contract=int(params.get_param('hr_fleet.delay_alert_contract',default=30))
        res=[]
        assertoperatorin('=','!=','<>')andvaluein(True,False),'Operationnotsupported'
        if(operator=='='andvalueisTrue)or(operatorin('<>','!=')andvalueisFalse):
            search_operator='in'
        else:
            search_operator='notin'
        today=fields.Date.context_today(self)
        datetime_today=fields.Datetime.from_string(today)
        limit_date=fields.Datetime.to_string(datetime_today+relativedelta(days=+delay_alert_contract))
        res_ids=self.env['fleet.vehicle.log.contract'].search([
            ('expiration_date','>',today),
            ('expiration_date','<',limit_date),
            ('state','in',['open','expired'])
        ]).mapped('vehicle_id').ids
        res.append(('id',search_operator,res_ids))
        returnres

    def_search_get_overdue_contract_reminder(self,operator,value):
        res=[]
        assertoperatorin('=','!=','<>')andvaluein(True,False),'Operationnotsupported'
        if(operator=='='andvalueisTrue)or(operatorin('<>','!=')andvalueisFalse):
            search_operator='in'
        else:
            search_operator='notin'
        today=fields.Date.context_today(self)
        res_ids=self.env['fleet.vehicle.log.contract'].search([
            ('expiration_date','!=',False),
            ('expiration_date','<',today),
            ('state','in',['open','expired'])
        ]).mapped('vehicle_id').ids
        res.append(('id',search_operator,res_ids))
        returnres

    def_clean_vals_internal_user(self,vals):
        #Fleetadministratormaynothaverightstowriteonpartner
        #relatedfieldswhenthedriver_idisares.user.
        #Thistrickisusedtopreventaccessrighterror.
        su_vals={}
        ifself.env.su:
            returnsu_vals
        if'plan_to_change_car'invals:
            su_vals['plan_to_change_car']=vals.pop('plan_to_change_car')
        returnsu_vals

    @api.model
    defcreate(self,vals):
        ptc_value=self._clean_vals_internal_user(vals)
        res=super(FleetVehicle,self).create(vals)
        ifptc_value:
            res.sudo().write(ptc_value)
        if'driver_id'invalsandvals['driver_id']:
            res.create_driver_history(vals['driver_id'])
        if'future_driver_id'invalsandvals['future_driver_id']:
            state_waiting_list=self.env.ref('fleet.fleet_vehicle_state_waiting_list',raise_if_not_found=False)
            states=res.mapped('state_id').ids
            ifnotstate_waiting_listorstate_waiting_list.idnotinstates:
                future_driver=self.env['res.partner'].browse(vals['future_driver_id'])
                future_driver.sudo().write({'plan_to_change_car':True})
        returnres

    defwrite(self,vals):
        if'driver_id'invalsandvals['driver_id']:
            driver_id=vals['driver_id']
            self.filtered(lambdav:v.driver_id.id!=driver_id).create_driver_history(driver_id)

        if'future_driver_id'invalsandvals['future_driver_id']:
            state_waiting_list=self.env.ref('fleet.fleet_vehicle_state_waiting_list',raise_if_not_found=False)
            states=self.mapped('state_id').idsif'state_id'notinvalselse[vals['state_id']]
            ifnotstate_waiting_listorstate_waiting_list.idnotinstates:
                future_driver=self.env['res.partner'].browse(vals['future_driver_id'])
                future_driver.sudo().write({'plan_to_change_car':True})
        su_vals=self._clean_vals_internal_user(vals)
        ifsu_vals:
            self.sudo().write(su_vals)
        res=super(FleetVehicle,self).write(vals)
        if'active'invalsandnotvals['active']:
            self.mapped('log_contracts').write({'active':False})
        returnres

    def_close_driver_history(self):
        self.env['fleet.vehicle.assignation.log'].search([
            ('vehicle_id','in',self.ids),
            ('driver_id','in',self.mapped('driver_id').ids),
            ('date_end','=',False)
        ]).write({'date_end':fields.Date.today()})

    defcreate_driver_history(self,driver_id):
        forvehicleinself:
            self.env['fleet.vehicle.assignation.log'].create({
                'vehicle_id':vehicle.id,
                'driver_id':driver_id,
                'date_start':fields.Date.today(),
            })

    defaction_accept_driver_change(self):
        self._close_driver_history()
        #Findallthevehiclesforwhichthedriveristhefuture_driver_id
        #removetheirdriver_idandclosetheirhistoryusingcurrentdate
        vehicles=self.search([('driver_id','in',self.mapped('future_driver_id').ids)])
        vehicles.write({'driver_id':False})
        vehicles._close_driver_history()

        forvehicleinself:
            vehicle.future_driver_id.sudo().write({'plan_to_change_car':False})
            vehicle.driver_id=vehicle.future_driver_id
            vehicle.future_driver_id=False

    @api.model
    def_read_group_stage_ids(self,stages,domain,order):
        returnself.env['fleet.vehicle.state'].search([],order=order)

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        if'co2'infields:
            fields.remove('co2')
        returnsuper(FleetVehicle,self).read_group(domain,fields,groupby,offset,limit,orderby,lazy)

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        args=argsor[]
        ifoperator=='ilike'andnot(nameor'').strip():
            domain=[]
        else:
            domain=['|',('name',operator,name),('driver_id.name',operator,name)]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

    defreturn_action_to_open(self):
        """Thisopensthexmlviewspecifiedinxml_idforthecurrentvehicle"""
        self.ensure_one()
        xml_id=self.env.context.get('xml_id')
        ifxml_id:

            res=self.env['ir.actions.act_window']._for_xml_id('fleet.%s'%xml_id)
            res.update(
                context=dict(self.env.context,default_vehicle_id=self.id,group_by=False),
                domain=[('vehicle_id','=',self.id)]
            )
            returnres
        returnFalse

    defact_show_log_cost(self):
        """Thisopenslogviewtoviewandaddnewlogforthisvehicle,groupbydefaulttoonlyshoweffectivecosts
            @return:thecostslogview
        """
        self.ensure_one()
        copy_context=dict(self.env.context)
        copy_context.pop('group_by',None)
        res=self.env['ir.actions.act_window']._for_xml_id('fleet.fleet_vehicle_costs_action')
        res.update(
            context=dict(copy_context,default_vehicle_id=self.id,search_default_parent_false=True),
            domain=[('vehicle_id','=',self.id)]
        )
        returnres

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'driver_id'ininit_valuesor'future_driver_id'ininit_values:
            returnself.env.ref('fleet.mt_fleet_driver_updated')
        returnsuper(FleetVehicle,self)._track_subtype(init_values)

    defopen_assignation_logs(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_window',
            'name':'AssignmentLogs',
            'view_mode':'tree',
            'res_model':'fleet.vehicle.assignation.log',
            'domain':[('vehicle_id','=',self.id)],
            'context':{'default_driver_id':self.driver_id.id,'default_vehicle_id':self.id}
        }

classFleetVehicleOdometer(models.Model):
    _name='fleet.vehicle.odometer'
    _description='Odometerlogforavehicle'
    _order='datedesc'

    name=fields.Char(compute='_compute_vehicle_log_name',store=True)
    date=fields.Date(default=fields.Date.context_today)
    value=fields.Float('OdometerValue',group_operator="max")
    vehicle_id=fields.Many2one('fleet.vehicle','Vehicle',required=True)
    unit=fields.Selection(related='vehicle_id.odometer_unit',string="Unit",readonly=True)
    driver_id=fields.Many2one(related="vehicle_id.driver_id",string="Driver",readonly=False)

    @api.depends('vehicle_id','date')
    def_compute_vehicle_log_name(self):
        forrecordinself:
            name=record.vehicle_id.name
            ifnotname:
                name=str(record.date)
            elifrecord.date:
                name+='/'+str(record.date)
            record.name=name

    @api.onchange('vehicle_id')
    def_onchange_vehicle(self):
        ifself.vehicle_id:
            self.unit=self.vehicle_id.odometer_unit


classFleetVehicleState(models.Model):
    _name='fleet.vehicle.state'
    _order='sequenceasc'
    _description='VehicleStatus'

    name=fields.Char(required=True,translate=True)
    sequence=fields.Integer(help="Usedtoorderthenotestages")

    _sql_constraints=[('fleet_state_name_unique','unique(name)','Statenamealreadyexists')]


classFleetVehicleTag(models.Model):
    _name='fleet.vehicle.tag'
    _description='VehicleTag'

    name=fields.Char('TagName',required=True,translate=True)
    color=fields.Integer('ColorIndex')

    _sql_constraints=[('name_uniq','unique(name)',"Tagnamealreadyexists!")]


classFleetServiceType(models.Model):
    _name='fleet.service.type'
    _description='FleetServiceType'

    name=fields.Char(required=True,translate=True)
    category=fields.Selection([
        ('contract','Contract'),
        ('service','Service')
        ],'Category',required=True,help='Choosewhethertheservicerefertocontracts,vehicleservicesorboth')


classFleetVehicleAssignationLog(models.Model):
    _name="fleet.vehicle.assignation.log"
    _description="Drivershistoryonavehicle"
    _order="create_datedesc,date_startdesc"

    vehicle_id=fields.Many2one('fleet.vehicle',string="Vehicle",required=True)
    driver_id=fields.Many2one('res.partner',string="Driver",required=True)
    date_start=fields.Date(string="StartDate")
    date_end=fields.Date(string="EndDate")
