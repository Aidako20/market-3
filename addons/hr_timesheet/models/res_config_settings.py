#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    module_project_timesheet_synchro=fields.Boolean("AwesomeTimesheet",
        compute="_compute_timesheet_modules",store=True,readonly=False)
    module_project_timesheet_holidays=fields.Boolean("RecordTimeOff",
        compute="_compute_timesheet_modules",store=True,readonly=False)
    project_time_mode_id=fields.Many2one(
        'uom.uom',related='company_id.project_time_mode_id',string='ProjectTimeUnit',readonly=False,
        help="Thiswillsettheunitofmeasureusedinprojectsandtasks.\n"
             "Ifyouusethetimesheetlinkedtoprojects,don't"
             "forgettosetuptherightunitofmeasureinyouremployees.")
    timesheet_encode_uom_id=fields.Many2one('uom.uom',string="EncodingUnit",
        related='company_id.timesheet_encode_uom_id',readonly=False,
        help="""Thiswillsettheunitofmeasureusedtoencodetimesheet.Thiswillsimplyprovidetools
        andwidgetstohelptheencoding.Allreportingwillstillbeexpressedinhours(defaultvalue).""")
    timesheet_min_duration=fields.Integer('Minimalduration',default=15,config_parameter='hr_timesheet.timesheet_min_duration')
    timesheet_rounding=fields.Integer('Roundingup',default=15,config_parameter='hr_timesheet.timesheet_rounding')
    is_encode_uom_days=fields.Boolean(compute='_compute_is_encode_uom_days')

    @api.depends('timesheet_encode_uom_id')
    def_compute_is_encode_uom_days(self):
        product_uom_day=self.env.ref('uom.product_uom_day')
        forsettingsinself:
            settings.is_encode_uom_days=settings.timesheet_encode_uom_id==product_uom_day

    @api.depends('module_hr_timesheet')
    def_compute_timesheet_modules(self):
        self.filtered(lambdaconfig:notconfig.module_hr_timesheet).update({
            'module_project_timesheet_synchro':False,
            'module_project_timesheet_holidays':False,
        })
