flectra.define('web.keyboard_navigation_mixin_tests',function(require){
"usestrict";

varKeyboardNavigationMixin=require('web.KeyboardNavigationMixin');
vartestUtils=require('web.test_utils');
varWidget=require('web.Widget');

QUnit.module('KeyboardNavigationMixin',function(){
    QUnit.test('aria-keyshortcutsisaddedonelementswithaccesskey',asyncfunction(assert){
        assert.expect(1);
        var$target=$('#qunit-fixture');
        varKeyboardWidget=Widget.extend(KeyboardNavigationMixin,{
            init:function(){
                this._super.apply(this,arguments);
                KeyboardNavigationMixin.init.call(this);
            },
            start:function(){
                KeyboardNavigationMixin.start.call(this);
                var$button=$('<button>').text('ClickMe!').attr('accesskey','o');
                //weneedtodefinetheaccesskeybecauseitwillnotbeassignedoninvisiblebuttons
                this.$el.append($button);
                returnthis._super.apply(this,arguments);
            },
            destroy:function(){
                KeyboardNavigationMixin.destroy.call(this);
                returnthis._super(...arguments);
            },
        });
        varparent=awaittestUtils.createParent({});
        varw=newKeyboardWidget(parent);
        awaitw.appendTo($target);

        //minimumsetofattributetogenerateanativeeventthatworkswiththemixin
        vare=newEvent("keydown");
        e.key='';
        e.altKey=true;
        w.$el[0].dispatchEvent(e);

        assert.ok(w.$el.find('button[aria-keyshortcuts]')[0],'thearia-keyshortcutsissetonthebutton');

        parent.destroy();
    });

    QUnit.test('keepCSSpositionabsoluteforparentofoverlay',asyncfunction(assert){
        //IfwechangetheCSSpositionofan'absolute'elementto'relative',
        //wemaylikelychangeitspositiononthedocument.Sincetheoverlay
        //CSSpositionis'absolute',itwillmatchthesizeandcoverthe
        //parentwith'absolute'>'absolute',withoutalteringtheposition
        //oftheparentonthedocument.
        assert.expect(1);
        var$target=$('#qunit-fixture');
        var$button;
        varKeyboardWidget=Widget.extend(KeyboardNavigationMixin,{
            init:function(){
                this._super.apply(this,arguments);
                KeyboardNavigationMixin.init.call(this);
            },
            start:function(){
                KeyboardNavigationMixin.start.call(this);
                $button=$('<button>').text('ClickMe!').attr('accesskey','o');
                //weneedtodefinetheaccesskeybecauseitwillnotbeassignedoninvisiblebuttons
                this.$el.append($button);
                returnthis._super.apply(this,arguments);
            },
            destroy:function(){
                KeyboardNavigationMixin.destroy.call(this);
                returnthis._super(...arguments);
            },
        });
        varparent=awaittestUtils.createParent({});
        varw=newKeyboardWidget(parent);
        awaitw.appendTo($target);

        $button.css('position','absolute');

        //minimumsetofattributetogenerateanativeeventthatworkswiththemixin
        vare=newEvent("keydown");
        e.key='';
        e.altKey=true;
        w.$el[0].dispatchEvent(e);

        assert.strictEqual($button.css('position'),'absolute',
            "shouldnothavekepttheCSSpositionofthebutton");

        parent.destroy();
    });
});
});
