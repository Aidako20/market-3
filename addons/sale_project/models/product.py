#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classProductTemplate(models.Model):
    _inherit='product.template'

    service_tracking=fields.Selection([
        ('no','Don\'tcreatetask'),
        ('task_global_project','Createataskinanexistingproject'),
        ('task_in_project','Createataskinsalesorder\'sproject'),
        ('project_only','Createanewprojectbutnotask')],
        string="ServiceTracking",default="no",
        help="OnSalesorderconfirmation,thisproductcangenerateaprojectand/ortask.\
        Fromthose,youcantracktheserviceyouareselling.\n\
        'Insaleorder\'sproject':Willusethesaleorder\'sconfiguredprojectifdefinedorfallbackto\
        creatinganewprojectbasedontheselectedtemplate.")
    project_id=fields.Many2one(
        'project.project','Project',company_dependent=True,
        domain="[('company_id','=',current_company_id)]",
        help='Selectabillableprojectonwhichtaskscanbecreated.Thissettingmustbesetforeachcompany.')
    project_template_id=fields.Many2one(
        'project.project','ProjectTemplate',company_dependent=True,copy=True,
        domain="[('company_id','=',current_company_id)]",
        help='Selectabillableprojecttobetheskeletonofthenewcreatedprojectwhensellingthecurrentproduct.Itsstagesandtaskswillbeduplicated.')

    @api.constrains('project_id','project_template_id')
    def_check_project_and_template(self):
        """NOTE'service_tracking'shouldbeindecoratorparametersbutsinceORMcheckconstraintstwice(oneaftersetting
            storedfields,oneaftersettingnonstoredfield),theerrorisraisedwhencompany-dependentfieldsarenotset.
            So,thisconstraintsdoescoverallcasesandinconsistentcanstillberecordeduntiltheORMchangeitsbehavior.
        """
        forproductinself:
            ifproduct.service_tracking=='no'and(product.project_idorproduct.project_template_id):
                raiseValidationError(_('Theproduct%sshouldnothaveaprojectnoraprojecttemplatesinceitwillnotgenerateproject.')%(product.name,))
            elifproduct.service_tracking=='task_global_project'andproduct.project_template_id:
                raiseValidationError(_('Theproduct%sshouldnothaveaprojecttemplatesinceitwillgenerateataskinaglobalproject.')%(product.name,))
            elifproduct.service_trackingin['task_in_project','project_only']andproduct.project_id:
                raiseValidationError(_('Theproduct%sshouldnothaveaglobalprojectsinceitwillgenerateaproject.')%(product.name,))

    @api.onchange('service_tracking')
    def_onchange_service_tracking(self):
        ifself.service_tracking=='no':
            self.project_id=False
            self.project_template_id=False
        elifself.service_tracking=='task_global_project':
            self.project_template_id=False
        elifself.service_trackingin['task_in_project','project_only']:
            self.project_id=False


classProductProduct(models.Model):
    _inherit='product.product'

    @api.onchange('service_tracking')
    def_onchange_service_tracking(self):
        ifself.service_tracking=='no':
            self.project_id=False
            self.project_template_id=False
        elifself.service_tracking=='task_global_project':
            self.project_template_id=False
        elifself.service_trackingin['task_in_project','project_only']:
            self.project_id=False
