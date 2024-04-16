flectra.define('web.SwitchCompanyMenu_tests',function(require){
"usestrict";

varSwitchCompanyMenu=require('web.SwitchCompanyMenu');
vartestUtils=require('web.test_utils');


asyncfunctioncreateSwitchCompanyMenu(params){
    params=params||{};
    vartarget=params.debug?document.body: $('#qunit-fixture');
    varmenu=newSwitchCompanyMenu();
    awaittestUtils.mock.addMockEnvironment(menu,params);
    awaitmenu.appendTo(target)
    returnmenu
}


asyncfunctioninitMockCompanyMenu(assert,params){
    varmenu=awaitcreateSwitchCompanyMenu({
        session:{
            ...params.session,
            setCompanies:function(mainCompanyId,companyIds){
                assert.equal(mainCompanyId,params.assertMainCompany[0],params.assertMainCompany[1]);
                assert.equal(_.intersection(companyIds,params.asserCompanies[0]).length,params.asserCompanies[0].length,params.asserCompanies[1]);
            },
        }
    })
    awaittestUtils.dom.click(menu.$('.dropdown-toggle')); //opencompanyswitcherdropdown
    returnmenu
}

asyncfunctiontestSwitchCompany(assert,params){
    assert.expect(2);
    varmenu=awaitinitMockCompanyMenu(assert,params);
    awaittestUtils.dom.click(menu.$(`div[data-company-id=${params.company}]div.log_into`));
    menu.destroy();
}

asyncfunctiontestToggleCompany(assert,params){
    assert.expect(2);
    varmenu=awaitinitMockCompanyMenu(assert,params);
    awaittestUtils.dom.click(menu.$(`div[data-company-id=${params.company}]div.toggle_company`));
    menu.destroy();
}

QUnit.module('widgets',{
    beforeEach:asyncfunction(){
        this.session_mock_multi={
            user_companies:{
                current_company:[1,"Company1"],
                allowed_companies:[[1,"Company1"],[2,"Company2"],[3,"Company3"]],
            },
            user_context:{allowed_company_ids:[1,3]},
        },
        this.session_mock_single={
            user_companies:{
                current_company:[1,"Company1"],
                allowed_companies:[[1,"Company1"],[2,"Company2"],[3,"Company3"]],
            },
            user_context:{allowed_company_ids:[1]},
        }
    },

},function(){

    QUnit.module('SwitchCompanyMenu',{},function(){

        QUnit.test("Companyswitcherbasicrendering",asyncfunction(assert){
            assert.expect(6);
            varmenu=awaitcreateSwitchCompanyMenu({session:this.session_mock_multi});
            assert.equal(menu.$('.company_label:contains(Company1)').length,1,"itshoulddisplayCompany1")
            assert.equal(menu.$('.company_label:contains(Company2)').length,1,"itshoulddisplayCompany2")
            assert.equal(menu.$('.company_label:contains(Company3)').length,1,"itshoulddisplayCompany3")

            assert.equal(menu.$('div[data-company-id=1].fa-check-square').length,1,"Company1shouldbechecked")
            assert.equal(menu.$('div[data-company-id=2].fa-square-o').length,1,"Company2shouldnotbechecked")
            assert.equal(menu.$('div[data-company-id=3].fa-check-square').length,1,"Company3shouldbechecked")
            menu.destroy();
        });
    });

    QUnit.module('SwitchCompanyMenu',{},function(){

        QUnit.test("Togglenewcompanyinmultiplecompanymode",asyncfunction(assert){
            /**
             *         [x]**Company1**         [x]**Company1**
             * toggle->[]Company2    ====>   [x]Company2
             *         [x]Company3             [x]Company3
             */
            awaittestToggleCompany(assert,{
                company:2,
                session:this.session_mock_multi,
                assertMainCompany:[1,"Maincompanyshouldnothavechanged"],
                asserCompanies:[[1,2,3],"Allcompaniesshouldbeactivated"],
            });
        });

        QUnit.test("Toggleactivecompanyinmutliplecompanymode",asyncfunction(assert){
            /**
             *         [x]**Company1**         [x]**Company1**
             *         []Company2    ====>   []Company2
             * toggle->[x]Company3             []Company3
             */
            awaittestToggleCompany(assert,{
                company:3,
                session:this.session_mock_multi,
                assertMainCompany:[1,"Maincompanyshouldnothavechanged"],
                asserCompanies:[[1],"Companies3shouldbeunactivated"],
            });
        });

        QUnit.test("Switchmaincompanyinmutliplecompanymode",asyncfunction(assert){
            /**
             *         [x]**Company1**         [x]Company1
             *         []Company2    ====>   []Company2
             * switch->[x]Company3             [x]**Company3**
             */
            awaittestSwitchCompany(assert,{
                company:3,
                session:this.session_mock_multi,
                assertMainCompany:[3,"MaincompanyshouldswitchtoCompany3"],
                asserCompanies:[[1,3],"Companies1and3shouldstillbeactive"],
            });
        });

        QUnit.test("Switchnewcompanyinmutliplecompanymode",asyncfunction(assert){
            /**
             *         [x]**Company1**         [x]Company1
             * switch->[]Company2    ====>   [x]**Company2**
             *         [x]Company3             [x]Company3
             */
            awaittestSwitchCompany(assert,{
                company:2,
                session:this.session_mock_multi,
                assertMainCompany:[2,"Company2shouldbecomethemaincompany"],
                asserCompanies:[[1,2,3],"Companies1and3shouldstillbeactive"],
            });
        });

        QUnit.test("Switchmaincompanyinsinglecompanymode",asyncfunction(assert){
            /**
             *         [x]**Company1**         []Company1
             *         []Company2    ====>   []Company2
             * switch->[]Company3             [x]**Company3**
             */
            awaittestSwitchCompany(assert,{
                company:3,
                session:this.session_mock_single,
                assertMainCompany:[3,"MaincompanyshouldswitchtoCompany3"],
                asserCompanies:[[3],"Companies1shouldnolongerbeactive"],
            });
        });

        QUnit.test("Togglenewcompanyinsinglecompanymode",asyncfunction(assert){
            /**
             *         [x]**Company1**         []**Company1**
             *         []Company2    ====>   []Company2
             * toggle->[]Company3             [x]Company3
             */
            awaittestToggleCompany(assert,{
                company:3,
                session:this.session_mock_single,
                assertMainCompany:[1,"Company1shouldstillbethemaincompany"],
                asserCompanies:[[1,3],"Company3shouldbeactivated"],
            });
        });
    });
});
});
