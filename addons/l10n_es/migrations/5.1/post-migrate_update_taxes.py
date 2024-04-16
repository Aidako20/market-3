#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.account.models.chart_templateimportupdate_taxes_from_templates


defmigrate(cr,version):
    update_taxes_from_templates(cr,'l10n_es.account_chart_template_common')
