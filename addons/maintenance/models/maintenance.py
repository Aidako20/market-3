#-*-coding:utf-8-*-

importast

fromdatetimeimportdate,datetime,timedelta

fromflectraimportapi,fields,models,SUPERUSER_ID,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


classMaintenanceStage(models.Model):
    """Modelforcasestages.ThismodelsthemainstagesofaMaintenanceRequestmanagementflow."""

    _name='maintenance.stage'
    _description='MaintenanceStage'
    _order='sequence,id'

    name=fields.Char('Name',required=True,translate=True)
    sequence=fields.Integer('Sequence',default=20)
    fold=fields.Boolean('FoldedinMaintenancePipe')
    done=fields.Boolean('RequestDone')


classMaintenanceEquipmentCategory(models.Model):
    _name='maintenance.equipment.category'
    _inherit=['mail.alias.mixin','mail.thread']
    _description='MaintenanceEquipmentCategory'

    @api.depends('equipment_ids')
    def_compute_fold(self):
        #fixmutualdependency:'fold'dependson'equipment_count',whichis
        #computedwitharead_group(),whichretrieves'fold'!
        self.fold=False
        forcategoryinself:
            category.fold=Falseifcategory.equipment_countelseTrue

    name=fields.Char('CategoryName',required=True,translate=True)
    company_id=fields.Many2one('res.company',string='Company',
        default=lambdaself:self.env.company)
    technician_user_id=fields.Many2one('res.users','Responsible',tracking=True,default=lambdaself:self.env.uid)
    color=fields.Integer('ColorIndex')
    note=fields.Text('Comments',translate=True)
    equipment_ids=fields.One2many('maintenance.equipment','category_id',string='Equipments',copy=False)
    equipment_count=fields.Integer(string="Equipment",compute='_compute_equipment_count')
    maintenance_ids=fields.One2many('maintenance.request','category_id',copy=False)
    maintenance_count=fields.Integer(string="MaintenanceCount",compute='_compute_maintenance_count')
    alias_id=fields.Many2one(
        'mail.alias','Alias',ondelete='restrict',required=True,
        help="Emailaliasforthisequipmentcategory.Newemailswillautomatically"
        "createanewequipmentunderthiscategory.")
    fold=fields.Boolean(string='FoldedinMaintenancePipe',compute='_compute_fold',store=True)

    def_compute_equipment_count(self):
        equipment_data=self.env['maintenance.equipment'].read_group([('category_id','in',self.ids)],['category_id'],['category_id'])
        mapped_data=dict([(m['category_id'][0],m['category_id_count'])forminequipment_data])
        forcategoryinself:
            category.equipment_count=mapped_data.get(category.id,0)

    def_compute_maintenance_count(self):
        maintenance_data=self.env['maintenance.request'].read_group([('category_id','in',self.ids)],['category_id'],['category_id'])
        mapped_data=dict([(m['category_id'][0],m['category_id_count'])forminmaintenance_data])
        forcategoryinself:
            category.maintenance_count=mapped_data.get(category.id,0)

    defunlink(self):
        forcategoryinself:
            ifcategory.equipment_idsorcategory.maintenance_ids:
                raiseUserError(_("Youcannotdeleteanequipmentcategorycontainingequipmentsormaintenancerequests."))
        returnsuper(MaintenanceEquipmentCategory,self).unlink()

    def_alias_get_creation_values(self):
        values=super(MaintenanceEquipmentCategory,self)._alias_get_creation_values()
        values['alias_model_id']=self.env['ir.model']._get('maintenance.request').id
        ifself.id:
            values['alias_defaults']=defaults=ast.literal_eval(self.alias_defaultsor"{}")
            defaults['category_id']=self.id
        returnvalues


