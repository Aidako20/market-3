#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.account.models.chart_templateimportupdate_taxes_from_templates


defmigrate(cr,version):
    update_taxes_from_templates(cr,'l10n_de_skr04.l10n_chart_de_skr04')
