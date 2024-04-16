fromflectra.addons.account.models.chart_templateimportupdate_taxes_from_templates

defmigrate(cr,version):
    #Addthenewtaxtagstothecreditnoterepartitionlines
    update_taxes_from_templates(cr,'l10n_it.l10n_it_chart_template_generic')
