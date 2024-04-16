#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classResCompany(models.Model):
    _inherit='res.company'

    @api.model
    def_default_project_time_mode_id(self):
        uom=self.env.ref('uom.product_uom_hour',raise_if_not_found=False)
        wtime=self.env.ref('uom.uom_categ_wtime')
        ifnotuom:
            uom=self.env['uom.uom'].search([('category_id','=',wtime.id),('uom_type','=','reference')],limit=1)
        ifnotuom:
            uom=self.env['uom.uom'].search([('category_id','=',wtime.id)],limit=1)
        returnuom

    @api.model
    def_default_timesheet_encode_uom_id(self):
        uom=self.env.ref('uom.product_uom_hour',raise_if_not_found=False)
        wtime=self.env.ref('uom.uom_categ_wtime')
        ifnotuom:
            uom=self.env['uom.uom'].search([('category_id','=',wtime.id),('uom_type','=','reference')],limit=1)
        ifnotuom:
            uom=self.env['uom.uom'].search([('category_id','=',wtime.id)],limit=1)
        returnuom
    
    project_time_mode_id=fields.Many2one('uom.uom',string='ProjectTimeUnit',
        default=_default_project_time_mode_id,
        help="Thiswillsettheunitofmeasureusedinprojectsandtasks.\n"
             "Ifyouusethetimesheetlinkedtoprojects,don't"
             "forgettosetuptherightunitofmeasureinyouremployees.")
    timesheet_encode_uom_id=fields.Many2one('uom.uom',string="TimesheetEncodingUnit",
        default=_default_timesheet_encode_uom_id,domain=lambdaself:[('category_id','=',self.env.ref('uom.uom_categ_wtime').id)],
        help="""Thiswillsettheunitofmeasureusedtoencodetimesheet.Thiswillsimplyprovidetools
        andwidgetstohelptheencoding.Allreportingwillstillbeexpressedinhours(defaultvalue).""")

    @api.model_create_multi
    defcreate(self,values):
        company=super(ResCompany,self).create(values)
        #usesudoastheusercouldhavetherighttocreateacompany
        #butnottocreateaproject.Ontheotherhand,whenthecompany
        #iscreated,itisnotintheallowed_company_idsontheenv
        company.sudo()._create_internal_project_task()
        returncompany

    def_create_internal_project_task(self):
        results=[]
        forcompanyinself:
            company=company.with_company(company)
            internal_project=company.env['project.project'].sudo().create({
                'name':_('Internal'),
                'allow_timesheets':True,
                'company_id':company.id,
            })

            company.env['project.task'].sudo().create([{
                'name':_('Training'),
                'project_id':internal_project.id,
                'company_id':company.id,
            },{
                'name':_('Meeting'),
                'project_id':internal_project.id,
                'company_id':company.id,
            }])
            results.append(internal_project)
        returnresults
