#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classCompany(models.Model):
    _inherit='res.company'

    manufacturing_lead=fields.Float(
        'ManufacturingLeadTime',default=0.0,required=True,
        help="Securitydaysforeachmanufacturingoperation.")

    def_create_unbuild_sequence(self):
        unbuild_vals=[]
        forcompanyinself:
            unbuild_vals.append({
                'name':'Unbuild',
                'code':'mrp.unbuild',
                'company_id':company.id,
                'prefix':'UB/',
                'padding':5,
                'number_next':1,
                'number_increment':1
            })
        ifunbuild_vals:
            self.env['ir.sequence'].create(unbuild_vals)

    @api.model
    defcreate_missing_unbuild_sequences(self):
        company_ids =self.env['res.company'].search([])
        company_has_unbuild_seq=self.env['ir.sequence'].search([('code','=','mrp.unbuild')]).mapped('company_id')
        company_todo_sequence=company_ids-company_has_unbuild_seq
        company_todo_sequence._create_unbuild_sequence()

    def_create_per_company_sequences(self):
        super(Company,self)._create_per_company_sequences()
        self._create_unbuild_sequence()
