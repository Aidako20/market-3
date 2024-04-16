#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.account.models.chart_templateimportupdate_taxes_from_templates


defmigrate(cr,version):
    update_taxes_from_templates(cr,'l10n_lu.lu_2011_chart_1')
