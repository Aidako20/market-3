flectra.define('web.abstract_view_banner_tests',function(require){
"usestrict";

varAbstractRenderer=require('web.AbstractRenderer');
varAbstractView=require('web.AbstractView');

vartestUtils=require('web.test_utils');
varcreateView=testUtils.createView;

varTestRenderer=AbstractRenderer.extend({
    _renderView:function(){
        this.$el.addClass('test_content');
        returnthis._super();
    },
});

varTestView=AbstractView.extend({
    type:'test',
    config:_.extend({},AbstractView.prototype.config,{
        Renderer:TestRenderer
    }),
});

vartest_css_url='/test_assetsbundle/static/src/css/test_cssfile1.css';

QUnit.module('Views',{
        beforeEach:function(){
            this.data={
                test_model:{
                    fields:{},
                    records:[],
                },
            };
        },
        afterEach:function(){
            $('headlink[href$="'+test_css_url+'"]').remove();
        }
    },function(){
        QUnit.module('BasicRenderer');

        QUnit.test("Thebannershouldbefetchedfromtheroute",function(assert){
            vardone=assert.async();
            assert.expect(6);

            varbanner_html=`
                <divclass="modalo_onboarding_modalo_technical_modal"tabindex="-1"role="dialog">
                    <divclass="modal-dialog"role="document">
                        <divclass="modal-content">
                            <divclass="modal-footer">
                                <atype="action"class="btnbtn-primary"data-dismiss="modal"
                                data-toggle="collapse"href=".o_onboarding_container">
                                    Remove
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                <divclass="o_onboarding_containercollapseshow">
                    <divclass="o_onboarding_wrap">
                        <ahref="#"data-toggle="modal"data-target=".o_onboarding_modal"
                           class="float-righto_onboarding_btn_close">
                            <iclass="fafa-times"title="Closetheonboardingpanel"/>
                        </a>
                    </div>
                    <div>
                        <linktype="text/css"href="`+test_css_url+`"rel="stylesheet">
                        <divclass="hello_banner">Hereisthebanner</div>
                    </div>
                </div>`;

            createView({
                View:TestView,
                model:'test_model',
                data:this.data,
                arch:'<testbanner_route="/module/hello_banner"/>',
                mockRPC:function(route,args){
                    if(route==='/module/hello_banner'){
                        assert.step(route);
                        returnPromise.resolve({html:banner_html});
                    }
                    returnthis._super(route,args);
                },
            }).then(asyncfunction(view){
                var$banner=view.$('.hello_banner');
                assert.strictEqual($banner.length,1,
                    "Theviewshouldcontaintheresponsefromthecontroller.");
                assert.verifySteps(['/module/hello_banner'],"Thebannershouldbefetched.");

                var$head_link=$('headlink[href$="'+test_css_url+'"]');
                assert.strictEqual($head_link.length,1,
                    "Thestylesheetshouldhavebeenaddedtohead.");

                var$banner_link=$('link[href$="'+test_css_url+'"]',$banner);
                assert.strictEqual($banner_link.length,0,
                    "Thestylesheetshouldhavebeenremovedfromthebanner.");

                awaittestUtils.dom.click(view.$('.o_onboarding_btn_close')); //clickonclosetoremovebanner
                awaittestUtils.dom.click(view.$('.o_technical_modal.btn-primary:contains("Remove")')); //clickonbuttonremovefromtechinalmodal
                assert.strictEqual(view.$('.o_onboarding_container.show').length,0,
                    "Bannershouldberemovedfromtheview");

                view.destroy();
                done();
            });
        });
    }
);
});
