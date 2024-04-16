flectra.define("base.abstract_controller_tests",function(require){
"usestrict";

const{xml}=owl.tags;

vartestUtils=require("web.test_utils");
varcreateView=testUtils.createView;
varBasicView=require("web.BasicView");
varBasicRenderer=require("web.BasicRenderer");
constAbstractRenderer=require('web.AbstractRendererOwl');
constRendererWrapper=require('web.RendererWrapper');

functiongetHtmlRenderer(html){
    returnBasicRenderer.extend({
        start:function(){
            this.$el.html(html);
            returnthis._super.apply(this,arguments);
        }
    });
}

functiongetOwlView(owlRenderer,viewType){
    viewType=viewType||"test";
    returnBasicView.extend({
        viewType:viewType,
        config:_.extend({},BasicView.prototype.config,{
            Renderer:owlRenderer,
        }),
        getRenderer(){
            returnnewRendererWrapper(null,this.config.Renderer,{});
        }
    });
}

functiongetHtmlView(html,viewType){
    viewType=viewType||"test";
    returnBasicView.extend({
        viewType:viewType,
        config:_.extend({},BasicView.prototype.config,{
            Renderer:getHtmlRenderer(html)
        })
    });
}

QUnit.module("Views",{
    beforeEach:function(){
        this.data={
            test_model:{
                fields:{},
                records:[]
            }
        };
    }
},function(){
    QUnit.module('AbstractController');

    QUnit.test('clickonaa[type="action"]childtriggersthecorrectaction',asyncfunction(assert){
        assert.expect(7);

        varhtml=
            "<div>"+
            '<aname="a1"type="action"class="simple">simple</a>'+
            '<aname="a2"type="action"class="with-child">'+
            "<span>child</input>"+
            "</a>"+
            '<atype="action"data-model="foo"data-method="bar"class="method">method</a>'+
            '<atype="action"data-model="foo"data-res-id="42"class="descr">descr</a>'+
            '<atype="action"data-model="foo"class="descr2">descr2</a>'+
            "</div>";

        varview=awaitcreateView({
            View:getHtmlView(html,"test"),
            data:this.data,
            model:"test_model",
            arch:"<test/>",
            intercepts:{
                do_action:function(event){
                    assert.step(event.data.action.name||event.data.action);
                }
            },
            mockRPC:function(route,args){
                if(args.model==='foo'&&args.method==='bar'){
                    assert.step("method");
                    returnPromise.resolve({name:'method'});
                }
                returnthis._super.apply(this,arguments);
            }
        });
        awaittestUtils.dom.click(view.$(".simple"));
        awaittestUtils.dom.click(view.$(".with-childspan"));
        awaittestUtils.dom.click(view.$(".method"));
        awaittestUtils.dom.click(view.$(".descr"));
        awaittestUtils.dom.click(view.$(".descr2"));
        assert.verifySteps(["a1","a2","method","method","descr","descr2"]);

        view.destroy();
    });

    QUnit.test('OWLRenderercorrectlydestroyed',asyncfunction(assert){
        assert.expect(2);

        classRendererextendsAbstractRenderer{
            __destroy(){
                assert.step("destroy");
                super.__destroy();
            }
        }
        Renderer.template=xml`<div>Test</div>`;

        varview=awaitcreateView({
            View:getOwlView(Renderer,"test"),
            data:this.data,
            model:"test_model",
            arch:"<test/>",
        });
        view.destroy();

        assert.verifySteps(["destroy"]);

    });

    QUnit.test('CorrectlysetfocustosearchpanelwithOwlRenderer',asyncfunction(assert){
        assert.expect(1);

        classRendererextendsAbstractRenderer{}
        Renderer.template=xml`<div>Test</div>`;

        varview=awaitcreateView({
            View:getOwlView(Renderer,"test"),
            data:this.data,
            model:"test_model",
            arch:"<test/>",
        });
        assert.hasClass(document.activeElement,"o_searchview_input");
        view.destroy();
    });

    QUnit.test('OwlRenderermounted/willUnmounthooksareproperlycalled',asyncfunction(assert){
        //Thistestcouldberemovedassoonascontrollersandrendererswill
        //bothbeconvertedinOwl.
        assert.expect(3);

        classRendererextendsAbstractRenderer{
            mounted(){
                assert.step("mounted");
            }
            willUnmount(){
                assert.step("unmounted");
            }
        }
        Renderer.template=xml`<div>Test</div>`;

        constview=awaitcreateView({
            View:getOwlView(Renderer,"test"),
            data:this.data,
            model:"test_model",
            arch:"<test/>",
        });

        view.destroy();

        assert.verifySteps([
            "mounted",
            "unmounted",
        ]);
    });
});
});
