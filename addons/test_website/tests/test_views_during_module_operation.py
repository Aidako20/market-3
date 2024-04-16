#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website.toolsimportMockRequest
fromflectra.testsimportstandalone


@standalone('cow_views','website_standalone')
deftest_01_cow_views_unlink_on_module_update(env):
    """EnsureCOWviewsarecorrectlyremovedduringmoduleupdate.
    Notremovingtheviewcouldleadtotraceback:
    -HavingaviewA
    -HavingaviewBthatinheritsfromaviewC
    -ViewBt-callviewA
    -COWviewB
    -DeleteviewAandBfrommoduledatasandupdateit
    -RenderingviewCwillcrashsinceitwillrenderchildviewBthat
      t-callunexistingviewA
    """

    View=env['ir.ui.view']
    Imd=env['ir.model.data']

    update_module_base_view=env.ref('test_website.update_module_base_view')
    update_module_view_to_be_t_called=View.create({
        'name':'Viewtobet-called',
        'type':'qweb',
        'arch':'<div>Iwillbet-called</div>',
        'key':'test_website.update_module_view_to_be_t_called',
    })
    update_module_child_view=View.create({
        'name':'ChildView',
        'mode':'extension',
        'inherit_id':update_module_base_view.id,
        'arch':'''
            <divposition="inside">
                <tt-call="test_website.update_module_view_to_be_t_called"/>
            </div>
        ''',
        'key':'test_website.update_module_child_view',
    })

    #CreateIMDsowhenupdatingthemoduletheviewswillberemoved(notfoundinfile)
    Imd.create({
        'module':'test_website',
        'name':'update_module_view_to_be_t_called',
        'model':'ir.ui.view',
        'res_id':update_module_view_to_be_t_called.id,
    })
    Imd.create({
        'module':'test_website',
        'name':'update_module_child_view',
        'model':'ir.ui.view',
        'res_id':update_module_child_view.id,
    })

    #TriggerCOWonchildview
    update_module_child_view.with_context(website_id=1).write({'name':'ChildView(W1)'})

    #Ensureviewsarecorrectlysetup
    msg="View'%s'doesnotexist!"
    assertView.search_count([
        ('type','=','qweb'),
        ('key','=',update_module_child_view.key)
    ])==2,msg%update_module_child_view.key
    assertbool(env.ref(update_module_view_to_be_t_called.key)),\
        msg%update_module_view_to_be_t_called.key
    assertbool(env.ref(update_module_base_view.key)),msg%update_module_base_view.key

    #Upgradethemodule
    test_website_module=env['ir.module.module'].search([('name','=','test_website')])
    test_website_module.button_immediate_upgrade()
    env.reset()    #clearthesetofenvironments
    env=env()    #getanenvironmentthatreferstothenewregistry

    #Ensuregenericviewsgotremoved
    view=env.ref('test_website.update_module_view_to_be_t_called',raise_if_not_found=False)
    assertnotview,"Genericviewdidnotgetremoved!"

    #EnsurespecificCOWviewsgotremoved
    assertnotenv['ir.ui.view'].search_count([
        ('type','=','qweb'),
        ('key','=','test_website.update_module_child_view'),
    ]),"SpecificCOWviewsdidnotgetremoved!"


