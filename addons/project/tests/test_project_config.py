#-*-coding:utf-8-*-

importlogging

from.test_project_baseimportTestProjectCommon

_logger=logging.getLogger(__name__)


classTestProjectConfig(TestProjectCommon):
    """Testmoduleconfigurationanditseffectsonprojects."""

    @classmethod
    defsetUpClass(cls):
        super(TestProjectConfig,cls).setUpClass()
        cls.Project=cls.env["project.project"]
        cls.Settings=cls.env["res.config.settings"]
        cls.features=(
            #Pairsofassociated(config_flag,project_flag)
            ("group_subtask_project","allow_subtasks"),
            ("group_project_recurring_tasks","allow_recurring_tasks"),
            ("group_project_rating","rating_active"),
            )

        #Startwithaknownvalueonfeatureflagstoensurevalidityoftests
        cls._set_feature_status(is_enabled=False)

    @classmethod
    def_set_feature_status(cls,is_enabled):
        """Setenabled/disabledstatusofalloptionalfeaturesinthe
        projectappconfigtois_enabled(boolean).
        """
        features_config=cls.Settings.create(
            {feature[0]:is_enabledforfeatureincls.features})
        features_config.execute()

    deftest_existing_projects_enable_features(self):
        """Checkthat*existing*projectshavefeaturesenabledwhen
        theuserenablestheminthemoduleconfiguration.
        """
        self._set_feature_status(is_enabled=True)
        forconfig_flag,project_flaginself.features:
            self.assertTrue(
                self.project_pigs[project_flag],
                "Existingprojectfailedtoadoptactivationof"
                f"{config_flag}/{project_flag}feature")

    deftest_new_projects_enable_features(self):
        """Checkthataftertheuserenablesfeaturesinthemodule
        configuration,*newlycreated*projectshavethosefeatures
        enabledaswell.
        """
        self._set_feature_status(is_enabled=True)
        project_cows=self.Project.create({
            "name":"Cows",
            "partner_id":self.partner_1.id})
        forconfig_flag,project_flaginself.features:
            self.assertTrue(
                project_cows[project_flag],
                f"Newlycreatedprojectfailedtoadoptactivationof"
                f"{config_flag}/{project_flag}feature")
