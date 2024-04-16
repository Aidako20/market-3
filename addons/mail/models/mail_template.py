#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importlogging


fromflectraimport_,api,fields,models,tools
fromflectra.exceptionsimportUserError

_logger=logging.getLogger(__name__)


classMailTemplate(models.Model):
    "Templatesforsendingemail"
    _name="mail.template"
    _inherit=['mail.render.mixin']
    _description='EmailTemplates'
    _order='name'

    @api.model
    defdefault_get(self,fields):
        res=super(MailTemplate,self).default_get(fields)
        ifres.get('model'):
            res['model_id']=self.env['ir.model']._get(res.pop('model')).id
        returnres

    #description
    name=fields.Char('Name')
    model_id=fields.Many2one('ir.model','Appliesto',help="Thetypeofdocumentthistemplatecanbeusedwith")
    model=fields.Char('RelatedDocumentModel',related='model_id.model',index=True,store=True,readonly=True)
    subject=fields.Char('Subject',translate=True,help="Subject(placeholdersmaybeusedhere)")
    email_from=fields.Char('From',
                             help="Senderaddress(placeholdersmaybeusedhere).Ifnotset,thedefault"
                                  "valuewillbetheauthor'semailaliasifconfigured,oremailaddress.")
    #recipients
    use_default_to=fields.Boolean(
        'Defaultrecipients',
        help="Defaultrecipientsoftherecord:\n"
             "-partner(usingidonapartnerorthepartner_idfield)OR\n"
             "-email(usingemail_fromoremailfield)")
    email_to=fields.Char('To(Emails)',help="Comma-separatedrecipientaddresses(placeholdersmaybeusedhere)")
    partner_to=fields.Char('To(Partners)',
                             help="Comma-separatedidsofrecipientpartners(placeholdersmaybeusedhere)")
    email_cc=fields.Char('Cc',help="Carboncopyrecipients(placeholdersmaybeusedhere)")
    reply_to=fields.Char('Reply-To',help="Preferredresponseaddress(placeholdersmaybeusedhere)")
    #content
    body_html=fields.Html('Body',translate=True,sanitize=False)
    attachment_ids=fields.Many2many('ir.attachment','email_template_attachment_rel','email_template_id',
                                      'attachment_id','Attachments',
                                      help="Youmayattachfilestothistemplate,tobeaddedtoall"
                                           "emailscreatedfromthistemplate")
    report_name=fields.Char('ReportFilename',translate=True,
                              help="Nametouseforthegeneratedreportfile(maycontainplaceholders)\n"
                                   "Theextensioncanbeomittedandwillthencomefromthereporttype.")
    report_template=fields.Many2one('ir.actions.report','Optionalreporttoprintandattach')
    #options
    mail_server_id=fields.Many2one('ir.mail_server','OutgoingMailServer',readonly=False,
                                     help="Optionalpreferredserverforoutgoingmails.Ifnotset,thehighest"
                                          "priorityonewillbeused.")
    scheduled_date=fields.Char('ScheduledDate',help="Ifset,thequeuemanagerwillsendtheemailafterthedate.Ifnotset,theemailwillbesendassoonaspossible.Jinja2placeholdersmaybeused.")
    auto_delete=fields.Boolean(
        'AutoDelete',default=True,
        help="Thisoptionpermanentlyremovesanytrackofemailafterit'sbeensent,includingfromtheTechnicalmenuintheSettings,inordertopreservestoragespaceofyourFlectradatabase.")
    #contextualaction
    ref_ir_act_window=fields.Many2one('ir.actions.act_window','Sidebaraction',readonly=True,copy=False,
                                        help="Sidebaractiontomakethistemplateavailableonrecords"
                                             "oftherelateddocumentmodel")

    def_fix_attachment_ownership(self):
        forrecordinself:
            record.attachment_ids.write({'res_model':record._name,'res_id':record.id})
        returnself

    @api.model_create_multi
    defcreate(self,values_list):
        returnsuper().create(values_list)\
            ._fix_attachment_ownership()

    defwrite(self,vals):
        super().write(vals)
        self._fix_attachment_ownership()
        returnTrue

    defunlink(self):
        self.unlink_action()
        returnsuper(MailTemplate,self).unlink()

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        default=dict(defaultor{},
                       name=_("%s(copy)",self.name))
        returnsuper(MailTemplate,self).copy(default=default)

    defunlink_action(self):
        fortemplateinself:
            iftemplate.ref_ir_act_window:
                template.ref_ir_act_window.unlink()
        returnTrue

    defcreate_action(self):
        ActWindow=self.env['ir.actions.act_window']
        view=self.env.ref('mail.email_compose_message_wizard_form')

        fortemplateinself:
            button_name=_('SendMail(%s)',template.name)
            action=ActWindow.create({
                'name':button_name,
                'type':'ir.actions.act_window',
                'res_model':'mail.compose.message',
                'context':"{'default_composition_mode':'mass_mail','default_template_id':%d,'default_use_template':True}"%(template.id),
                'view_mode':'form,tree',
                'view_id':view.id,
                'target':'new',
                'binding_model_id':template.model_id.id,
            })
            template.write({'ref_ir_act_window':action.id})

        returnTrue

    #------------------------------------------------------------
    #MESSAGE/EMAILVALUESGENERATION
    #------------------------------------------------------------

    defgenerate_recipients(self,results,res_ids):
        """Generatestherecipientsofthetemplate.Defaultvaluescanbengenerated
        insteadofthetemplatevaluesifrequestedbytemplateorcontext.
        Emails(email_to,email_cc)canbetransformedintopartnersifrequested
        inthecontext."""
        self.ensure_one()

        ifself.use_default_toorself._context.get('tpl_force_default_to'):
            records=self.env[self.model].browse(res_ids).sudo()
            default_recipients=records._message_get_default_recipients()
            forres_id,recipientsindefault_recipients.items():
                results[res_id].pop('partner_to',None)
                results[res_id].update(recipients)

        records_company=None
        ifself._context.get('tpl_partners_only')andself.modelandresultsand'company_id'inself.env[self.model]._fields:
            records=self.env[self.model].browse(results.keys()).read(['company_id'])
            records_company={rec['id']:(rec['company_id'][0]ifrec['company_id']elseNone)forrecinrecords}

        forres_id,valuesinresults.items():
            partner_ids=values.get('partner_ids',list())
            ifself._context.get('tpl_partners_only'):
                mails=tools.email_split(values.pop('email_to',''))+tools.email_split(values.pop('email_cc',''))
                Partner=self.env['res.partner']
                ifrecords_company:
                    Partner=Partner.with_context(default_company_id=records_company[res_id])
                formailinmails:
                    partner=Partner.find_or_create(mail)
                    partner_ids.append(partner.id)
            partner_to=values.pop('partner_to','')
            ifpartner_to:
                #placeholderscouldgenerate'',3,2duetosomeemptyfieldvalues
                tpl_partner_ids=[int(pid.strip())forpidinpartner_to.split(',')if(pidandpid.strip().isdigit())]
                partner_ids+=self.env['res.partner'].sudo().browse(tpl_partner_ids).exists().ids
            results[res_id]['partner_ids']=partner_ids
        returnresults

    defgenerate_email(self,res_ids,fields):
        """Generatesanemailfromthetemplateforgiventhegivenmodelbasedon
        recordsgivenbyres_ids.

        :paramres_id:idoftherecordtouseforrenderingthetemplate(model
                       istakenfromtemplatedefinition)
        :returns:adictcontainingallrelevantfieldsforcreatinganew
                  mail.mailentry,withoneextrakey``attachments``,inthe
                  format[(report_name,data)]wheredataisbase64encoded.
        """
        self.ensure_one()
        multi_mode=True
        ifisinstance(res_ids,int):
            res_ids=[res_ids]
            multi_mode=False

        results=dict()
        forlang,(template,template_res_ids)inself._classify_per_lang(res_ids).items():
            forfieldinfields:
                template=template.with_context(safe=(field=='subject'))
                generated_field_values=template._render_field(
                    field,template_res_ids,
                    post_process=(field=='body_html')
                )
                forres_id,field_valueingenerated_field_values.items():
                    results.setdefault(res_id,dict())[field]=field_value
            #computerecipients
            ifany(fieldinfieldsforfieldin['email_to','partner_to','email_cc']):
                results=template.generate_recipients(results,template_res_ids)
            #updatevaluesforallres_ids
            forres_idintemplate_res_ids:
                values=results[res_id]
                ifvalues.get('body_html'):
                    values['body']=tools.html_sanitize(values['body_html'])
                #technicalsettings
                values.update(
                    mail_server_id=template.mail_server_id.idorFalse,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_idorFalse,
                    attachment_ids=[attach.idforattachintemplate.attachment_ids],
                )

            #Addreportinattachments:generateonceforalltemplate_res_ids
            iftemplate.report_template:
                forres_idintemplate_res_ids:
                    attachments=[]
                    report_name=template._render_field('report_name',[res_id])[res_id]
                    report=template.report_template
                    report_service=report.report_name

                    ifreport.report_typein['qweb-html','qweb-pdf']:
                        result,format=report._render_qweb_pdf([res_id])
                    else:
                        res=report._render([res_id])
                        ifnotres:
                            raiseUserError(_('Unsupportedreporttype%sfound.',report.report_type))
                        result,format=res

                    #TODOintrunk,changereturnformattobinarytomatchmessage_postexpectedformat
                    result=base64.b64encode(result)
                    ifnotreport_name:
                        report_name='report.'+report_service
                    ext="."+format
                    ifnotreport_name.endswith(ext):
                        report_name+=ext
                    attachments.append((report_name,result))
                    results[res_id]['attachments']=attachments

        returnmulti_modeandresultsorresults[res_ids[0]]

    #------------------------------------------------------------
    #EMAIL
    #------------------------------------------------------------

    def_send_check_access(self,res_ids):
        records=self.env[self.model].browse(res_ids)
        records.check_access_rights('read')
        records.check_access_rule('read')

    defsend_mail(self,res_id,force_send=False,raise_exception=False,email_values=None,notif_layout=False):
        """Generatesanewmail.mail.Templateisrenderedonrecordgivenby
        res_idandmodelcomingfromtemplate.

        :paramintres_id:idoftherecordtorenderthetemplate
        :paramboolforce_send:sendemailimmediately;otherwiseusethemail
            queue(recommended);
        :paramdictemail_values:updategeneratedmailwiththosevaluestofurther
            customizethemail;
        :paramstrnotif_layout:optionalnotificationlayouttoencapsulatethe
            generatedemail;
        :returns:idofthemail.mailthatwascreated"""

        #Grantaccesstosend_mailonlyifaccesstorelateddocument
        self.ensure_one()
        self._send_check_access([res_id])

        Attachment=self.env['ir.attachment'] #TDEFIXME:shouldremovedefault_typefromcontext

        #createamail_mailbasedonvalues,withoutattachments
        values=self.generate_email(res_id,['subject','body_html','email_from','email_to','partner_to','email_cc','reply_to','scheduled_date'])
        values['recipient_ids']=[(4,pid)forpidinvalues.get('partner_ids',list())]
        values['attachment_ids']=[(4,aid)foraidinvalues.get('attachment_ids',list())]
        values.update(email_valuesor{})
        attachment_ids=values.pop('attachment_ids',[])
        attachments=values.pop('attachments',[])
        #addaprotectionagainstvoidemail_from
        if'email_from'invaluesandnotvalues.get('email_from'):
            values.pop('email_from')
        #encapsulatebody
        ifnotif_layoutandvalues['body_html']:
            try:
                template=self.env.ref(notif_layout,raise_if_not_found=True)
            exceptValueError:
                _logger.warning('QWebtemplate%snotfoundwhensendingtemplate%s.Sendingwithoutlayouting.'%(notif_layout,self.name))
            else:
                record=self.env[self.model].browse(res_id)
                model=self.env['ir.model']._get(record._name)

                ifself.lang:
                    lang=self._render_lang([res_id])[res_id]
                    template=template.with_context(lang=lang)
                    model=model.with_context(lang=lang)

                template_ctx={
                    'message':self.env['mail.message'].sudo().new(dict(body=values['body_html'],record_name=record.display_name)),
                    'model_description':model.display_name,
                    'company':'company_id'inrecordandrecord['company_id']orself.env.company,
                    'record':record,
                }
                body=template._render(template_ctx,engine='ir.qweb',minimal_qcontext=True)
                values['body_html']=self.env['mail.render.mixin']._replace_local_links(body)
        mail=self.env['mail.mail'].sudo().create(values)

        #manageattachments
        forattachmentinattachments:
            attachment_data={
                'name':attachment[0],
                'datas':attachment[1],
                'type':'binary',
                'res_model':'mail.message',
                'res_id':mail.mail_message_id.id,
            }
            attachment_ids.append((4,Attachment.create(attachment_data).id))
        ifattachment_ids:
            mail.write({'attachment_ids':attachment_ids})

        ifforce_send:
            mail.send(raise_exception=raise_exception)
        returnmail.id #TDECLEANME:returnmail+api.returns?
