flectra.define('website.tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require("web.test_utils");

varcreateView=testUtils.createView;

QUnit.module('website',{
    before:function(){
        this.data={
            blog_post:{
                fields:{
                    website_published:{string:"AvailableontheWebsite",type:"boolean"},
                },
                records:[{
                    id:1,
                    website_published:false,
                },{
                    id:2,
                    website_published:true,
                }]
            }
        };
    },
},function(){
    QUnit.test("widgetwebsitebutton:displayfalsevalue",asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'blog_post',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<divclass="oe_button_box"name="button_box">'+
                            '<fieldname="website_published"widget="website_redirect_button"/>'+
                        '</div>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });
        varselector='.oe_button_box.oe_stat_button[name="website_published"].o_stat_text';
        assert.containsN(form,selector,1,"thereshouldbeonetextdisplayed");
        selector='.oe_button_box.oe_stat_button[name="website_published"].o_button_icon.fa-globe.text-danger';
        assert.containsOnce(form,selector,"thereshouldbeoneiconinred");
        form.destroy();
    });
    QUnit.test("widgetwebsitebutton:displaytruevalue",asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'blog_post',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<divclass="oe_button_box"name="button_box">'+
                            '<fieldname="website_published"widget="website_redirect_button"/>'+
                        '</div>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });
        varselector='.oe_button_box.oe_stat_button[name="website_published"].o_stat_text';
        assert.containsN(form,selector,1,"shouldbeonetextdisplayed");
        selector='.oe_button_box.oe_stat_button[name="website_published"].o_button_icon.fa-globe.text-success';
        assert.containsOnce(form,selector,"thereshouldbeonetextingreen");
        form.destroy();
    });
});

});
