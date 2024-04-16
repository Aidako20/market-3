#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classCalendarEvent(models.Model):
    _inherit='calendar.event'

    @api.model
    defdefault_get(self,fields):
        ifself.env.context.get('default_opportunity_id'):
            self=self.with_context(
                default_res_model_id=self.env.ref('crm.model_crm_lead').id,
                default_res_id=self.env.context['default_opportunity_id']
            )
        defaults=super(CalendarEvent,self).default_get(fields)

        #syncres_model/res_idtoopportunityid(akacreatingmeetingfromleadchatter)
        if'opportunity_id'notindefaults:
            ifself._is_crm_lead(defaults,self.env.context):
                defaults['opportunity_id']=defaults.get('res_id',False)orself.env.context.get('default_res_id',False)

        returndefaults

    opportunity_id=fields.Many2one(
        'crm.lead','Opportunity',domain="[('type','=','opportunity')]",
        index=True,ondelete='setnull')

    def_compute_is_highlighted(self):
        super(CalendarEvent,self)._compute_is_highlighted()
        ifself.env.context.get('active_model')=='crm.lead':
            opportunity_id=self.env.context.get('active_id')
            foreventinself:
                ifevent.opportunity_id.id==opportunity_id:
                    event.is_highlighted=True

    @api.model_create_multi
    defcreate(self,vals):
        events=super(CalendarEvent,self).create(vals)
        foreventinevents:
            ifevent.opportunity_idandnotevent.activity_ids:
                event.opportunity_id.log_meeting(event.name,event.start,event.duration)
        returnevents

    def_is_crm_lead(self,defaults,ctx=None):
        """
            ThismethodchecksiftheconcernedmodelisaCRMlead.
            Theinformationisnotalwaysinthedefaultsvalues,
            thisiswhyitisnecessarytocheckthecontexttoo.
        """
        res_model=defaults.get('res_model',False)orctxandctx.get('default_res_model')
        res_model_id=defaults.get('res_model_id',False)orctxandctx.get('default_res_model_id')

        returnres_modelandres_model=='crm.lead'orres_model_idandself.env['ir.model'].sudo().browse(res_model_id).model=='crm.lead'
