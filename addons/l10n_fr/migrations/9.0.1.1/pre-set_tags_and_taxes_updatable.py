fromopenerp.modules.registryimportRegistryManager

defmigrate(cr,version):
    registry=RegistryManager.get(cr.dbname)
    fromopenerp.addons.account.models.chart_templateimportmigrate_set_tags_and_taxes_updatable
    migrate_set_tags_and_taxes_updatable(cr,registry,'l10n_fr')

