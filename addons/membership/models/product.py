#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classProduct(models.Model):
    _inherit='product.template'

    membership=fields.Boolean(help='Checkiftheproductiseligibleformembership.')
    membership_date_from=fields.Date(string='MembershipStartDate',
        help='Datefromwhichmembershipbecomesactive.')
    membership_date_to=fields.Date(string='MembershipEndDate',
        help='Dateuntilwhichmembershipremainsactive.')

    _sql_constraints=[
        ('membership_date_greater','check(membership_date_to>=membership_date_from)','Error!EndingDatecannotbesetbeforeBeginningDate.')
    ]

    @api.model
    deffields_view_get(self,view_id=None,view_type='form',toolbar=False,submenu=False):
        ifself._context.get('product')=='membership_product':
            ifview_type=='form':
                view_id=self.env.ref('membership.membership_products_form').id
            else:
                view_id=self.env.ref('membership.membership_products_tree').id
        returnsuper(Product,self).fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)