classMaintenanceEquipment(models.Model):
    _name='maintenance.equipment'
    _inherit=['mail.thread','mail.activity.mixin']
    _description='MaintenanceEquipment'
    _check_company_auto=True

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'owner_user_id'ininit_valuesandself.owner_user_id:
            returnself.env.ref('maintenance.mt_mat_assign')
        returnsuper(MaintenanceEquipment,self)._track_subtype(init_values)

    defname_get(self):
        result=[]
        forrecordinself:
            ifrecord.nameandrecord.serial_no:
                result.append((record.id,record.name+'/'+record.serial_no))
            ifrecord.nameandnotrecord.serial_no:
                result.append((record.id,record.name))
        returnresult

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        args=argsor[]
        equipment_ids=[]
        ifname:
            equipment_ids=self._search([('name','=',name)]+args,limit=limit,access_rights_uid=name_get_uid)
        ifnotequipment_ids:
            equipment_ids=self._search([('name',operator,name)]+args,limit=limit,access_rights_uid=name_get_uid)
        returnequipment_ids

    name=fields.Char('EquipmentName',required=True,translate=True)
    company_id=fields.Many2one('res.company',string='Company',
        default=lambdaself:self.env.company)
    active=fields.Boolean(default=True)
    technician_user_id=fields.Many2one('res.users',string='Technician',tracking=True)
    owner_user_id=fields.Many2one('res.users',string='Owner',tracking=True)
    category_id=fields.Many2one('maintenance.equipment.category',string='EquipmentCategory',
                                  tracking=True,group_expand='_read_group_category_ids')
    partner_id=fields.Many2one('res.partner',string='Vendor',check_company=True)
    partner_ref=fields.Char('VendorReference')
    location=fields.Char('Location')
    model=fields.Char('Model')
    serial_no=fields.Char('SerialNumber',copy=False)
    assign_date=fields.Date('AssignedDate',tracking=True)
    effective_date=fields.Date('EffectiveDate',default=fields.Date.context_today,required=True,help="Dateatwhichtheequipmentbecameeffective.ThisdatewillbeusedtocomputetheMeanTimeBetweenFailure.")
    cost=fields.Float('Cost')
    note=fields.Text('Note')
    warranty_date=fields.Date('WarrantyExpirationDate')
    color=fields.Integer('ColorIndex')
    scrap_date=fields.Date('ScrapDate')
    maintenance_ids=fields.One2many('maintenance.request','equipment_id')
    maintenance_count=fields.Integer(compute='_compute_maintenance_count',string="MaintenanceCount",store=True)
    maintenance_open_count=fields.Integer(compute='_compute_maintenance_count',string="CurrentMaintenance",store=True)
    period=fields.Integer('Daysbetweeneachpreventivemaintenance')
    next_action_date=fields.Date(compute='_compute_next_maintenance',string='Dateofthenextpreventivemaintenance',store=True)
    maintenance_team_id=fields.Many2one('maintenance.team',string='MaintenanceTeam',check_company=True,ondelete="restrict")
    maintenance_duration=fields.Float(help="MaintenanceDurationinhours.")

    @api.depends('effective_date','period','maintenance_ids.request_date','maintenance_ids.close_date')
    def_compute_next_maintenance(self):
        date_now=fields.Date.context_today(self)
        equipments=self.filtered(lambdax:x.period>0)
        forequipmentinequipments:
            next_maintenance_todo=self.env['maintenance.request'].search([
                ('equipment_id','=',equipment.id),
                ('maintenance_type','=','preventive'),
                ('stage_id.done','!=',True),
                ('close_date','=',False)],order="request_dateasc",limit=1)
            last_maintenance_done=self.env['maintenance.request'].search([
                ('equipment_id','=',equipment.id),
                ('maintenance_type','=','preventive'),
                ('stage_id.done','=',True),
                ('close_date','!=',False)],order="close_datedesc",limit=1)
            ifnext_maintenance_todoandlast_maintenance_done:
                next_date=next_maintenance_todo.request_date
                date_gap=next_maintenance_todo.request_date-last_maintenance_done.close_date
                #Ifthegapbetweenthelast_maintenance_doneandthenext_maintenance_todooneisbiggerthan2timestheperiodandnextrequestisinthefuture
                #Weuse2timestheperiodtoavoidcreationtooclosedrequestfromamanuallyonecreated
                ifdate_gap>timedelta(0)anddate_gap>timedelta(days=equipment.period)*2andnext_maintenance_todo.request_date>date_now:
                    #Ifthenewdatestillinthepast,wesetitfortoday
                    iflast_maintenance_done.close_date+timedelta(days=equipment.period)<date_now:
                        next_date=date_now
                    else:
                        next_date=last_maintenance_done.close_date+timedelta(days=equipment.period)
            elifnext_maintenance_todo:
                next_date=next_maintenance_todo.request_date
                date_gap=next_maintenance_todo.request_date-date_now
                #Ifnextmaintenancetodoisinthefuture,andinmorethan2timestheperiod,weinsertannewrequest
                #Weuse2timestheperiodtoavoidcreationtooclosedrequestfromamanuallyonecreated
                ifdate_gap>timedelta(0)anddate_gap>timedelta(days=equipment.period)*2:
                    next_date=date_now+timedelta(days=equipment.period)
            eliflast_maintenance_done:
                next_date=last_maintenance_done.close_date+timedelta(days=equipment.period)
                #Ifwhenweaddtheperiodtothelastmaintenancedoneandwestillinpast,weplanitfortoday
                ifnext_date<date_now:
                    next_date=date_now
            else:
                next_date=equipment.effective_date+timedelta(days=equipment.period)
            equipment.next_action_date=next_date
        (self-equipments).next_action_date=False

    @api.depends('maintenance_ids.stage_id.done')
    def_compute_maintenance_count(self):
        forequipmentinself:
            equipment.maintenance_count=len(equipment.maintenance_ids)
            equipment.maintenance_open_count=len(equipment.maintenance_ids.filtered(lambdax:notx.stage_id.done))

    @api.onchange('company_id')
    def_onchange_company_id(self):
        ifself.company_idandself.maintenance_team_id:
            ifself.maintenance_team_id.company_idandnotself.maintenance_team_id.company_id.id==self.company_id.id:
                self.maintenance_team_id=False

    @api.onchange('category_id')
    def_onchange_category_id(self):
        self.technician_user_id=self.category_id.technician_user_id

    _sql_constraints=[
        ('serial_no','unique(serial_no)',"Anotherassetalreadyexistswiththisserialnumber!"),
    ]

    @api.model
    defcreate(self,vals):
        equipment=super(MaintenanceEquipment,self).create(vals)
        ifequipment.owner_user_id:
            equipment.message_subscribe(partner_ids=[equipment.owner_user_id.partner_id.id])
        returnequipment

    defwrite(self,vals):
        ifvals.get('owner_user_id'):
            self.message_subscribe(partner_ids=self.env['res.users'].browse(vals['owner_user_id']).partner_id.ids)
        returnsuper(MaintenanceEquipment,self).write(vals)

    @api.model
    def_read_group_category_ids(self,categories,domain,order):
        """Readgroupcustomizationinordertodisplayallthecategoriesin
            thekanbanview,eveniftheyareempty.
        """
        category_ids=categories._search([],order=order,access_rights_uid=SUPERUSER_ID)
        returncategories.browse(category_ids)

    def_prepare_maintenance_request_vals(self,date):
        self.ensure_one()
        return{
            'name':_('PreventiveMaintenance-%s',self.name),
            'request_date':date,
            'schedule_date':date,
            'category_id':self.category_id.id,
            'equipment_id':self.id,
            'maintenance_type':'preventive',
            'owner_user_id':self.owner_user_id.id,
            'user_id':self.technician_user_id.id,
            'maintenance_team_id':self.maintenance_team_id.id,
            'duration':self.maintenance_duration,
            'company_id':self.company_id.idorself.env.company.id
        }

    def_create_new_request(self,date):
        self.ensure_one()
        vals=self._prepare_maintenance_request_vals(date)
        maintenance_requests=self.env['maintenance.request'].create(vals)
        returnmaintenance_requests

    @api.model
    def_cron_generate_requests(self):
        """
            Generatesmaintenancerequestonthenext_action_dateortodayifnoneexists
        """
        forequipmentinself.search([('period','>',0)]):
            next_requests=self.env['maintenance.request'].search([('stage_id.done','=',False),
                                                    ('equipment_id','=',equipment.id),
                                                    ('maintenance_type','=','preventive'),
                                                    ('request_date','=',equipment.next_action_date)])
            ifnotnext_requests:
                equipment._create_new_request(equipment.next_action_date)


