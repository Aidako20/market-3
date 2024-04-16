#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classCrmLeadForwardToPartner(models.TransientModel):
    """Forwardinfohistorytopartners."""
    _name='crm.lead.forward.to.partner'
    _description='Leadforwardtopartner'

    @api.model
    def_convert_to_assignation_line(self,lead,partner):
        lead_location=[]
        partner_location=[]
        iflead.country_id:
            lead_location.append(lead.country_id.name)
        iflead.city:
            lead_location.append(lead.city)
        ifpartner:
            ifpartner.country_id:
                partner_location.append(partner.country_id.name)
            ifpartner.city:
                partner_location.append(partner.city)
        return{'lead_id':lead.id,
                'lead_location':",".join(lead_location),
                'partner_assigned_id':partnerandpartner.idorFalse,
                'partner_location':",".join(partner_location),
                'lead_link':self.get_lead_portal_url(lead.id,lead.type),
                }

    @api.model
    defdefault_get(self,fields):
        res=super(CrmLeadForwardToPartner,self).default_get(fields)
        active_ids=self.env.context.get('active_ids')
        if'body'infields:
            template=self.env.ref('website_crm_partner_assign.email_template_lead_forward_mail',False)
            iftemplate:
                res['body']=template.body_html
        ifactive_ids:
            default_composition_mode=self.env.context.get('default_composition_mode')
            res['assignation_lines']=[]
            leads=self.env['crm.lead'].browse(active_ids)
            ifdefault_composition_mode=='mass_mail':
                partner_assigned_dict=leads.search_geo_partner()
            else:
                partner_assigned_dict={lead.id:lead.partner_assigned_id.idforleadinleads}
                res['partner_id']=leads[0].partner_assigned_id.id
            forleadinleads:
                partner_id=partner_assigned_dict.get(lead.id)orFalse
                partner=self.env['res.partner'].browse(partner_id)
                res['assignation_lines'].append((0,0,self._convert_to_assignation_line(lead,partner)))
        returnres

    defaction_forward(self):
        self.ensure_one()
        template=self.env.ref('website_crm_partner_assign.email_template_lead_forward_mail',False)
        ifnottemplate:
            raiseUserError(_('TheForwardEmailTemplateisnotinthedatabase'))
        portal_group=self.env.ref('base.group_portal')

        local_context=self.env.context.copy()
        ifnot(self.forward_type=='single'):
            no_email=set()
            forleadinself.assignation_lines:
                iflead.partner_assigned_idandnotlead.partner_assigned_id.email:
                    no_email.add(lead.partner_assigned_id.name)
            ifno_email:
                raiseUserError(_('Setanemailaddressforthepartner(s):%s')%",".join(no_email))
        ifself.forward_type=='single'andnotself.partner_id.email:
            raiseUserError(_('Setanemailaddressforthepartner%s',self.partner_id.name))

        partners_leads={}
        forleadinself.assignation_lines:
            partner=self.forward_type=='single'andself.partner_idorlead.partner_assigned_id
            lead_details={
                'lead_link':lead.lead_link,
                'lead_id':lead.lead_id,
            }
            ifpartner:
                partner_leads=partners_leads.get(partner.id)
                ifpartner_leads:
                    partner_leads['leads'].append(lead_details)
                else:
                    partners_leads[partner.id]={'partner':partner,'leads':[lead_details]}

        forpartner_id,partner_leadsinpartners_leads.items():
            in_portal=False
            ifportal_group:
                forcontactin(partner.child_idsorpartner).filtered(lambdacontact:contact.user_ids):
                    in_portal=portal_group.idin[g.idforgincontact.user_ids[0].groups_id]

            local_context['partner_id']=partner_leads['partner']
            local_context['partner_leads']=partner_leads['leads']
            local_context['partner_in_portal']=in_portal
            template.with_context(local_context).send_mail(self.id)
            leads=self.env['crm.lead']
            forlead_datainpartner_leads['leads']:
                leads|=lead_data['lead_id']
            values={'partner_assigned_id':partner_id,'user_id':partner_leads['partner'].user_id.id}
            leads.with_context(mail_auto_subscribe_no_notify=1).write(values)
            self.env['crm.lead'].message_subscribe([partner_id])
        returnTrue

    defget_lead_portal_url(self,lead_id,type):
        action=type=='opportunity'and'action_portal_opportunities'or'action_portal_leads'
        action_ref=self.env.ref('website_crm_partner_assign.%s'%(action,),False)
        portal_link="%s/?db=%s#id=%s&action=%s&view_type=form"%(
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            self.env.cr.dbname,
            lead_id,
            action_refandaction_ref.idorFalse)
        returnportal_link

    defget_portal_url(self):
        portal_link="%s/?db=%s"%(self.env['ir.config_parameter'].sudo().get_param('web.base.url'),self.env.cr.dbname)
        returnportal_link

    forward_type=fields.Selection([
        ('single','asinglepartner:manualselectionofpartner'),
        ('assigned',"severalpartners:automaticassignment,usingGPScoordinatesandpartner'sgrades")
    ],'Forwardselectedleadsto',default=lambdaself:self.env.context.get('forward_type')or'single')
    partner_id=fields.Many2one('res.partner','ForwardLeadsTo')
    assignation_lines=fields.One2many('crm.lead.assignation','forward_id','PartnerAssignment')
    body=fields.Html('Contents',help='AutomaticallysanitizedHTMLcontents')


classCrmLeadAssignation(models.TransientModel):
    _name='crm.lead.assignation'
    _description='LeadAssignation'

    forward_id=fields.Many2one('crm.lead.forward.to.partner','PartnerAssignment')
    lead_id=fields.Many2one('crm.lead','Lead')
    lead_location=fields.Char('LeadLocation')
    partner_assigned_id=fields.Many2one('res.partner','AssignedPartner')
    partner_location=fields.Char('PartnerLocation')
    lead_link=fields.Char('LinktoLead')

    @api.onchange('lead_id')
    def_onchange_lead_id(self):
        lead=self.lead_id
        ifnotlead:
            self.lead_location=False
        else:
            lead_location=[]
            iflead.country_id:
                lead_location.append(lead.country_id.name)
            iflead.city:
                lead_location.append(lead.city)
            self.lead_location=",".join(lead_location)

    @api.onchange('partner_assigned_id')
    def_onchange_partner_assigned_id(self):
        partner=self.partner_assigned_id
        ifnotpartner:
            self.lead_location=False
        else:
            partner_location=[]
            ifpartner.country_id:
                partner_location.append(partner.country_id.name)
            ifpartner.city:
                partner_location.append(partner.city)
            self.partner_location=",".join(partner_location)
