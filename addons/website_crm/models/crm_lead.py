#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,SUPERUSER_ID


classLead(models.Model):
    _inherit='crm.lead'

    visitor_ids=fields.Many2many('website.visitor',string="WebVisitors")
    visitor_page_count=fields.Integer('#PageViews',compute="_compute_visitor_page_count")

    @api.depends('visitor_ids.page_ids')
    def_compute_visitor_page_count(self):
        mapped_data={}
        ifself.ids:
            self.flush(['visitor_ids'])
            sql="""SELECTl.idaslead_id,count(*)aspage_view_count
                        FROMcrm_leadl
                        JOINcrm_lead_website_visitor_rellvONl.id=lv.crm_lead_id
                        JOINwebsite_visitorvONv.id=lv.website_visitor_id
                        JOINwebsite_trackpONp.visitor_id=v.id
                        WHEREl.idin%sANDv.active=TRUE
                        GROUPBYl.id"""
            self.env.cr.execute(sql,(tuple(self.ids),))
            page_data=self.env.cr.dictfetchall()
            mapped_data={data['lead_id']:data['page_view_count']fordatainpage_data}
        forleadinself:
            lead.visitor_page_count=mapped_data.get(lead.id,0)

    defaction_redirect_to_page_views(self):
        visitors=self.visitor_ids
        action=self.env["ir.actions.actions"]._for_xml_id("website.website_visitor_page_action")
        action['domain']=[('visitor_id','in',visitors.ids)]
        #avoidgroupingifonlyfewrecords
        iflen(visitors.website_track_ids)>15andlen(visitors.website_track_ids.page_id)>1:
            action['context']={'search_default_group_by_page':'1'}
        returnaction

    def_merge_data(self,fields):
        merged_data=super(Lead,self)._merge_data(fields)
        #addallthevisitorsfromallleadtomerge
        merged_data['visitor_ids']=[(6,0,self.visitor_ids.ids)]
        returnmerged_data

    defwebsite_form_input_filter(self,request,values):
        values['medium_id']=values.get('medium_id')or\
                              self.default_get(['medium_id']).get('medium_id')or\
                              self.sudo().env.ref('utm.utm_medium_website').id
        values['team_id']=values.get('team_id')or\
                            request.website.crm_default_team_id.id
        values['user_id']=values.get('user_id')or\
                            request.website.crm_default_user_id.id
        ifvalues.get('team_id'):
            values['type']='lead'ifself.env['crm.team'].sudo().browse(values['team_id']).use_leadselse'opportunity'
        else:
            values['type']='lead'ifself.with_user(SUPERUSER_ID).env['res.users'].has_group('crm.group_use_lead')else'opportunity'

        returnvalues


classWebsite(models.Model):
    _inherit='website'

    def_get_crm_default_team_domain(self):
        ifnotself.env.user.has_group('crm.group_use_lead'):
            return[('use_opportunities','=',True)]
        return[('use_leads','=',True)]

    crm_default_team_id=fields.Many2one(
        'crm.team',string='DefaultSalesTeams',
        default=lambdaself:self.env['crm.team'].search([],limit=1),
        domain=lambdaself:self._get_crm_default_team_domain(),
        help='DefaultSalesTeamfornewleadscreatedthroughtheContactUsform.')
    crm_default_user_id=fields.Many2one(
        'res.users',string='DefaultSalesperson',domain=[('share','=',False)],
        help='DefaultsalespersonfornewleadscreatedthroughtheContactUsform.')