classMaintenanceRequest(models.Model):
    _name='maintenance.request'
    _inherit=['mail.thread.cc','mail.activity.mixin']
    _description='MaintenanceRequest'
    _order="iddesc"
    _check_company_auto=True

    @api.returns('self')
    def_default_stage(self):
        returnself.env['maintenance.stage'].search([],limit=1)

    def_creation_subtype(self):
        returnself.env.ref('maintenance.mt_req_created')

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'stage_id'ininit_values:
            returnself.env.ref('maintenance.mt_req_status')
        returnsuper(MaintenanceRequest,self)._track_subtype(init_values)

    def_get_default_team_id(self):
        MT=self.env['maintenance.team']
        team=MT.search([('company_id','=',self.env.company.id)],limit=1)
        ifnotteam:
            team=MT.search([],limit=1)
        returnteam.id

    name=fields.Char('Subjects',required=True)
    company_id=fields.Many2one('res.company',string='Company',
        default=lambdaself:self.env.company)
    description=fields.Text('Description')
    request_date=fields.Date('RequestDate',tracking=True,default=fields.Date.context_today,
                               help="Daterequestedforthemaintenancetohappen")
    owner_user_id=fields.Many2one('res.users',string='CreatedbyUser',default=lambdas:s.env.uid)
    category_id=fields.Many2one('maintenance.equipment.category',related='equipment_id.category_id',string='Category',store=True,readonly=True)
    equipment_id=fields.Many2one('maintenance.equipment',string='Equipment',
                                   ondelete='restrict',index=True,check_company=True)
    user_id=fields.Many2one('res.users',string='Technician',tracking=True)
    stage_id=fields.Many2one('maintenance.stage',string='Stage',ondelete='restrict',tracking=True,
                               group_expand='_read_group_stage_ids',default=_default_stage,copy=False)
    priority=fields.Selection([('0','VeryLow'),('1','Low'),('2','Normal'),('3','High')],string='Priority')
    color=fields.Integer('ColorIndex')
    close_date=fields.Date('CloseDate',help="Datethemaintenancewasfinished.")
    kanban_state=fields.Selection([('normal','InProgress'),('blocked','Blocked'),('done','Readyfornextstage')],
                                    string='KanbanState',required=True,default='normal',tracking=True)
    #active=fields.Boolean(default=True,help="Setactivetofalsetohidethemaintenancerequestwithoutdeletingit.")
    archive=fields.Boolean(default=False,help="Setarchivetotruetohidethemaintenancerequestwithoutdeletingit.")
    maintenance_type=fields.Selection([('corrective','Corrective'),('preventive','Preventive')],string='MaintenanceType',default="corrective")
    schedule_date=fields.Datetime('ScheduledDate',help="Datethemaintenanceteamplansthemaintenance. ItshouldnotdiffermuchfromtheRequestDate.")
    maintenance_team_id=fields.Many2one('maintenance.team',string='Team',required=True,default=_get_default_team_id,check_company=True)
    duration=fields.Float(help="Durationinhours.")
    done=fields.Boolean(related='stage_id.done')

    defarchive_equipment_request(self):
        self.write({'archive':True})

    defreset_equipment_request(self):
        """Reinsertthemaintenancerequestintothemaintenancepipeinthefirststage"""
        first_stage_obj=self.env['maintenance.stage'].search([],order="sequenceasc",limit=1)
        #self.write({'active':True,'stage_id':first_stage_obj.id})
        self.write({'archive':False,'stage_id':first_stage_obj.id})

    @api.onchange('company_id')
    def_onchange_company_id(self):
        ifself.company_idandself.maintenance_team_id:
            ifself.maintenance_team_id.company_idandnotself.maintenance_team_id.company_id.id==self.company_id.id:
                self.maintenance_team_id=False

    @api.onchange('equipment_id')
    defonchange_equipment_id(self):
        ifself.equipment_id:
            self.user_id=self.equipment_id.technician_user_idifself.equipment_id.technician_user_idelseself.equipment_id.category_id.technician_user_id
            self.category_id=self.equipment_id.category_id
            ifself.equipment_id.maintenance_team_id:
                self.maintenance_team_id=self.equipment_id.maintenance_team_id.id

    @api.onchange('category_id')
    defonchange_category_id(self):
        ifnotself.user_idornotself.equipment_idor(self.user_idandnotself.equipment_id.technician_user_id):
            self.user_id=self.category_id.technician_user_id

    @api.model
    defcreate(self,vals):
        #context:no_log,becausesubtypealreadyhandlethis
        request=super(MaintenanceRequest,self).create(vals)
        ifrequest.owner_user_idorrequest.user_id:
            request._add_followers()
        ifrequest.equipment_idandnotrequest.maintenance_team_id:
            request.maintenance_team_id=request.equipment_id.maintenance_team_id
        ifnotrequest.stage_id.done:
            request.close_date=False
        elifrequest.stage_id.doneandnotrequest.close_date:
            request.close_date=fields.Date.today()
        request.activity_update()
        returnrequest

    defwrite(self,vals):
        #Overriddentoresetthekanban_statetonormalwhenever
        #thestage(stage_id)oftheMaintenanceRequestchanges.
        ifvalsand'kanban_state'notinvalsand'stage_id'invals:
            vals['kanban_state']='normal'
        res=super(MaintenanceRequest,self).write(vals)
        ifvals.get('owner_user_id')orvals.get('user_id'):
            self._add_followers()
        if'stage_id'invals:
            self.filtered(lambdam:m.stage_id.done).write({'close_date':fields.Date.today()})
            self.filtered(lambdam:notm.stage_id.done).write({'close_date':False})
            self.activity_feedback(['maintenance.mail_act_maintenance_request'])
            self.activity_update()
        ifvals.get('user_id')orvals.get('schedule_date'):
            self.activity_update()
        ifvals.get('equipment_id'):
            #needtochangedescriptionofactivityalsosounlinkoldandcreatenewactivity
            self.activity_unlink(['maintenance.mail_act_maintenance_request'])
            self.activity_update()
        returnres

    defactivity_update(self):
        """Updatemaintenanceactivitiesbasedoncurrentrecordsetstate.
        Itreschedule,unlinkorcreatemaintenancerequestactivities."""
        self.filtered(lambdarequest:notrequest.schedule_date).activity_unlink(['maintenance.mail_act_maintenance_request'])
        forrequestinself.filtered(lambdarequest:request.schedule_date):
            date_dl=fields.Datetime.from_string(request.schedule_date).date()
            updated=request.activity_reschedule(
                ['maintenance.mail_act_maintenance_request'],
                date_deadline=date_dl,
                new_user_id=request.user_id.idorrequest.owner_user_id.idorself.env.uid)
            ifnotupdated:
                ifrequest.equipment_id:
                    note=_('Requestplannedfor<ahref="#"data-oe-model="%s"data-oe-id="%s">%s</a>')%(
                        request.equipment_id._name,request.equipment_id.id,request.equipment_id.display_name)
                else:
                    note=False
                request.activity_schedule(
                    'maintenance.mail_act_maintenance_request',
                    fields.Datetime.from_string(request.schedule_date).date(),
                    note=note,user_id=request.user_id.idorrequest.owner_user_id.idorself.env.uid)

    def_add_followers(self):
        forrequestinself:
            partner_ids=(request.owner_user_id.partner_id+request.user_id.partner_id).ids
            request.message_subscribe(partner_ids=partner_ids)

    @api.model
    def_read_group_stage_ids(self,stages,domain,order):
        """Readgroupcustomizationinordertodisplayallthestagesinthe
            kanbanview,eveniftheyareempty
        """
        stage_ids=stages._search([],order=order,access_rights_uid=SUPERUSER_ID)
        returnstages.browse(stage_ids)


