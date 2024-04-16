#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,tools


classReportProjectTaskUser(models.Model):
    _name="report.project.task.user"
    _description="TasksAnalysis"
    _order='namedesc,project_id'
    _auto=False

    name=fields.Char(string='TaskTitle',readonly=True)
    user_id=fields.Many2one('res.users',string='AssignedTo',readonly=True)
    date_assign=fields.Datetime(string='AssignmentDate',readonly=True)
    date_end=fields.Datetime(string='EndingDate',readonly=True)
    date_deadline=fields.Date(string='Deadline',readonly=True)
    date_last_stage_update=fields.Datetime(string='LastStageUpdate',readonly=True)
    project_id=fields.Many2one('project.project',string='Project',readonly=True)
    working_days_close=fields.Float(string='#WorkingDaystoClose',
        digits=(16,2),readonly=True,group_operator="avg",
        help="NumberofWorkingDaystoclosethetask")
    working_days_open=fields.Float(string='#WorkingDaystoAssign',
        digits=(16,2),readonly=True,group_operator="avg",
        help="NumberofWorkingDaystoOpenthetask")
    delay_endings_days=fields.Float(string='#DaystoDeadline',digits=(16,2),readonly=True)
    nbr=fields.Integer('#ofTasks',readonly=True) #TDEFIXMEmaster:renameintonbr_tasks
    priority=fields.Selection([
        ('0','Low'),
        ('1','Normal'),
        ('2','High')
        ],readonly=True,string="Priority")
    state=fields.Selection([
            ('normal','InProgress'),
            ('blocked','Blocked'),
            ('done','Readyfornextstage')
        ],string='KanbanState',readonly=True)
    company_id=fields.Many2one('res.company',string='Company',readonly=True)
    partner_id=fields.Many2one('res.partner',string='Customer',readonly=True)
    stage_id=fields.Many2one('project.task.type',string='Stage',readonly=True)

    def_select(self):
        select_str="""
             SELECT
                    (select1)ASnbr,
                    t.idasid,
                    t.date_assignasdate_assign,
                    t.date_endasdate_end,
                    t.date_last_stage_updateasdate_last_stage_update,
                    t.date_deadlineasdate_deadline,
                    t.user_id,
                    t.project_id,
                    t.priority,
                    t.nameasname,
                    t.company_id,
                    t.partner_id,
                    t.stage_idasstage_id,
                    t.kanban_stateasstate,
                    t.working_days_closeasworking_days_close,
                    t.working_days_open asworking_days_open,
                    (extract('epoch'from(t.date_deadline-(now()attimezone'UTC'))))/(3600*24) asdelay_endings_days
        """
        returnselect_str

    def_group_by(self):
        group_by_str="""
                GROUPBY
                    t.id,
                    t.create_date,
                    t.write_date,
                    t.date_assign,
                    t.date_end,
                    t.date_deadline,
                    t.date_last_stage_update,
                    t.user_id,
                    t.project_id,
                    t.priority,
                    t.name,
                    t.company_id,
                    t.partner_id,
                    t.stage_id
        """
        returngroup_by_str

    definit(self):
        tools.drop_view_if_exists(self._cr,self._table)
        self._cr.execute("""
            CREATEview%sas
              %s
              FROMproject_taskt
                WHEREt.active='true'
                ANDt.project_idISNOTNULL
                %s
        """%(self._table,self._select(),self._group_by()))
