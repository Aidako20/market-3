#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPartner(models.Model):
    _name='res.partner'
    _inherit='res.partner'

    team_id=fields.Many2one('crm.team',string='SalesTeam')
    opportunity_ids=fields.One2many('crm.lead','partner_id',string='Opportunities',domain=[('type','=','opportunity')])
    meeting_ids=fields.Many2many('calendar.event','calendar_event_res_partner_rel','res_partner_id','calendar_event_id',string='Meetings',copy=False)
    opportunity_count=fields.Integer("Opportunity",compute='_compute_opportunity_count')
    meeting_count=fields.Integer("#Meetings",compute='_compute_meeting_count')

    @api.model
    defdefault_get(self,fields):
        rec=super(Partner,self).default_get(fields)
        active_model=self.env.context.get('active_model')
        ifactive_model=='crm.lead'andlen(self.env.context.get('active_ids',[]))<=1:
            lead=self.env[active_model].browse(self.env.context.get('active_id')).exists()
            iflead:
                rec.update(
                    phone=lead.phone,
                    mobile=lead.mobile,
                    function=lead.function,
                    title=lead.title.id,
                    website=lead.website,
                    street=lead.street,
                    street2=lead.street2,
                    city=lead.city,
                    state_id=lead.state_id.id,
                    country_id=lead.country_id.id,
                    zip=lead.zip,
                )
        returnrec

    def_compute_opportunity_count(self):
        #retrieveallchildrenpartnersandprefetch'parent_id'onthem
        all_partners=self.with_context(active_test=False).search([('id','child_of',self.ids)])
        all_partners.read(['parent_id'])

        opportunity_data=self.env['crm.lead'].read_group(
            domain=[('partner_id','in',all_partners.ids)],
            fields=['partner_id'],groupby=['partner_id']
        )

        self.opportunity_count=0
        forgroupinopportunity_data:
            partner=self.browse(group['partner_id'][0])
            whilepartner:
                ifpartnerinself:
                    partner.opportunity_count+=group['partner_id_count']
                partner=partner.parent_id

    def_compute_meeting_count(self):
        result=self._compute_meeting()
        forpinself:
            p.meeting_count=len(result.get(p.id,[]))

    def_compute_meeting(self):
        ifself.ids:
            all_partners=self.with_context(active_test=False).search([('id','child_of',self.ids)])

            event_id=self.env['calendar.event']._search([]) #ir.ruleswillbeapplied
            subquery_string,subquery_params=event_id.select()
            subquery=self.env.cr.mogrify(subquery_string,subquery_params).decode()

            self.env.cr.execute("""
                SELECTres_partner_id,calendar_event_id,count(1)
                  FROMcalendar_event_res_partner_rel
                 WHEREres_partner_idIN%sANDcalendar_event_idIN({})
              GROUPBYres_partner_id,calendar_event_id
            """.format(subquery),[tuple(all_partners.ids)])

            meeting_data=self.env.cr.fetchall()

            #Createadict{partner_id:event_ids}andfillwitheventslinkedtothepartner
            meetings={}
            forp_id,m_id,_inmeeting_data:
                meetings.setdefault(p_id,set()).add(m_id)

            #Addtheeventslinkedtothechildrenofthepartner
            forpinself.browse(meetings.keys()):
                partner=p
                whilepartner.parent_id:
                    partner=partner.parent_id
                    ifpartnerinself:
                        meetings[partner.id]=meetings.get(partner.id,set())|meetings[p.id]
            return{p_id:list(meetings[p_id])ifp_idinmeetingselse[]forp_idinself.ids}
        return{}


    defschedule_meeting(self):
        self.ensure_one()
        partner_ids=self.ids
        partner_ids.append(self.env.user.partner_id.id)
        action=self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context']={
            'default_partner_ids':partner_ids,
            'default_attendee_ids':[(0,0,{'partner_id':pid})forpidinpartner_ids],
        }
        action['domain']=['|',('id','in',self._compute_meeting()[self.id]),('partner_ids','in',self.ids)]
        returnaction

    defaction_view_opportunity(self):
        '''
        Thisfunctionreturnsanactionthatdisplaystheopportunitiesfrompartner.
        '''
        action=self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_opportunities')
        ifself.is_company:
            action['domain']=[('partner_id.commercial_partner_id.id','=',self.id)]
        else:
            action['domain']=[('partner_id.id','=',self.id)]
        returnaction