classMaintenanceTeam(models.Model):
    _name='maintenance.team'
    _description='MaintenanceTeams'

    name=fields.Char('TeamName',required=True,translate=True)
    active=fields.Boolean(default=True)
    company_id=fields.Many2one('res.company',string='Company',
        default=lambdaself:self.env.company)
    member_ids=fields.Many2many(
        'res.users','maintenance_team_users_rel',string="TeamMembers",
        domain="[('company_ids','in',company_id)]")
    color=fields.Integer("ColorIndex",default=0)
    request_ids=fields.One2many('maintenance.request','maintenance_team_id',copy=False)
    equipment_ids=fields.One2many('maintenance.equipment','maintenance_team_id',copy=False)

    #Forthedashboardonly
    todo_request_ids=fields.One2many('maintenance.request',string="Requests",copy=False,compute='_compute_todo_requests')
    todo_request_count=fields.Integer(string="NumberofRequests",compute='_compute_todo_requests')
    todo_request_count_date=fields.Integer(string="NumberofRequestsScheduled",compute='_compute_todo_requests')
    todo_request_count_high_priority=fields.Integer(string="NumberofRequestsinHighPriority",compute='_compute_todo_requests')
    todo_request_count_block=fields.Integer(string="NumberofRequestsBlocked",compute='_compute_todo_requests')
    todo_request_count_unscheduled=fields.Integer(string="NumberofRequestsUnscheduled",compute='_compute_todo_requests')

    @api.depends('request_ids.stage_id.done')
    def_compute_todo_requests(self):
        forteaminself:
            team.todo_request_ids=self.env['maintenance.request'].search([('maintenance_team_id','=',team.id),('stage_id.done','=',False)])
            team.todo_request_count=len(team.todo_request_ids)
            team.todo_request_count_date=self.env['maintenance.request'].search_count([('maintenance_team_id','=',team.id),('schedule_date','!=',False)])
            team.todo_request_count_high_priority=self.env['maintenance.request'].search_count([('maintenance_team_id','=',team.id),('priority','=','3')])
            team.todo_request_count_block=self.env['maintenance.request'].search_count([('maintenance_team_id','=',team.id),('kanban_state','=','blocked')])
            team.todo_request_count_unscheduled=self.env['maintenance.request'].search_count([('maintenance_team_id','=',team.id),('schedule_date','=',False)])

    @api.depends('equipment_ids')
    def_compute_equipment(self):
        forteaminself:
            team.equipment_count=len(team.equipment_ids)
