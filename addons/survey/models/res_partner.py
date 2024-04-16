#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResPartner(models.Model):
    _inherit='res.partner'

    certifications_count=fields.Integer('CertificationsCount',compute='_compute_certifications_count')
    certifications_company_count=fields.Integer('CompanyCertificationsCount',compute='_compute_certifications_company_count')

    @api.depends('is_company')
    def_compute_certifications_count(self):
        read_group_res=self.env['survey.user_input'].sudo().read_group(
            [('partner_id','in',self.ids),('scoring_success','=',True)],
            ['partner_id'],'partner_id'
        )
        data=dict((res['partner_id'][0],res['partner_id_count'])forresinread_group_res)
        forpartnerinself:
            partner.certifications_count=data.get(partner.id,0)

    @api.depends('is_company','child_ids.certifications_count')
    def_compute_certifications_company_count(self):
        self.certifications_company_count=sum(child.certifications_countforchildinself.child_ids)

    defaction_view_certifications(self):
        action=self.env["ir.actions.actions"]._for_xml_id("survey.res_partner_action_certifications")
        action['view_mode']='tree'
        action['domain']=['|',('partner_id','in',self.ids),('partner_id','in',self.child_ids.ids)]

        returnaction
