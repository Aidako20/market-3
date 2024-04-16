#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classProject(models.Model):
    _inherit='project.project'

    def_get_not_billed_timesheets(self):
        """GetthetimesheetsnotinvoicedandtheSOLhasnotmanuallybeenedited
            FIXME:[XBO]thischangemustbedoneinthe_update_timesheets_sale_line_id
                ratherthanthismethodinmastertokeeptheinitialbehaviourofthismethod.
        """
        returnsuper(Project,self)._get_not_billed_timesheets()-self.mapped('timesheet_ids').filtered('is_so_line_edited')
