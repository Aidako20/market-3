flectra.define('web.user_menu_tests',function(require){
"usestrict";

vartestUtils=require('web.test_utils');
varUserMenu=require('web.UserMenu');
varWidget=require('web.Widget');

QUnit.module('chrome',{},function(){
    QUnit.module('UserMenu');

    QUnit.test('basicrendering',asyncfunction(assert){
        assert.expect(3);

        varparent=newWidget();

        awaittestUtils.mock.addMockEnvironment(parent,{});
        varuserMenu=newUserMenu(parent);
        awaituserMenu.appendTo($('body'));

        assert.strictEqual($('.o_user_menu').length,1,
            "shouldhaveausermenuintheDOM");
        assert.hasClass(userMenu.$el,'o_user_menu',
            "usermenuinDOMshouldbefromusermenuwidgetinstantiation");
        assert.containsOnce(userMenu,'.dropdown-item[data-menu="shortcuts"]',
            "shouldhavea'Shortcuts'item");

        userMenu.destroy();
        parent.destroy();
    });
});

});
