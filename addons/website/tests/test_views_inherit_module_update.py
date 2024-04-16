#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportHttpCase,standalone,tagged


@tagged('website_nightly','-standard')
classTestWebsiteNightlyRunbot(HttpCase):
    deftest_01_website_nightly_runbot(self):
        """Thistestisjustheretoavoidrunbottoraiseanerroronthe
        ``website_nightly``build.Indeed,ifnotasingletestwiththistagis
        found,thebuildwillbeconsideredasfailed.
        InFlectra16.4arealtestisusingthistag.
        """


"""
Thistestensure`inherit_id`updateiscorrectlyreplicatedoncowviews.
Theviewreceivingthe`inherit_id`updateiseither:
1.inamoduleloadedbefore`website`.Inthatcase,`website`codeisnot
   loadedyet,sowestoretheupdatestoreplaythechangesonthecowviews
   once`website`moduleisloaded(see`_check()`).Thistestistestingthat
   part.
2.inamoduleloadedafter`website`.Inthatcase,the`inherit_id`updateis
   directlyreplicatedonthecowviews.Thatbehavioristestedwith
   `test_module_new_inherit_view_on_parent_already_forked`and
   `test_specific_view_module_update_inherit_change`in`website`module.
"""


@standalone('cow_views_inherit','website_standalone')
deftest_01_cow_views_inherit_on_module_update(env):
    #    A   B                       A   B
    #   /\                  =>          /\
    #  D  D'                            D  D'

    #1.Setuphierarchyascommentabove
    View=env['ir.ui.view']
    View.with_context(_force_unlink=True,active_test=False).search([('website_id','=',1)]).unlink()
    child_view=env.ref('portal.footer_language_selector')
    parent_view=env.ref('portal.portal_back_in_edit_mode')
    #RemoveanypossiblyexistingCOWview(anotherthemeetc)
    parent_view.with_context(_force_unlink=True,active_test=False)._get_specific_views().unlink()
    child_view.with_context(_force_unlink=True,active_test=False)._get_specific_views().unlink()
    #Change`inherit_id`sothemoduleupdatewillsetitbacktotheXMLvalue
    child_view.write({'inherit_id':parent_view.id,'arch':child_view.arch_db.replace('o_footer_copyright_name','text-center')})
    #TriggerCOWonview
    child_view.with_context(website_id=1).write({'name':'COWWebsite1'})
    child_cow_view=child_view._get_specific_views()

    #2.Ensuresetupisasexpected
    assertlen(child_cow_view.inherit_id)==1,"ShouldonlybetheXMLviewanditsCOWcounterpart."
    assertchild_cow_view.inherit_id==parent_view,"Ensuretestissetupasexpected."

    #3.Upgradethemodule
    portal_module=env['ir.module.module'].search([('name','=','portal')])
    portal_module.button_immediate_upgrade()
    env.reset()    #clearthesetofenvironments
    env=env()    #getanenvironmentthatreferstothenewregistry

    #4.Ensurecowviewalsogotitsinherit_idupdated
    expected_parent_view=env.ref('portal.frontend_layout') #XMLdata
    assertchild_view.inherit_id==expected_parent_view,"Genericviewsecuritycheck."
    assertchild_cow_view.inherit_id==expected_parent_view,"COWviewshouldalsohavereceivedthe`inherit_id`update."


@standalone('cow_views_inherit','website_standalone')
deftest_02_cow_views_inherit_on_module_update(env):
    #    A   B   B'                 A   B  B'
    #   /\                  =>           |  |
    #  D  D'                              D  D'

    #1.Setuphierarchyascommentabove
    View=env['ir.ui.view']
    View.with_context(_force_unlink=True,active_test=False).search([('website_id','=',1)]).unlink()
    view_D=env.ref('portal.my_account_link')
    view_A=env.ref('portal.message_thread')
    #Change`inherit_id`sothemoduleupdatewillsetitbacktotheXMLvalue
    view_D.write({'inherit_id':view_A.id,'arch_db':view_D.arch_db.replace('o_logout_divider','discussion')})
    #TriggerCOWonview
    view_B=env.ref('portal.user_dropdown') #XMLdata
    view_D.with_context(website_id=1).write({'name':'DWebsite1'})
    view_B.with_context(website_id=1).write({'name':'BWebsite1'})
    view_Dcow=view_D._get_specific_views()

    #2.Ensuresetupisasexpected
    view_Bcow=view_B._get_specific_views()
    assertview_Dcow.inherit_id==view_A,"Ensuretestissetupasexpected."
    assertlen(view_Bcow)==len(view_Dcow)==1,"Ensuretestissetupasexpected(2)."
    assertview_B!=view_Bcow,"Securitychecktoensure`_get_specific_views`returnwhatitshould."

    #3.Upgradethemodule
    portal_module=env['ir.module.module'].search([('name','=','portal')])
    portal_module.button_immediate_upgrade()
    env.reset()    #clearthesetofenvironments
    env=env()    #getanenvironmentthatreferstothenewregistry

    #4.Ensurecowviewalsogotitsinherit_idupdated
    assertview_D.inherit_id==view_B,"Genericviewsecuritycheck."
    assertview_Dcow.inherit_id==view_Bcow,"COWviewshouldalsohavereceivedthe`inherit_id`update."
