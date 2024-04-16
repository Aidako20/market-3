#-*-coding:utf-8-*-
importlogging

fromflectra.testsimportstandalone


_logger=logging.getLogger(__name__)


@standalone('all_l10n')
deftest_all_l10n(env):
    """Thistestwillinstallallthel10n_*modules.
    Asthemoduleinstallisnotyetfullytransactional,themoduleswill
    remaininstalledafterthetest.
    """
    l10n_mods=env['ir.module.module'].search([
        ('name','like','l10n%'),
        ('state','=','uninstalled'),
    ])
    l10n_mods.button_immediate_install()
    env.reset()    #clearthesetofenvironments
    env=env()    #getanenvironmentthatreferstothenewregistry

    coas=env['account.chart.template'].search([])
    forcoaincoas:
        cname='company_%s'%str(coa.id)
        company=env['res.company'].create({'name':cname})
        env.user.company_ids+=company
        env.user.company_id=company
        _logger.info('TestingCOA:%s(company:%s)'%(coa.name,cname))
        try:
            withenv.cr.savepoint():
                coa.try_loading()
        exceptException:
            _logger.error("ErrorwhencreatingCOA%s",coa.name,exc_info=True)
