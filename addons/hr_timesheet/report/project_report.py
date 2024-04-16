#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classReportProjectTaskUser(models.Model):
    _inherit="report.project.task.user"

    hours_planned=fields.Float('PlannedHours',readonly=True)
    hours_effective=fields.Float('EffectiveHours',readonly=True)
    remaining_hours=fields.Float('RemainingHours',readonly=True)
    progress=fields.Float('Progress',group_operator='avg',readonly=True)

    def_select(self):
        returnsuper(ReportProjectTaskUser,self)._select()+""",
            t.progressasprogress,
            t.effective_hoursashours_effective,
            t.planned_hours-t.effective_hours-t.subtask_effective_hoursasremaining_hours,
            planned_hoursashours_planned"""

    def_group_by(self):
        returnsuper(ReportProjectTaskUser,self)._group_by()+""",
            remaining_hours,
            t.effective_hours,
            t.progress,
            planned_hours
            """
