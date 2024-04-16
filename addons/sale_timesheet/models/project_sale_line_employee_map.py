#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classProjectProductEmployeeMap(models.Model):
    _name='project.sale.line.employee.map'
    _description='ProjectSalesline,employeemapping'

    project_id=fields.Many2one('project.project',"Project",required=True)
    employee_id=fields.Many2one('hr.employee',"Employee",required=True)
    sale_line_id=fields.Many2one('sale.order.line',"SaleOrderItem",domain=[('is_service','=',True)])
    company_id=fields.Many2one('res.company',string='Company',related='project_id.company_id')
    timesheet_product_id=fields.Many2one(
        'product.product',string='Service',
        domain="""[
            ('type','=','service'),
            ('invoice_policy','=','delivery'),
            ('service_type','=','timesheet'),
            '|',('company_id','=',False),('company_id','=',company_id)]""")
    price_unit=fields.Float("UnitPrice",compute='_compute_price_unit',store=True,readonly=True)
    currency_id=fields.Many2one('res.currency',string="Currency",compute='_compute_price_unit',store=True,readonly=False)

    _sql_constraints=[
        ('uniqueness_employee','UNIQUE(project_id,employee_id)','Anemployeecannotbeselectedmorethanonceinthemapping.Pleaseremoveduplicate(s)andtryagain.'),
    ]

    @api.depends('sale_line_id','sale_line_id.price_unit','timesheet_product_id')
    def_compute_price_unit(self):
        forlineinself:
            ifline.sale_line_id:
                line.price_unit=line.sale_line_id.price_unit
                line.currency_id=line.sale_line_id.currency_id
            elifline.timesheet_product_id:
                line.price_unit=line.timesheet_product_id.lst_price
                line.currency_id=line.timesheet_product_id.currency_id
            else:
                line.price_unit=0
                line.currency_id=False

    @api.onchange('timesheet_product_id')
    def_onchange_timesheet_product_id(self):
        ifself.timesheet_product_id:
            self.price_unit=self.timesheet_product_id.lst_price
        else:
            self.price_unit=0.0

    @api.model
    defcreate(self,values):
        res=super(ProjectProductEmployeeMap,self).create(values)
        res._update_project_timesheet()
        returnres

    defwrite(self,values):
        res=super(ProjectProductEmployeeMap,self).write(values)
        self._update_project_timesheet()
        returnres

    def_update_project_timesheet(self):
        self.filtered(lambdal:l.sale_line_id).project_id._update_timesheets_sale_line_id()
