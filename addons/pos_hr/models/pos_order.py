#-*-coding:utf-8-*-
fromflectraimportmodels,fields,api


classPosOrder(models.Model):
    _inherit="pos.order"

    employee_id=fields.Many2one('hr.employee',help="Personwhousesthecashregister.Itcanbeareliever,astudentoraninterimemployee.",states={'done':[('readonly',True)],'invoiced':[('readonly',True)]})
    cashier=fields.Char(string="Cashier",compute="_compute_cashier",store=True)

    @api.model
    def_order_fields(self,ui_order):
        order_fields=super(PosOrder,self)._order_fields(ui_order)
        order_fields['employee_id']=ui_order.get('employee_id')
        returnorder_fields

    @api.depends('employee_id','user_id')
    def_compute_cashier(self):
        fororderinself:
            iforder.employee_id:
                order.cashier=order.employee_id.name
            else:
                order.cashier=order.user_id.name

    def_export_for_ui(self,order):
        result=super(PosOrder,self)._export_for_ui(order)
        result.update({
            'employee_id':order.employee_id.id,
        })
        returnresult

    def_get_fields_for_draft_order(self):
        fields=super(PosOrder,self)._get_fields_for_draft_order()
        fields.append('employee_id')
        returnfields
