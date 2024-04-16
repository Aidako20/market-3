flectra.define('hr.StandaloneM2OEmployeeTests',function(require){
    "usestrict";

    const{xml}=owl.tags;

    constAbstractRendererOwl=require('web.AbstractRendererOwl');
    constBasicView=require("web.BasicView");
    constBasicRenderer=require("web.BasicRenderer");
    constRendererWrapper=require('web.RendererWrapper');
    const{createView}=require('web.test_utils');

    constStandaloneM2OAvatarEmployee=require('hr.StandaloneM2OAvatarEmployee');

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
            config:Object.assign({},BasicView.prototype.config,{
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
            config:Object.assign({},BasicView.prototype.config,{
                Renderer:getHtmlRenderer(html)
            })
        });
    }

    QUnit.module('hr',{},function(){
        QUnit.module('StandaloneM2OEmployeeTests',{
            beforeEach:function(){
                this.data={
                    'foo':{
                        fields:{
                            employee_id:{string:"Employee",type:'many2one',relation:'hr.employee'},
                        },
                        records:[],
                    },
                    'hr.employee':{
                        fields:{},
                        records:[
                            {id:10,name:"Mario"},
                            {id:20,name:"Luigi"},
                            {id:30,name:"Yoshi"}
                        ],
                    },
                };
            },
        });

        QUnit.test('standalone_m2o_avatar_employee:legacyview',asyncfunction(assert){
            assert.expect(1);

            consthtml="<divclass='coucou_test'></div>";
            constview=awaitcreateView({
                View:getHtmlView(html,"test"),
                data:this.data,
                model:"foo",
                arch:"<test/>"
            });

            constavatar10=newStandaloneM2OAvatarEmployee(view,10);
            constavatar20=newStandaloneM2OAvatarEmployee(view,20);
            constavatar30=newStandaloneM2OAvatarEmployee(view,[30,'Bowser']);

            awaitavatar10.appendTo(view.el.querySelector('.coucou_test'));
            awaitavatar20.appendTo(view.el.querySelector('.coucou_test'));
            awaitavatar30.appendTo(view.el.querySelector('.coucou_test'));

            assert.deepEqual(
                [...view.el.querySelectorAll('.o_field_many2one_avatarspan')].map(el=>el.innerText),
                ["Mario","Luigi","Bowser"]
            );

            view.destroy();
        });

        QUnit.test('standalone_m2o_avatar_employee:Owlview',asyncfunction(assert){
            assert.expect(1);

            classRendererextendsAbstractRendererOwl{}
            Renderer.template=xml`<divclass='coucou_test'></div>`;

            constview=awaitcreateView({
                View:getOwlView(Renderer,"test"),
                data:this.data,
                model:"foo",
                arch:"<test/>"
            });

            constavatar10=newStandaloneM2OAvatarEmployee(view,10);
            constavatar20=newStandaloneM2OAvatarEmployee(view,20);
            constavatar30=newStandaloneM2OAvatarEmployee(view,[30,'Bowser']);

            awaitavatar10.appendTo(view.el.querySelector('.coucou_test'));
            awaitavatar20.appendTo(view.el.querySelector('.coucou_test'));
            awaitavatar30.appendTo(view.el.querySelector('.coucou_test'));

            assert.deepEqual(
                [...view.el.querySelectorAll('.o_field_many2one_avatarspan')].map(el=>el.innerText),
                ["Mario","Luigi","Bowser"]
            );

            view.destroy();
        });
    });
});
