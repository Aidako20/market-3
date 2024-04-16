#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromastimportliteral_eval
fromflectraimportfields,models,_,api
fromflectra.exceptionsimportUserError
fromflectra.fieldsimportDatetime

_logger=logging.getLogger(__name__)


classEmployee(models.AbstractModel):
    _inherit='hr.employee.base'

    email_sent=fields.Boolean(default=False)
    ip_connected=fields.Boolean(default=False)
    manually_set_present=fields.Boolean(default=False)

    #Storedfieldusedinthepresencekanbanreportingview
    #toallowgroupbystate.
    hr_presence_state_display=fields.Selection([
        ('to_define','ToDefine'),
        ('present','Present'),
        ('absent','Absent'),
        ])

    def_compute_presence_state(self):
        super()._compute_presence_state()
        employees=self.filtered(lambdae:e.hr_presence_state!='present'andnote.is_absent)
        company=self.env.company
        employee_to_check_working=employees.filtered(lambdae:
                                                       note.is_absentand
                                                       (e.email_sentore.ip_connectedore.manually_set_present))
        working_now_list=employee_to_check_working._get_employee_working_now()
        foremployeeinemployees:
            ifnotemployee.is_absentandcompany.hr_presence_last_compute_dateandemployee.idinworking_now_listand\
                    company.hr_presence_last_compute_date.day==Datetime.now().dayand\
                    (employee.email_sentoremployee.ip_connectedoremployee.manually_set_present):
                employee.hr_presence_state='present'

    @api.model
    def_check_presence(self):
        company=self.env.company
        ifnotcompany.hr_presence_last_compute_dateor\
                company.hr_presence_last_compute_date.day!=Datetime.now().day:
            self.env['hr.employee'].search([
                ('company_id','=',company.id)
            ]).write({
                'email_sent':False,
                'ip_connected':False,
                'manually_set_present':False
            })

        employees=self.env['hr.employee'].search([('company_id','=',company.id)])
        all_employees=employees


        #CheckonIP
        ifliteral_eval(self.env['ir.config_parameter'].sudo().get_param('hr_presence.hr_presence_control_ip','False')):
            ip_list=company.hr_presence_control_ip_list
            ip_list=ip_list.split(',')ifip_listelse[]
            ip_employees=self.env['hr.employee']
            foremployeeinemployees:
                employee_ips=self.env['res.users.log'].search([
                    ('create_uid','=',employee.user_id.id),
                    ('ip','!=',False),
                    ('create_date','>=',Datetime.to_string(Datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)))]
                ).mapped('ip')
                ifany(ipinip_listforipinemployee_ips):
                    ip_employees|=employee
            ip_employees.write({'ip_connected':True})
            employees=employees-ip_employees

        #Checkonsentemails
        ifliteral_eval(self.env['ir.config_parameter'].sudo().get_param('hr_presence.hr_presence_control_email','False')):
            email_employees=self.env['hr.employee']
            threshold=company.hr_presence_control_email_amount
            foremployeeinemployees:
                sent_emails=self.env['mail.message'].search_count([
                    ('author_id','=',employee.user_id.partner_id.id),
                    ('date','>=',Datetime.to_string(Datetime.now().replace(hour=0,minute=0,second=0,microsecond=0))),
                    ('date','<=',Datetime.to_string(Datetime.now()))])
                ifsent_emails>=threshold:
                    email_employees|=employee
            email_employees.write({'email_sent':True})
            employees=employees-email_employees

        company.sudo().hr_presence_last_compute_date=Datetime.now()

        foremployeeinall_employees:
            employee.hr_presence_state_display=employee.hr_presence_state

    @api.model
    def_action_open_presence_view(self):
        #Computethepresence/absencefortheemployeesonthesame
        #companythantheHR/manager.Thenopensthekanbanview
        #oftheemployeeswithanundefinedpresence/absence

        _logger.info("Employeespresencecheckedby:%s"%self.env.user.name)

        self._check_presence()

        return{
            "type":"ir.actions.act_window",
            "res_model":"hr.employee",
            "views":[[self.env.ref('hr_presence.hr_employee_view_kanban').id,"kanban"],[False,"tree"],[False,"form"]],
            'view_mode':'kanban,tree,form',
            "domain":[],
            "name":_("Employee'sPresencetoDefine"),
            "search_view_id":[self.env.ref('hr_presence.hr_employee_view_presence_search').id,'search'],
            "context":{'search_default_group_hr_presence_state':1,
                        'searchpanel_default_hr_presence_state_display':'to_define'},
        }

    defaction_set_present(self):
        ifnotself.env.user.has_group('hr.group_hr_manager'):
            raiseUserError(_("Youdon'thavetherighttodothis.PleasecontactanAdministrator."))
        self.write({'manually_set_present':True})

    defwrite(self,vals):
        ifvals.get('hr_presence_state_display')=='present':
            vals['manually_set_present']=True
        returnsuper().write(vals)

    defaction_open_leave_request(self):
        self.ensure_one()
        return{
            "type":"ir.actions.act_window",
            "res_model":"hr.leave",
            "views":[[False,"form"]],
            "view_mode":'form',
            "context":{'default_employee_id':self.id},
        }

    #--------------------------------------------------
    #Messaging
    #--------------------------------------------------

    defaction_send_sms(self):
        self.ensure_one()
        ifnotself.env.user.has_group('hr.group_hr_manager'):
            raiseUserError(_("Youdon'thavetherighttodothis.PleasecontactanAdministrator."))
        ifnotself.mobile_phone:
            raiseUserError(_("Thereisnoprofessionalmobileforthisemployee."))

        context=dict(self.env.context)
        context.update(default_res_model='hr.employee',default_res_id=self.id,default_composition_mode='comment',default_number_field_name='mobile_phone')

        template=self.env.ref('hr_presence.sms_template_presence',False)
        ifnottemplate:
            context['default_body']=_("""Exceptionmadeiftherewasamistakeofours,itseemsthatyouarenotatyourofficeandthereisnotrequestoftimeofffromyou.
Please,takeappropriatemeasuresinordertocarryoutthisworkabsence.
Donothesitatetocontactyourmanagerorthehumanresourcedepartment.""")
        else:
            context['default_template_id']=template.id

        return{
            "type":"ir.actions.act_window",
            "res_model":"sms.composer",
            "view_mode":'form',
            "context":context,
            "name":"SendSMSTextMessage",
            "target":"new",
        }

    defaction_send_mail(self):
        self.ensure_one()
        ifnotself.env.user.has_group('hr.group_hr_manager'):
            raiseUserError(_("Youdon'thavetherighttodothis.PleasecontactanAdministrator."))
        ifnotself.work_email:
            raiseUserError(_("Thereisnoprofessionalemailaddressforthisemployee."))
        template=self.env.ref('hr_presence.mail_template_presence',False)
        compose_form=self.env.ref('mail.email_compose_message_wizard_form',False)
        ctx=dict(
            default_model="hr.employee",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            default_is_log=True,
            custom_layout='mail.mail_notification_light',
        )
        return{
            'name':_('ComposeEmail'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.compose.message',
            'views':[(compose_form.id,'form')],
            'view_id':compose_form.id,
            'target':'new',
            'context':ctx,
        }
