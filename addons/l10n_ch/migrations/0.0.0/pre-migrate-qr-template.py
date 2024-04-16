#-*-coding:utf-8-*-


defmigrate(cr,version):
    """From12.0,tosaas-13.3,l10n_ch_swissqr_template
    usedtoinheritfromanothertemplate.Thisisn'tthecase
    anymoresincehttps://github.com/flectra/flectra/commit/719f087b1b5be5f1f276a0f87670830d073f6ef4
    (madein12.0,andforward-ported).Themodulewillnotbeupdatableifwe
    don'tmanuallycleaninherit_id.
    """
    cr.execute("""
        updateir_ui_viewv
        setinherit_id=NULL,mode='primary'
        fromir_model_datamdata
        where
        v.id=mdata.res_id
        andmdata.model='ir.ui.view'
        andmdata.name='l10n_ch_swissqr_template'
        andmdata.module='l10n_ch';
    """)