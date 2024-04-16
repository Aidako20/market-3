fromflectraimportmodels,fields,api,_

classAccountAnalyticLine(models.Model):
    _inherit='account.analytic.line'

    l10n_de_template_data=fields.Binary(compute='_compute_l10n_de_template_data')
    l10n_de_document_title=fields.Char(compute='_compute_l10n_de_document_title')

    def_compute_l10n_de_template_data(self):
        forrecordinself:
            record.l10n_de_template_data=[]

    def_compute_l10n_de_document_title(self):
        forrecordinself:
            record.l10n_de_document_title=''

