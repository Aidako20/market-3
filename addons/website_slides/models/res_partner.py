#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classResPartner(models.Model):
    _inherit='res.partner'

    slide_channel_ids=fields.Many2many(
        'slide.channel','slide_channel_partner','partner_id','channel_id',
        string='eLearningCourses',copy=False)
    slide_channel_count=fields.Integer('CourseCount',compute='_compute_slide_channel_count')
    slide_channel_company_count=fields.Integer('CompanyCourseCount',compute='_compute_slide_channel_company_count')

    @api.depends('is_company')
    def_compute_slide_channel_count(self):
        read_group_res=self.env['slide.channel.partner'].sudo().read_group(
            [('partner_id','in',self.ids)],
            ['partner_id'],'partner_id'
        )
        data=dict((res['partner_id'][0],res['partner_id_count'])forresinread_group_res)
        forpartnerinself:
            partner.slide_channel_count=data.get(partner.id,0)

    @api.depends('is_company','child_ids.slide_channel_count')
    def_compute_slide_channel_company_count(self):
        forpartnerinself:
            ifpartner.is_company:
                partner.slide_channel_company_count=self.env['slide.channel'].sudo().search_count(
                    [('partner_ids','in',partner.child_ids.ids)]
                )
            else:
                partner.slide_channel_company_count=0

    defaction_view_courses(self):
        action=self.env["ir.actions.actions"]._for_xml_id("website_slides.slide_channel_action_overview")
        action['name']=_('FollowedCourses')
        action['domain']=['|',('partner_ids','in',self.ids),('partner_ids','in',self.child_ids.ids)]
        returnaction
