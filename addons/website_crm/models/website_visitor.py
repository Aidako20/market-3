#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classWebsiteVisitor(models.Model):
    _inherit='website.visitor'

    lead_ids=fields.Many2many('crm.lead',string='Leads',groups="sales_team.group_sale_salesman")
    lead_count=fields.Integer('#Leads',compute="_compute_lead_count",groups="sales_team.group_sale_salesman")

    @api.depends('lead_ids')
    def_compute_lead_count(self):
        forvisitorinself:
            visitor.lead_count=len(visitor.lead_ids)

    @api.depends('partner_id.email_normalized','partner_id.mobile','lead_ids.email_normalized','lead_ids.mobile')
    def_compute_email_phone(self):
        super(WebsiteVisitor,self)._compute_email_phone()
        self.flush()

        left_visitors=self.filtered(lambdavisitor:notvisitor.emailornotvisitor.mobile)
        leads=left_visitors.mapped('lead_ids').sorted('create_date',reverse=True)
        visitor_to_lead_ids=dict((visitor.id,visitor.lead_ids.ids)forvisitorinleft_visitors)

        forvisitorinleft_visitors:
            visitor_leads=leads.filtered(lambdalead:lead.idinvisitor_to_lead_ids[visitor.id])
            ifnotvisitor.email:
                visitor.email=next((lead.email_normalizedforleadinvisitor_leadsiflead.email_normalized),False)
            ifnotvisitor.mobile:
                visitor.mobile=next((lead.mobileorlead.phoneforleadinvisitor_leadsiflead.mobileorlead.phone),False)

    def_check_for_message_composer(self):
        check=super(WebsiteVisitor,self)._check_for_message_composer()
        ifnotcheckandself.lead_ids:
            sorted_leads=self.lead_ids._sort_by_confidence_level(reverse=True)
            partners=sorted_leads.mapped('partner_id')
            ifnotpartners:
                main_lead=self.lead_ids[0]
                main_lead.handle_partner_assignment(create_missing=True)
                self.partner_id=main_lead.partner_id.id
            returnTrue
        returncheck

    def_prepare_message_composer_context(self):
        ifnotself.partner_idandself.lead_ids:
            sorted_leads=self.lead_ids._sort_by_confidence_level(reverse=True)
            lead_partners=sorted_leads.mapped('partner_id')
            partner=lead_partners[0]iflead_partnerselseFalse
            ifpartner:
                return{
                    'default_model':'crm.lead',
                    'default_res_id':sorted_leads[0].id,
                    'default_partner_ids':partner.ids,
                }
        returnsuper(WebsiteVisitor,self)._prepare_message_composer_context()
