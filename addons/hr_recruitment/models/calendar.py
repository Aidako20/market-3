#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classCalendarEvent(models.Model):
    """ModelforCalendarEvent"""
    _inherit='calendar.event'

    @api.model
    defdefault_get(self,fields):
        ifself.env.context.get('default_applicant_id'):
            self=self.with_context(
                default_res_model='hr.applicant',#res_modelseemstobelostwithoutthis
                default_res_model_id=self.env.ref('hr_recruitment.model_hr_applicant').id,
                default_res_id=self.env.context['default_applicant_id']
            )

        defaults=super(CalendarEvent,self).default_get(fields)

        #syncres_model/res_idtoopportunityid(akacreatingmeetingfromleadchatter)
        if'applicant_id'notindefaults:
            res_model=defaults.get('res_model',False)orself.env.context.get('default_res_model')
            res_model_id=defaults.get('res_model_id',False)orself.env.context.get('default_res_model_id')
            if(res_modelandres_model=='hr.applicant')or(res_model_idandself.env['ir.model'].sudo().browse(res_model_id).model=='hr.applicant'):
                defaults['applicant_id']=defaults.get('res_id',False)orself.env.context.get('default_res_id',False)

        returndefaults

    def_compute_is_highlighted(self):
        super(CalendarEvent,self)._compute_is_highlighted()
        applicant_id=self.env.context.get('active_id')
        ifself.env.context.get('active_model')=='hr.applicant'andapplicant_id:
            foreventinself:
                ifevent.applicant_id.id==applicant_id:
                    event.is_highlighted=True

    applicant_id=fields.Many2one('hr.applicant',string="Applicant",index=True,ondelete='setnull')
