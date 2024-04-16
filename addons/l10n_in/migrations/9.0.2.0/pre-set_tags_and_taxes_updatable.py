#-*-coding:utf-8-*-

importflectra

defmigrate(cr,version):
    registry=flectra.registry(cr.dbname)
    fromflectra.addons.account.models.chart_templateimportmigrate_set_tags_and_taxes_updatable
    migrate_set_tags_and_taxes_updatable(cr,registry,'l10n_in')