@standalone('theme_views','website_standalone')
deftest_02_copy_ids_views_unlink_on_module_update(env):
    """Ensurecopy_idsviewsarecorrectlyremovedduringmoduleupdate.
    -Havinganir.ui.viewAinthecodebase,eg`website.layout`
    -Havingatheme.ir.ui.viewBinatheme,inheritingir.ui.viewA
    -Removingthetheme.ir.ui.viewBfromtheXMLfileandthenupdatingthe
      themeforaparticularwebsiteshould:
      1.Removethetheme.ir.ui.viewrecord,whichistherecordpointedbythe
         ir.model.data
         ->ThisisdonethroughtheregularFlectrabehaviorrelatedtothe
            ir.model.dataandXMLfilecheckonupgrade.
      2.Removethetheme.ir.ui.view'scopy_ids(sortoftheCOWviews)
         ->Notworkingfornow
      3.(notimpactotherwebsiteusingthistheme,seebelow)
         ->Thisisdonethroughflectra/flectra@96ef4885a79butdidnotcomewith
            tests

      Point2.wasnotworking,thistestaimstoensureitwillnow.
      Note:Thiscan'tbedonethrougha`ondelete=cascade`asthiswould
            impactotherwebsiteswhenmodifyingaspecificwebsite.Thiswould
            beagainstthemulti-websiterule:
            "Whatisdoneonawebsiteshouldnotalterotherwebsites."

            Regardingtheflowdescribedabove,ifathememodulewasupdated
            throughthecommandline(orviatheUI,butthisisnotpossiblein
            standardasthememodulesarehiddenfromtheApps),itshould
            updateeverywebsiteusingthistheme.
    """
    View=env['ir.ui.view']
    ThemeView=env['theme.ir.ui.view']
    Imd=env['ir.model.data']

    website_1=env['website'].browse(1)
    website_2=env['website'].browse(2)
    theme_default=env.ref('base.module_theme_default')

    #Installtheme_defaultonwebsite1andwebsite2
    (website_1+website_2).theme_id=theme_default
    env['ir.module.module'].with_context(load_all_views=True)._theme_load(website_1)
    env['ir.module.module'].with_context(load_all_views=True)._theme_load(website_2)

    key='theme_default.theme_child_view'
    domain=[
        ('type','=','qweb'),
        ('key','=',key),
    ]

    def_simulate_xml_view():
        #Simulateatheme.ir.ui.viewinsidetheme_defaultXMLfiles
        base_view=env.ref('test_website.update_module_base_view')
        theme_child_view=ThemeView.create({
            'name':'ThemeChildView',
            'mode':'extension',
            'inherit_id':f'{base_view._name},{base_view.id}',
            'arch':'''
                <divposition="inside">
                    <p>,andIaminheritedbyatheme.ir.ui.view</p>
                </div>
            ''',
            'key':key,
        })
        #CreateIMDsowhenupdatingthemoduletheviewswillberemoved(notfoundinfile)
        Imd.create({
            'module':'theme_default',
            'name':'theme_child_view',
            'model':'theme.ir.ui.view',
            'res_id':theme_child_view.id,
        })
        #Simulatethetheme.ir.ui.viewbeinginstalledonwebsite1and2
        View.create([
            theme_child_view._convert_to_base_model(website_1),
            theme_child_view._convert_to_base_model(website_2),
        ])

        #Ensureviewsarecorrectlysetup:thetheme.ir.ui.viewshouldhavebeen
        #copiedtoanir.ui.viewforwebsite1
        view_website_1,view_website_2=View.search(domain+[
            ('theme_template_id','=',theme_child_view.id),
            ('website_id','in',(website_1+website_2).ids),
        ])
        assert(
            set((view_website_1+view_website_2)).issubset(theme_child_view.copy_ids)
            andview_website_1.website_id==website_1
            andview_website_2.website_id==website_2
        ),"ThemeViewshouldhavebeencopiedtothewebsite."

        returnview_website_1,view_website_2,theme_child_view

    ##########################################
    #CASE1:genericupdate(-u,migration)#
    ##########################################

    view_website_1,view_website_2,theme_child_view=_simulate_xml_view()

    #Upgradethemodule
    theme_default.button_immediate_upgrade()
    env.reset() #clearthesetofenvironments
    env=env() #getanenvironmentthatreferstothenewregistry

    #Ensurethetheme.ir.ui.viewgotremoved(sincethereisanIMDbutnot
    #presentinXMLfiles)
    view=env.ref('theme_default.theme_child_view',False)
    assertnotview,"Themeviewshouldhavebeenremovedduringmoduleupdate."
    assertnottheme_child_view.exists(),\
        "Themeviewshouldhavebeenremovedduringmoduleupdate.(2)"

    #Ensurecopy_idsviewgotremoved(andisnotaleftoverorphan)
    assertnotView.search(domain),"copy_idsviewsdidnotgetremoved!"
    assertnot(view_website_1.exists()orview_website_2.exists()),\
        "copy_idsviewsdidnotgetremoved!(2)"

    #####################################################
    #CASE2:specificupdate(websitethemeselection)#
    #####################################################

    view_website_1,view_website_2,theme_child_view=_simulate_xml_view()

    #Upgradethemodule
    withMockRequest(env,website=website_1):
        theme_default.button_immediate_upgrade()
    env.reset() #clearthesetofenvironments
    env=env() #getanenvironmentthatreferstothenewregistry

    #Ensurethetheme.ir.ui.viewgotremoved(sincethereisanIMDbutnot
    #presentinXMLfiles)
    view=env.ref('theme_default.theme_child_view',False)
    assertnotview,"Themeviewshouldhavebeenremovedduringmoduleupdate."
    assertnottheme_child_view.exists(),\
        "Themeviewshouldhavebeenremovedduringmoduleupdate.(2)"

    #Ensureonlywebsite_1copy_idsgotremoved,website_2shouldbeuntouched
    assertnotview_website_1.exists()andview_website_2.exists(),\
        "Onlywebsite_1copyshouldberemoved(2)"
