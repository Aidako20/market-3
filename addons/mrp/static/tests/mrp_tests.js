flectra.define('mrp.tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require("web.test_utils");

varcreateView=testUtils.createView;

QUnit.module('mrp',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    state:{
                        string:"State",
                        type:"selection",
                        selection:[['waiting','Waiting'],['chilling','Chilling']],
                    },
                    duration:{string:"Duration",type:"float"},
                },
                records:[{
                    id:1,
                    state:'waiting',
                    duration:6000,
                }],
                onchanges:{},
            },
        };
    },
},function(){

    QUnit.test("bullet_state:basicrendering",asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            res_id:1,
            arch:
                '<form>'+
                    '<fieldname="state"widget="bullet_state"options="{\'classes\':{\'waiting\':\'danger\'}}"/>'+
                '</form>',
        });

        assert.strictEqual(form.$('.o_field_widget').text(),"WaitingMaterials",
            "thewidgetshouldbecorrectlynamed");
        assert.containsOnce(form,'.o_field_widget.badge-danger',
            "thebadgeshouldbedanger");

        form.destroy();
    });

    QUnit.test("mrp_time_counter:basicrendering",asyncfunction(assert){
        assert.expect(2);
        vardata={
            foo:{
                fields:{duration:{string:"Duration",type:"float"}},
                records:[{id:1,duration:150.5}]
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:data,
            res_id:1,
            arch:
                '<form>'+
                    '<fieldname="duration"widget="mrp_time_counter"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='search_read'&&args.model==='mrp.workcenter.productivity'){
                    assert.ok(true,"thewidgetshouldfetchthemrp.workcenter.productivity");
                    returnPromise.resolve([]);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name="duration"]').text(),"150:30",
            "thetimershouldbecorrectlyset");

        form.destroy();
    });

    QUnit.test("embed_viewerrenderinginformview",asyncfunction(assert){
        assert.expect(8);
        vardata={
            foo:{
                fields:{char_url:{string:"URL",type:"char"}},
                records:[{id:1}]
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:data,
            arch:
                '<form>'+
                '<fieldname="char_url"widget="embed_viewer"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route){
                if(route===('http://example.com')){
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.isNotVisible(form.$('iframe.o_embed_iframe'),"thereshouldbeaninvisibleiframereadonlymode");
        assert.strictEqual(_.has(form.$('iframe.o_embed_iframe')[0].attributes,"src"),false,
            "srcattributeisnotsetiftherearenovalues");
        awaittestUtils.form.clickEdit(form);
        assert.isNotVisible(form.$('iframe.o_embed_iframe'),"thereshouldbeaninvisibleiframeineditmode");
        awaittestUtils.fields.editAndTrigger(form.$('.o_field_char'),'http://example.com',['input','change','focusout']);
        assert.strictEqual(form.$('iframe.o_embed_iframe').attr('src'),'http://example.com',
            "srcshouldupdatedontheiframe");
        assert.isVisible(form.$('iframe.o_embed_iframe'),"thereshouldbeavisibleiframeineditmode");
        awaittestUtils.form.clickSave(form);
        assert.isVisible(form.$('iframe.o_embed_iframe'),"thereshouldbeavisibleiframeinreadonlymode");
        assert.strictEqual(form.$('iframe.o_embed_iframe').attr('data-src'),'http://example.com',
            "shouldhaveupdatedsrcinreadonlymode");

        //Inreadonlymode,wearenotdisplayingtheURL,onlyiframewillbethere.
        assert.strictEqual(form.$('.iframe.o_embed_iframe').siblings().length,0,
            "thereshouldn'tbeanysiblingsofiframeinreadonlymode");

        form.destroy();
    });
});
});
