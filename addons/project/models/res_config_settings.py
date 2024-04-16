#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    module_project_forecast=fields.Boolean(string="Planning")
    module_hr_timesheet=fields.Boolean(string="TaskLogs")
    group_subtask_project=fields.Boolean("Sub-tasks",implied_group="project.group_subtask_project")
    group_project_rating=fields.Boolean("CustomerRatings",implied_group='project.group_project_rating')
    group_project_recurring_tasks=fields.Boolean("RecurringTasks",implied_group="project.group_project_recurring_tasks")

    defset_values(self):

        #Ensurethatsettingsonexistingprojectsmatchtheabovefields
        projects=self.env["project.project"].search([])
        features=(
            #Pairsofassociated(config_flag,project_flag)
            ("group_subtask_project","allow_subtasks"),
            ("group_project_rating","rating_active"),
            ("group_project_recurring_tasks","allow_recurring_tasks"),
            )
        for(config_flag,project_flag)infeatures:
            config_flag_global="project."+config_flag
            config_feature_enabled=self[config_flag]
            if(self.user_has_groups(config_flag_global)
                    isnotconfig_feature_enabled):
                projects[project_flag]=config_feature_enabled

        super(ResConfigSettings,self).set_values()
