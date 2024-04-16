#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
fromrandomimportchoice
fromstringimportdigits
fromwerkzeug.urlsimporturl_encode

fromflectraimportapi,fields,models,_
fromflectra.osv.queryimportQuery
fromflectra.exceptionsimportValidationError,AccessError
fromflectra.modules.moduleimportget_module_resource


classHrEmployeePrivate(models.Model):
    """
    NB:Anyfieldonlyavailableonthemodelhr.employee(i.e.notonthe
    hr.employee.publicmodel)shouldhave`groups="hr.group_hr_user"`onits
    definitiontoavoidbeingprefetchedwhentheuserhasn'taccesstothe
    hr.employeemodel.Indeed,theprefetchloadsthedataforallthefields
    thatareavailableaccordingtothegroupdefinedonthem.
    """
    _name="hr.employee"
    _description="Employee"
    _order='name'
    _inherit=['hr.employee.base','mail.thread','mail.activity.mixin','resource.mixin','image.mixin']
    _mail_post_access='read'

    @api.model
    def_default_image(self):
        image_path=get_module_resource('hr','static/src/img','default_image.png')
        returnbase64.b64encode(open(image_path,'rb').read())

    #resourceanduser
    #requiredontheresource,makesurerequired="True"setintheview
    name=fields.Char(string="EmployeeName",related='resource_id.name',store=True,readonly=False,tracking=True)
    user_id=fields.Many2one('res.users','User',related='resource_id.user_id',store=True,readonly=False)
    user_partner_id=fields.Many2one(related='user_id.partner_id',related_sudo=False,string="User'spartner")
    active=fields.Boolean('Active',related='resource_id.active',default=True,store=True,readonly=False)
    company_id=fields.Many2one('res.company',required=True)
    #privatepartner
    address_home_id=fields.Many2one(
        'res.partner','Address',help='Enterheretheprivateaddressoftheemployee,nottheonelinkedtoyourcompany.',
        groups="hr.group_hr_user",tracking=True,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    is_address_home_a_company=fields.Boolean(
        'Theemployeeaddresshasacompanylinked',
        compute='_compute_is_address_home_a_company',
    )
    private_email=fields.Char(related='address_home_id.email',string="PrivateEmail",groups="hr.group_hr_user")
    country_id=fields.Many2one(
        'res.country','Nationality(Country)',groups="hr.group_hr_user",tracking=True)
    gender=fields.Selection([
        ('male','Male'),
        ('female','Female'),
        ('other','Other')
    ],groups="hr.group_hr_user",tracking=True)
    marital=fields.Selection([
        ('single','Single'),
        ('married','Married'),
        ('cohabitant','LegalCohabitant'),
        ('widower','Widower'),
        ('divorced','Divorced')
    ],string='MaritalStatus',groups="hr.group_hr_user",default='single',tracking=True)
    spouse_complete_name=fields.Char(string="SpouseCompleteName",groups="hr.group_hr_user",tracking=True)
    spouse_birthdate=fields.Date(string="SpouseBirthdate",groups="hr.group_hr_user",tracking=True)
    children=fields.Integer(string='NumberofChildren',groups="hr.group_hr_user",tracking=True)
    place_of_birth=fields.Char('PlaceofBirth',groups="hr.group_hr_user",tracking=True)
    country_of_birth=fields.Many2one('res.country',string="CountryofBirth",groups="hr.group_hr_user",tracking=True)
    birthday=fields.Date('DateofBirth',groups="hr.group_hr_user",tracking=True)
    ssnid=fields.Char('SSNNo',help='SocialSecurityNumber',groups="hr.group_hr_user",tracking=True)
    sinid=fields.Char('SINNo',help='SocialInsuranceNumber',groups="hr.group_hr_user",tracking=True)
    identification_id=fields.Char(string='IdentificationNo',groups="hr.group_hr_user",tracking=True)
    passport_id=fields.Char('PassportNo',groups="hr.group_hr_user",tracking=True)
    bank_account_id=fields.Many2one(
        'res.partner.bank','BankAccountNumber',
        domain="[('partner_id','=',address_home_id),'|',('company_id','=',False),('company_id','=',company_id)]",
        groups="hr.group_hr_user",
        tracking=True,
        help='Employeebanksalaryaccount')
    permit_no=fields.Char('WorkPermitNo',groups="hr.group_hr_user",tracking=True)
    visa_no=fields.Char('VisaNo',groups="hr.group_hr_user",tracking=True)
    visa_expire=fields.Date('VisaExpireDate',groups="hr.group_hr_user",tracking=True)
    additional_note=fields.Text(string='AdditionalNote',groups="hr.group_hr_user",tracking=True)
    certificate=fields.Selection([
        ('graduate','Graduate'),
        ('bachelor','Bachelor'),
        ('master','Master'),
        ('doctor','Doctor'),
        ('other','Other'),
    ],'CertificateLevel',default='other',groups="hr.group_hr_user",tracking=True)
    study_field=fields.Char("FieldofStudy",groups="hr.group_hr_user",tracking=True)
    study_school=fields.Char("School",groups="hr.group_hr_user",tracking=True)
    emergency_contact=fields.Char("EmergencyContact",groups="hr.group_hr_user",tracking=True)
    emergency_phone=fields.Char("EmergencyPhone",groups="hr.group_hr_user",tracking=True)
    km_home_work=fields.Integer(string="Home-WorkDistance",groups="hr.group_hr_user",tracking=True)

    image_1920=fields.Image(default=_default_image)
    phone=fields.Char(related='address_home_id.phone',related_sudo=False,readonly=False,string="PrivatePhone",groups="hr.group_hr_user")
    #employeeincompany
    child_ids=fields.One2many('hr.employee','parent_id',string='Directsubordinates')
    category_ids=fields.Many2many(
        'hr.employee.category','employee_category_rel',
        'emp_id','category_id',groups="hr.group_hr_manager",
        string='Tags')
    #misc
    notes=fields.Text('Notes',groups="hr.group_hr_user")
    color=fields.Integer('ColorIndex',default=0)
    barcode=fields.Char(string="BadgeID",help="IDusedforemployeeidentification.",groups="hr.group_hr_user",copy=False)
    pin=fields.Char(string="PIN",groups="hr.group_hr_user",copy=False,
        help="PINusedtoCheckIn/OutinKioskMode(ifenabledinConfiguration).")
    departure_reason=fields.Selection([
        ('fired','Fired'),
        ('resigned','Resigned'),
        ('retired','Retired')
    ],string="DepartureReason",groups="hr.group_hr_user",copy=False,tracking=True)
    departure_description=fields.Text(string="AdditionalInformation",groups="hr.group_hr_user",copy=False,tracking=True)
    departure_date=fields.Date(string="DepartureDate",groups="hr.group_hr_user",copy=False,tracking=True)
    message_main_attachment_id=fields.Many2one(groups="hr.group_hr_user")

    _sql_constraints=[
        ('barcode_uniq','unique(barcode)',"TheBadgeIDmustbeunique,thisoneisalreadyassignedtoanotheremployee."),
        ('user_uniq','unique(user_id,company_id)',"Ausercannotbelinkedtomultipleemployeesinthesamecompany.")
    ]

    defname_get(self):
        ifself.check_access_rights('read',raise_exception=False):
            returnsuper(HrEmployeePrivate,self).name_get()
        returnself.env['hr.employee.public'].browse(self.ids).name_get()

    def_read(self,fields):
        ifself.check_access_rights('read',raise_exception=False):
            returnsuper(HrEmployeePrivate,self)._read(fields)

        res=self.env['hr.employee.public'].browse(self.ids).read(fields)
        forrinres:
            record=self.browse(r['id'])
            record._update_cache({k:vfork,vinr.items()ifkinfields},validate=False)

    defread(self,fields,load='_classic_read'):
        ifself.check_access_rights('read',raise_exception=False):
            returnsuper(HrEmployeePrivate,self).read(fields,load=load)
        private_fields=set(fields).difference(self.env['hr.employee.public']._fields.keys())
        ifprivate_fields:
            raiseAccessError(_('Thefields"%s"youtrytoreadisnotavailableonthepublicemployeeprofile.')%(','.join(private_fields)))
        returnself.env['hr.employee.public'].browse(self.ids).read(fields,load=load)

    @api.model
    defload_views(self,views,options=None):
        ifself.check_access_rights('read',raise_exception=False):
            returnsuper(HrEmployeePrivate,self).load_views(views,options=options)
        returnself.env['hr.employee.public'].load_views(views,options=options)

    @api.model
    def_search(self,args,offset=0,limit=None,order=None,count=False,access_rights_uid=None):
        """
            Weoverridethe_searchbecauseitisthemethodthatcheckstheaccessrights
            Thisiscorrecttooverridethe_search.Thatwayweenforcethefactthatcalling
            searchonanhr.employeereturnsahr.employeerecordset,evenifyoudon'thaveaccess
            tothismodel,astheresultof_search(theidsofthepublicemployees)istobe
            browsedonthehr.employeemodel.Thiscanbetrustedastheidsofthepublic
            employeesexactlymatchtheidsoftherelatedhr.employee.
        """
        ifself.check_access_rights('read',raise_exception=False):
            returnsuper(HrEmployeePrivate,self)._search(args,offset=offset,limit=limit,order=order,count=count,access_rights_uid=access_rights_uid)
        ids=self.env['hr.employee.public']._search(args,offset=offset,limit=limit,order=order,count=count,access_rights_uid=access_rights_uid)
        ifnotcountandisinstance(ids,Query):
            #theresultisexpectedfromthistable,soweshouldlinktables
            ids=super(HrEmployeePrivate,self.sudo())._search([('id','in',ids)])
        returnids

    defget_formview_id(self,access_uid=None):
        """Overridethismethodinordertoredirectmany2onetowardstherightmodeldependingonaccess_uid"""
        ifaccess_uid:
            self_sudo=self.with_user(access_uid)
        else:
            self_sudo=self

        ifself_sudo.check_access_rights('read',raise_exception=False):
            returnsuper(HrEmployeePrivate,self).get_formview_id(access_uid=access_uid)
        #Hardcodetheformviewforpublicemployee
        returnself.env.ref('hr.hr_employee_public_view_form').id

    defget_formview_action(self,access_uid=None):
        """Overridethismethodinordertoredirectmany2onetowardstherightmodeldependingonaccess_uid"""
        res=super(HrEmployeePrivate,self).get_formview_action(access_uid=access_uid)
        ifaccess_uid:
            self_sudo=self.with_user(access_uid)
        else:
            self_sudo=self

        ifnotself_sudo.check_access_rights('read',raise_exception=False):
            res['res_model']='hr.employee.public'

        returnres

    @api.constrains('pin')
    def_verify_pin(self):
        foremployeeinself:
            ifemployee.pinandnotemployee.pin.isdigit():
                raiseValidationError(_("ThePINmustbeasequenceofdigits."))

    @api.onchange('user_id')
    def_onchange_user(self):
        ifself.user_id:
            self.update(self._sync_user(self.user_id,bool(self.image_1920)))
            ifnotself.name:
                self.name=self.user_id.name

    @api.onchange('resource_calendar_id')
    def_onchange_timezone(self):
        ifself.resource_calendar_idandnotself.tz:
            self.tz=self.resource_calendar_id.tz

    def_sync_user(self,user,employee_has_image=False):
        vals=dict(
            work_email=user.email,
            user_id=user.id,
        )
        ifnotemployee_has_image:
            vals['image_1920']=user.image_1920
        ifuser.tz:
            vals['tz']=user.tz
        returnvals

    @api.model
    defcreate(self,vals):
        ifvals.get('user_id'):
            user=self.env['res.users'].browse(vals['user_id'])
            vals.update(self._sync_user(user,vals.get('image_1920')==self._default_image()))
            vals['name']=vals.get('name',user.name)
        employee=super(HrEmployeePrivate,self).create(vals)
        employee._message_subscribe(employee.address_home_id.ids)
        url='/web#%s'%url_encode({
            'action':'hr.plan_wizard_action',
            'active_id':employee.id,
            'active_model':'hr.employee',
            'menu_id':self.env.ref('hr.menu_hr_root').id,
        })
        employee._message_log(body=_('<b>Congratulations!</b>MayIrecommendyoutosetupan<ahref="%s">onboardingplan?</a>')%(url))
        ifemployee.department_id:
            self.env['mail.channel'].sudo().search([
                ('subscription_department_ids','in',employee.department_id.id)
            ])._subscribe_users()
        returnemployee

    defwrite(self,vals):
        if'address_home_id'invals:
            account_id=vals.get('bank_account_id')orself.bank_account_id.id
            ifaccount_id:
                self.env['res.partner.bank'].browse(account_id).partner_id=vals['address_home_id']
            self.message_unsubscribe(self.address_home_id.ids)
            ifvals['address_home_id']:
                self._message_subscribe([vals['address_home_id']])
        ifvals.get('user_id'):
            #Updatetheprofilepictureswithuser,exceptifprovided
            vals.update(self._sync_user(self.env['res.users'].browse(vals['user_id']),bool(vals.get('image_1920'))))
        res=super(HrEmployeePrivate,self).write(vals)
        ifvals.get('department_id')orvals.get('user_id'):
            department_id=vals['department_id']ifvals.get('department_id')elseself[:1].department_id.id
            #Whenaddedtoadepartmentorchanginguser,subscribetothechannelsauto-subscribedbydepartment
            self.env['mail.channel'].sudo().search([
                ('subscription_department_ids','in',department_id)
            ])._subscribe_users()
        returnres

    defunlink(self):
        resources=self.mapped('resource_id')
        super(HrEmployeePrivate,self).unlink()
        returnresources.unlink()

    deftoggle_active(self):
        res=super(HrEmployeePrivate,self).toggle_active()
        unarchived_employees=self.filtered(lambdaemployee:employee.active)
        unarchived_employees.write({
            'departure_reason':False,
            'departure_description':False,
            'departure_date':False
        })
        archived_addresses=unarchived_employees.mapped('address_home_id').filtered(lambdaaddr:notaddr.active)
        archived_addresses.toggle_active()
        iflen(self)==1andnotself.active:
            return{
                'type':'ir.actions.act_window',
                'name':_('RegisterDeparture'),
                'res_model':'hr.departure.wizard',
                'view_mode':'form',
                'target':'new',
                'context':{'active_id':self.id},
                'views':[[False,'form']]
            }
        returnres

    defgenerate_random_barcode(self):
        foremployeeinself:
            employee.barcode='041'+"".join(choice(digits)foriinrange(9))

    @api.depends('address_home_id.parent_id')
    def_compute_is_address_home_a_company(self):
        """Checksthatchosenaddress(res.partner)isnotlinkedtoacompany.
        """
        foremployeeinself:
            try:
                employee.is_address_home_a_company=employee.address_home_id.parent_id.idisnotFalse
            exceptAccessError:
                employee.is_address_home_a_company=False

    #---------------------------------------------------------
    #BusinessMethods
    #---------------------------------------------------------

    @api.model
    defget_import_templates(self):
        return[{
            'label':_('ImportTemplateforEmployees'),
            'template':'/hr/static/xls/hr_employee.xls'
        }]

    def_post_author(self):
        """
        Whenauserupdateshisownemployee'sdata,alloperationsareperformed
        bysuperuser.However,trackingmessagesshouldnotbepostedasFlectraBot
        butastheactualuser.
        Thismethodisusedintheoverridesof`_message_log`and`message_post`
        topostmessagesasthecorrectuser.
        """
        real_user=self.env.context.get('binary_field_real_user')
        ifself.env.is_superuser()andreal_user:
            self=self.with_user(real_user)
        returnself

    #---------------------------------------------------------
    #Messaging
    #---------------------------------------------------------

    def_message_log(self,**kwargs):
        returnsuper(HrEmployeePrivate,self._post_author())._message_log(**kwargs)

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,**kwargs):
        returnsuper(HrEmployeePrivate,self._post_author()).message_post(**kwargs)

    def_sms_get_partner_fields(self):
        return['user_partner_id']

    def_sms_get_number_fields(self):
        return['mobile_phone']
