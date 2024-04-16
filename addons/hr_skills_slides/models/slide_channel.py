#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classSlideChannelPartner(models.Model):
    _inherit='slide.channel.partner'

    def_recompute_completion(self):
        res=super(SlideChannelPartner,self)._recompute_completion()
        partner_has_completed={
            channel_partner.partner_id.id:channel_partner.channel_idforchannel_partnerinself
            ifchannel_partner.completed}
        employees=self.env['hr.employee'].sudo().search(
            [('user_id.partner_id','in',list(partner_has_completed.keys()))])

        ifemployees:
            HrResumeLine=self.env['hr.resume.line'].sudo()
            line_type=self.env.ref('hr_skills_slides.resume_type_training',raise_if_not_found=False)
            line_type_id=line_typeandline_type.id

            foremployeeinemployees:
                channel=partner_has_completed[employee.user_id.partner_id.id]

                already_added=HrResumeLine.search([
                    ("employee_id","in",employees.ids),
                    ("channel_id","=",channel.id),
                    ("line_type_id","=",line_type_id),
                    ("display_type","=","course")
                ])

                ifnotalready_added:
                    HrResumeLine.create({
                        'employee_id':employee.id,
                        'name':channel.name,
                        'date_start':fields.Date.today(),
                        'date_end':fields.Date.today(),
                        'description':channel.description,
                        'line_type_id':line_type_id,
                        'display_type':'course',
                        'channel_id':channel.id
                    })
        returnres
