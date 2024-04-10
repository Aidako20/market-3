# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import _, api, fields, models
from flectra.exceptions import ValidationError


class ProductDocument(models.Model):
    _inherit = 'product.document'

    attached_on = fields.Selection(
        selection_add=[('inside', "Inside quote")],
        help="Allows you to share the document with your customers within a sale.\n"
             "Leave it empty if you don't want to share this document with sales customer.\n"
             "Quotation: the document will be sent to and accessible by customers at any time.\n"
             "e.g. this option can be useful to share Product description files.\n"
             "Confirmed order: the document will be sent to and accessible by customers.\n"
             "e.g. this option can be useful to share User Manual or digital content bought"
             " on ecommerce. \n"
             "Inside quote: The document will be included in the pdf of the quotation between the "
             "header pages and the quote table. ",
    )

    @api.constrains('attached_on', 'datas')
    def _check_attached_on_and_datas_compatibility(self):
        for doc in self:
            if doc.attached_on == 'inside' and not (doc.datas and doc.mimetype.endswith('pdf')):
                raise ValidationError(_("Only PDF documents can be attached inside a quote."))
