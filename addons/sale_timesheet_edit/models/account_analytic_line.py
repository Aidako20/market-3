#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


#TODO:[XBO]mergewithaccount.analytic.lineinthesale_timesheetmoduleinmaster.
classAccountAnalyticLine(models.Model):
    _inherit='account.analytic.line'

    is_so_line_edited=fields.Boolean()

    @api.depends('task_id.sale_line_id','project_id.sale_line_id','project_id.allow_billable','employee_id')
    def_compute_so_line(self):
        super(AccountAnalyticLine,self.filtered(lambdat:nott.is_so_line_edited))._compute_so_line()

    def_check_sale_line_in_project_map(self):
        #TODO:[XBO]removemeinmaster,nowweauthorizetomanuallyedittheso_line,thenthisso_linecanbedifferentoftheoneintask/project/map_entry
        #!!!Overrideofthemethodinsale_timesheet!!!
        return
