#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classRecurringPlan(models.Model):
    _name="crm.recurring.plan"
    _description="CRMRecurringrevenueplans"
    _order="sequence"

    name=fields.Char('PlanName',required=True,translate=True)
    number_of_months=fields.Integer('#Months',required=True)
    active=fields.Boolean('Active',default=True)
    sequence=fields.Integer('Sequence',default=10)

    _sql_constraints=[
        ('check_number_of_months','CHECK(number_of_months>=0)','Thenumberofmonthcan\'tbenegative.'),
    ]
