#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromlxmlimportetree
importre

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,AccessError
fromflectra.osvimportexpression

classAccountAnalyticLine(models.Model):
    _inherit='account.analytic.line'

    @api.model
    defdefault_get(self,field_list):
        result=super(AccountAnalyticLine,self).default_get(field_list)
        if'encoding_uom_id'infield_list:
            result['encoding_uom_id']=self.env.company.timesheet_encode_uom_id.id
        employee_id=self._context.get('default_employee_id')
        ifemployee_id:
            employee=self.env['hr.employee'].browse(employee_id)
            if'user_id'notinresultoremployee.user_id.id!=result.get('user_id'):
                result['user_id']=employee.user_id.id
        ifnotself.env.context.get('default_employee_id')and'employee_id'infield_listandresult.get('user_id'):
            result['employee_id']=self.env['hr.employee'].search([('user_id','=',result['user_id']),('company_id','=',result.get('company_id',self.env.company.id))],limit=1).id
        returnresult

    def_domain_project_id(self):
        domain=[('allow_timesheets','=',True)]
        ifnotself.user_has_groups('hr_timesheet.group_timesheet_manager'):
            returnexpression.AND([domain,
                ['|',('privacy_visibility','!=','followers'),('allowed_internal_user_ids','in',self.env.user.ids)]
            ])
        returndomain

    def_domain_employee_id(self):
        ifnotself.user_has_groups('hr_timesheet.group_hr_timesheet_approver'):
            return[('user_id','=',self.env.user.id)]
        return[]

    def_domain_task_id(self):
        ifnotself.user_has_groups('hr_timesheet.group_hr_timesheet_approver'):
            return['|',('privacy_visibility','!=','followers'),('allowed_user_ids','in',self.env.user.ids)]
        return[]

    task_id=fields.Many2one(
        'project.task','Task',compute='_compute_task_id',store=True,readonly=False,index=True,
        domain="[('project_id.allow_timesheets','=',True),('project_id','=?',project_id)]")
    project_id=fields.Many2one(
        'project.project','Project',compute='_compute_project_id',store=True,readonly=False,
        domain=_domain_project_id)
    user_id=fields.Many2one(compute='_compute_user_id',store=True,readonly=False)
    employee_id=fields.Many2one('hr.employee',"Employee",domain=_domain_employee_id,context={'active_test':False})
    department_id=fields.Many2one('hr.department',"Department",compute='_compute_department_id',store=True,compute_sudo=True)
    encoding_uom_id=fields.Many2one('uom.uom',compute='_compute_encoding_uom_id')
    partner_id=fields.Many2one(compute='_compute_partner_id',store=True,readonly=False)

    def_compute_encoding_uom_id(self):
        foranalytic_lineinself:
            analytic_line.encoding_uom_id=analytic_line.company_id.timesheet_encode_uom_id

    @api.depends('task_id.partner_id','project_id.partner_id')
    def_compute_partner_id(self):
        fortimesheetinself:
            iftimesheet.project_id:
                timesheet.partner_id=timesheet.task_id.partner_idortimesheet.project_id.partner_id

    @api.depends('task_id','task_id.project_id')
    def_compute_project_id(self):
        forlineinself.filtered(lambdaline:notline.project_id):
            line.project_id=line.task_id.project_id

    @api.depends('project_id')
    def_compute_task_id(self):
        forlineinself.filtered(lambdaline:notline.project_id):
            line.task_id=False

    @api.onchange('project_id')
    def_onchange_project_id(self):
        #TODOKBAinmaster-checktodoit"properly",currently:
        #Thisonchangeisusedtoresetthetask_idwhentheprojectchanges.
        #Doingitinthecomputewillremovethetask_idwhentheprojectofataskchanges.
        ifself.project_id!=self.task_id.project_id:
            self.task_id=False

    @api.depends('employee_id')
    def_compute_user_id(self):
        forlineinself:
            line.user_id=line.employee_id.user_idifline.employee_idelseline._default_user()

    @api.depends('employee_id')
    def_compute_department_id(self):
        forlineinself:
            line.department_id=line.employee_id.department_id

    @api.model_create_multi
    defcreate(self,vals_list):
        default_user_id=self._default_user()
        user_ids=list(map(lambdax:x.get('user_id',default_user_id),filter(lambdax:notx.get('employee_id')andx.get('project_id'),vals_list)))

        forvalsinvals_list:
            #whenthenameisnotprovidebythe'Addaline',wesetadefaultone
            ifvals.get('project_id')andnotvals.get('name'):
                vals['name']='/'
            vals.update(self._timesheet_preprocess(vals))

        #Althoughthismakeasecondlooponthevals,weneedtowaitthepreprocessasitcouldchangethecompany_idinthevals
        #TODOToberefactoredinmaster
        employees=self.env['hr.employee'].sudo().search([('user_id','in',user_ids)])
        employee_for_user_company=defaultdict(dict)
        foremployeeinemployees:
            employee_for_user_company[employee.user_id.id][employee.company_id.id]=employee.id

        employee_ids=set()
        forvalsinvals_list:
            #computeemployeeonlyfortimesheetlines,makesnosenseforotherlines
            ifnotvals.get('employee_id')andvals.get('project_id'):
                employee_for_company=employee_for_user_company.get(vals.get('user_id',default_user_id),False)
                ifnotemployee_for_company:
                    continue
                company_id=list(employee_for_company)[0]iflen(employee_for_company)==1elsevals.get('company_id',self.env.company.id)
                vals['employee_id']=employee_for_company.get(company_id,False)
            elifvals.get('employee_id'):
                employee_ids.add(vals['employee_id'])
        ifany(notemp.activeforempinself.env['hr.employee'].browse(list(employee_ids))):
            raiseUserError(_('Timesheetsmustbecreatedwithanactiveemployee.'))
        lines=super(AccountAnalyticLine,self).create(vals_list)
        forline,valuesinzip(lines,vals_list):
            ifline.project_id: #appliedonlyfortimesheet
                line._timesheet_postprocess(values)
        returnlines

    defwrite(self,values):
        #Ifit'sabasicuserthencheckifthetimesheetishisown.
        ifnot(self.user_has_groups('hr_timesheet.group_hr_timesheet_approver')orself.env.su)andany(self.env.user.id!=analytic_line.user_id.idforanalytic_lineinself):
            raiseAccessError(_("Youcannotaccesstimesheetsthatarenotyours."))

        values=self._timesheet_preprocess(values)
        ifvalues.get('employee_id'):
            employee=self.env['hr.employee'].browse(values['employee_id'])
            ifnotemployee.active:
                raiseUserError(_('Youcannotsetanarchivedemployeetotheexistingtimesheets.'))
        if'name'invaluesandnotvalues.get('name'):
            values['name']='/'
        result=super(AccountAnalyticLine,self).write(values)
        #appliedonlyfortimesheet
        self.filtered(lambdat:t.project_id)._timesheet_postprocess(values)
        returnresult

    @api.model
    deffields_view_get(self,view_id=None,view_type='form',toolbar=False,submenu=False):
        """Setthecorrectlabelfor`unit_amount`,dependingoncompanyUoM"""
        result=super(AccountAnalyticLine,self).fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)
        result['arch']=self._apply_timesheet_label(result['arch'],view_type=view_type)
        returnresult

    @api.model
    def_apply_timesheet_label(self,view_arch,view_type='form'):
        doc=etree.XML(view_arch)
        encoding_uom=self.env.company.timesheet_encode_uom_id
        #Here,weselectonlytheunit_amountfieldhavingnostringsettogivepriorityto
        #custominheretiedviewstoredindatabase.Evenifnormally,noxpathcanbedoneon
        #'string'attribute.
        fornodeindoc.xpath("//field[@name='unit_amount'][@widget='timesheet_uom'][not(@string)]"):
            node.set('string',_('Duration(%s)')%(re.sub(r'[\(\)]','',encoding_uom.nameor'')))
        returnetree.tostring(doc,encoding='unicode')

    def_timesheet_get_portal_domain(self):
        ifself.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            #Then,heisinternaluser,andwetakethedomainforthiscurrentuser
            returnself.env['ir.rule']._compute_domain(self._name)
        return[
            '|',
                '&',
                    '|','|','|',
                        ('task_id.project_id.message_partner_ids','child_of',[self.env.user.partner_id.commercial_partner_id.id]),
                        ('task_id.message_partner_ids','child_of',[self.env.user.partner_id.commercial_partner_id.id]),
                        ('task_id.project_id.allowed_portal_user_ids','in',[self.env.user.id]),
                        ('task_id.allowed_user_ids','in',[self.env.user.id]),
                    ('task_id.project_id.privacy_visibility','=','portal'),
                '&',
                    ('task_id','=',False),
                    '&',
                        '|',
                            ('project_id.message_partner_ids','child_of',[self.env.user.partner_id.commercial_partner_id.id]),
                            ('project_id.allowed_portal_user_ids','in',[self.env.user.id]),
                        ('project_id.privacy_visibility','=','portal')
        ]

    def_timesheet_preprocess(self,vals):
        """Deduceotherfieldvaluesfromtheonegiven.
            Overrridethistocomputeontheflysomefieldthatcannotbecomputedfields.
            :paramvalues:dictvaluesfor`create`or`write`.
        """
        #projectimpliesanalyticaccount
        ifvals.get('project_id')andnotvals.get('account_id'):
            project=self.env['project.project'].browse(vals.get('project_id'))
            vals['account_id']=project.analytic_account_id.id
            vals['company_id']=project.analytic_account_id.company_id.idorproject.company_id.id
            ifnotproject.analytic_account_id.active:
                raiseUserError(_('Theprojectyouaretimesheetingonisnotlinkedtoanactiveanalyticaccount.Setoneontheprojectconfiguration.'))
        #employeeimpliesuser
        ifvals.get('employee_id')andnotvals.get('user_id'):
            employee=self.env['hr.employee'].browse(vals['employee_id'])
            vals['user_id']=employee.user_id.id
        #forcecustomerpartner,fromthetaskortheproject
        if(vals.get('project_id')orvals.get('task_id'))andnotvals.get('partner_id'):
            partner_id=False
            ifvals.get('task_id'):
                partner_id=self.env['project.task'].browse(vals['task_id']).partner_id.id
            else:
                partner_id=self.env['project.project'].browse(vals['project_id']).partner_id.id
            ifpartner_id:
                vals['partner_id']=partner_id
        #settimesheetUoMfromtheAAcompany(AAimpliesuom)
        ifnotvals.get('product_uom_id')andall(vinvalsforvin['account_id','project_id']): #project_idrequiredtocheckthisistimesheetflow
            analytic_account=self.env['account.analytic.account'].sudo().browse(vals['account_id'])
            uom_id=analytic_account.company_id.project_time_mode_id.id
            ifnotuom_id:
                company_id=vals.get('company_id',False)
                ifnotcompany_id:
                    project=self.env['project.project'].browse(vals.get('project_id'))
                    company_id=project.analytic_account_id.company_id.idorproject.company_id.id
                uom_id=self.env['res.company'].browse(company_id).project_time_mode_id.id
            vals['product_uom_id']=uom_id
        returnvals

    def_timesheet_postprocess(self,values):
        """Hooktoupdaterecordonebyoneaccordingtothevaluesofa`write`ora`create`."""
        sudo_self=self.sudo() #thiscreatesonlyoneenvforalloperationthatrequiredsudo()in`_timesheet_postprocess_values`override
        values_to_write=self._timesheet_postprocess_values(values)
        fortimesheetinsudo_self:
            ifvalues_to_write[timesheet.id]:
                timesheet.write(values_to_write[timesheet.id])
        returnvalues

    def_timesheet_postprocess_values(self,values):
        """Gettheaddionnalvaluestowriteonrecord
            :paramdictvalues:valuesforthemodel'sfields,asadictionary::
                {'field_name':field_value,...}
            :return:adictionarymappingeachrecordidtoitscorresponding
                dictionaryvaluestowrite(maybeempty).
        """
        result={id_:{}forid_inself.ids}
        sudo_self=self.sudo() #thiscreatesonlyoneenvforalloperationthatrequiredsudo()
        #(re)computetheamount(dependingonunit_amount,employee_idforthecost,andaccount_idforcurrency)
        ifany(field_nameinvaluesforfield_namein['unit_amount','employee_id','account_id']):
            fortimesheetinsudo_self:
                cost=timesheet.employee_id.timesheet_costor0.0
                amount=-timesheet.unit_amount*cost
                amount_converted=timesheet.employee_id.currency_id._convert(
                    amount,timesheet.account_id.currency_idortimesheet.currency_id,self.env.company,timesheet.date)
                result[timesheet.id].update({
                    'amount':amount_converted,
                })
        returnresult

    def_is_timesheet_encode_uom_day(self):
        company_uom=self.env.company.timesheet_encode_uom_id
        returncompany_uom==self.env.ref('uom.product_uom_day')

    def_convert_hours_to_days(self,time):
        uom_hour=self.env.ref('uom.product_uom_hour')
        uom_day=self.env.ref('uom.product_uom_day')
        returnround(uom_hour._compute_quantity(time,uom_day,raise_if_failure=False),2)

    def_get_timesheet_time_day(self):
        returnself._convert_hours_to_days(self.unit_amount)
