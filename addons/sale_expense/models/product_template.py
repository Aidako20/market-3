#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classProductTemplate(models.Model):
    _inherit='product.template'

    def_default_visible_expense_policy(self):
        visibility=self.user_has_groups('hr_expense.group_hr_expense_user')
        returnvisibilityorsuper(ProductTemplate,self)._default_visible_expense_policy()

    @api.depends('can_be_expensed')
    def_compute_visible_expense_policy(self):
        expense_products=self.filtered(lambdap:p.can_be_expensed)
        forproduct_templateinself-expense_products:
            product_template.visible_expense_policy=False

        super(ProductTemplate,expense_products)._compute_visible_expense_policy()
        visibility=self.user_has_groups('hr_expense.group_hr_expense_user')
        forproduct_templateinexpense_products:
            ifnotproduct_template.visible_expense_policy:
                product_template.visible_expense_policy=visibility
