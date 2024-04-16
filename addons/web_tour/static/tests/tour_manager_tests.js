flectra.define('web_tour.tour_manager_tests',asyncfunction(require){
    "usestrict";

    constKanbanView=require('web.KanbanView');
    constTourManager=require('web_tour.TourManager');
    consttestUtils=require('web.test_utils');
    constcreateView=testUtils.createView;

    constajax=require('web.ajax');
    const{qweb}=require('web.core');

    //Pre-loadtheTipwidgettemplate
    awaitajax.loadXML('/web_tour/static/src/xml/tip.xml',qweb);

    /**
     *CreateawidgetandaTourManagerinstancewithalistofgivenTourobjects.
     *@seeTourManager.register()formoredetailsontheToursregistrysystem.
     *@param{Object}params
     *@param{string[]}[params.consumed_tours]
     *@param{boolean}[params.debug]
     *@param{string}params.templateinnerHTMLcontentofthewidget
     *@param{Object[]}params.tours{{string}name,{Object}option,{Object[]}steps}
     */
    asyncfunctioncreateTourManager({consumed_tours,debug,template,tours}){
        constparent=awaittestUtils.createParent({debug});
        consttourManager=newTourManager(parent,consumed_tours);
        tourManager.running_step_delay=0;
        for(const{name,options,steps}oftours){
            tourManager.register(name,options,steps);
        }
        const_destroy=tourManager.destroy;
        tourManager.destroy=function(){
            tourManager.destroy=_destroy;
            parent.destroy();
        };
        awaitparent.prependTo(testUtils.prepareTarget(debug));
        parent.el.innerHTML=template;
        testUtils.mock.patch(TourManager,{
            //Sincethe`tour_disable.js`scriptautomaticallysetstoursasconsumed
            //assoonastheyareregistered,weoverridethe"isconsumed"to
            //assertthatthetourisinthe`consumed_tours`paramkey.
            _isTourConsumed:name=>(consumed_tours||[]).includes(name),
        });
        awaittourManager._register_all(true);
        //Waitforpossibletooltipstobeloadedandappended.
        awaittestUtils.nextTick();
        returntourManager;
    }

    QUnit.module("Tours",{
        afterEach(){
            testUtils.mock.unpatch(TourManager);
        },
    },function(){

        QUnit.module("Tourmanager");

        QUnit.test("Tourssequence",asyncfunction(assert){
            assert.expect(2);

            consttourManager=awaitcreateTourManager({
                template:`
                    <buttonclass="btnanchor">Anchor</button>`,
                tours:[
                    {name:"Tour1",options:{sequence:10},steps:[{trigger:'.anchor'}]},
                    {name:"Tour2",options:{},steps:[{trigger:'.anchor'}]},
                    {name:"Tour3",options:{sequence:5},steps:[{trigger:'.anchor',content:"Oui"}]},
                ],
                //Usethistestin"debug"modebecausethetipsneedtobein
                //theviewporttobeabletotesttheirnormalcontent
                //(otherwise,thetipswouldindicatetotheusersthatthey
                //havetoscroll).
                debug:true,
            });

            assert.containsOnce(document.body,'.o_tooltip:visible');
            assert.strictEqual($('.o_tooltip_content:visible').text(),"Oui",
                "contentshouldbethatofthethirdtour");

            tourManager.destroy();
        });

        QUnit.test("Clickoninvisibletipconsumesit",asyncfunction(assert){
            assert.expect(5);

            consttourManager=awaitcreateTourManager({
                template:`
                    <buttonclass="btnanchor1">Anchor</button>
                    <buttonclass="btnanchor2">Anchor</button>
                    `,
                tours:[{
                    name:"Tour1",
                    options:{rainbowMan:false,sequence:10},
                    steps:[{trigger:'.anchor1',content:"1"}],
                },{
                    name:"Tour2",
                    options:{rainbowMan:false,sequence:5},
                    steps:[{trigger:'.anchor2',content:"2"}],
                }],
                //Usethistestin"debug"modebecausethetipsneedtobein
                //theviewporttobeabletotesttheirnormalcontent
                //(otherwise,thetipswouldindicatetotheusersthatthey
                //havetoscroll).
                debug:true,
            });

            assert.containsN(document.body,'.o_tooltip',2);
            assert.strictEqual($('.o_tooltip_content:visible').text(),"2");

            awaittestUtils.dom.click($('.anchor1'));
            assert.containsOnce(document.body,'.o_tooltip');
            assert.strictEqual($('.o_tooltip_content:visible').text(),"2");

            awaittestUtils.dom.click($('.anchor2'));
            assert.containsNone(document.body,'.o_tooltip');

            tourManager.destroy();
        });

        QUnit.test("Stepanchorreplaced",asyncfunction(assert){
            assert.expect(3);

            consttourManager=awaitcreateTourManager({
                observe:true,
                template:`<inputclass="anchor"/>`,
                tours:[{
                    name:"Tour",
                    options:{rainbowMan:false},
                    steps:[{trigger:"input.anchor"}],
                }],
            });

            assert.containsOnce(document.body,'.o_tooltip:visible');


            const$anchor=$(".anchor");
            const$parent=$anchor.parent();
            $parent.empty();
            $parent.append($anchor);
            //Simulatestheobserverpickingupthemutationandtriggeringanupdate
            tourManager.update();
            awaittestUtils.nextTick();

            assert.containsOnce(document.body,'.o_tooltip:visible');

            awaittestUtils.fields.editInput($('.anchor'),"AAA");

            assert.containsNone(document.body,'.o_tooltip:visible');

            tourManager.destroy();
        });

        QUnit.test("kanbanquickcreateVStourtooltips",asyncfunction(assert){
            assert.expect(3);

            constkanban=awaitcreateView({
                View:KanbanView,
                model:'partner',
                data:{
                    partner:{
                        fields:{
                            foo:{string:"Foo",type:"char"},
                            bar:{string:"Bar",type:"boolean"},
                        },
                        records:[
                            {id:1,bar:true,foo:"yop"},
                        ]
                    }
                },
                arch:`<kanban>
                        <fieldname="bar"/>
                        <templates><tt-name="kanban-box">
                            <div><fieldname="foo"/></div>
                        </t></templates>
                        </kanban>`,
                groupBy:['bar'],
            });

            //clicktoaddanelement
            awaittestUtils.dom.click(kanban.$('.o_kanban_header.o_kanban_quick_addi').first());
            assert.containsOnce(kanban,'.o_kanban_quick_create',
                "shouldhaveopenthequickcreatewidget");

            //createtourmanagertargetingthekanbanquickcreateinitssteps
            consttourManager=awaitcreateTourManager({
                observe:true,
                template:kanban.$el.html(),
                tours:[{
                    name:"Tour",
                    options:{rainbowMan:false},
                    steps:[{trigger:"input[name='display_name']"}],
                }],
            });

            assert.containsOnce(document.body,'.o_tooltip:visible');

            awaittestUtils.dom.click($('.o_tooltip:visible'));
            assert.containsOnce(kanban,'.o_kanban_quick_create',
                "thequickcreateshouldnothavebeendestroyedwhentooltipisclicked");

            kanban.destroy();
            tourManager.destroy();
        });
    });
});
