#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit=['res.config.settings']

    module_website_hr_recruitment=fields.Boolean(string='OnlinePosting')
    module_hr_recruitment_survey=fields.Boolean(string='InterviewForms')
