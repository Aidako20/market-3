#-*-coding:utf-8-*-

fromflectraimportfields,models


classProductTemplate(models.Model):
    """ProductTemplateinheritancetoaddanoptionalemail.templatetoa
    product.template.Whenvalidatinganinvoice,anemailwillbesendtothe
    customerbasedonthistemplate.Thecustomerwillreceiveanemailforeach
    productlinkedtoanemailtemplate."""
    _inherit="product.template"

    email_template_id=fields.Many2one('mail.template',string='ProductEmailTemplate',
        help='Whenvalidatinganinvoice,anemailwillbesenttothecustomer'
        'basedonthistemplate.Thecustomerwillreceiveanemailforeach'
        'productlinkedtoanemailtemplate.')
