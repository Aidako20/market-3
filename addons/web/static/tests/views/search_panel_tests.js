flectra.define("web/static/tests/views/search_panel_tests.js",function(require){
"usestrict";

constFormView=require('web.FormView');
constKanbanView=require('web.KanbanView');
constListView=require('web.ListView');
consttestUtils=require('web.test_utils');
constSearchPanel=require("web/static/src/js/views/search_panel.js");

constcpHelpers=testUtils.controlPanel;
constcreateActionManager=testUtils.createActionManager;
constcreateView=testUtils.createView;

/**
 *Returnthelistofcountersdisplayedinthesearchpanel(ifany).
 *@param{Widget}view,viewcontroller
 *@returns{number[]}
 */
functiongetCounters(view){
    return[...view.el.querySelectorAll('.o_search_panel_counter')].map(
        counter=>Number(counter.innerText.trim())
    );
}

/**
 *Fold/unfoldthecategoryvalue(withchildren)
 *@param{Widget}widget
 *@param{string}text
 *@returns{Promise}
 */
functiontoggleFold(widget,text){
    constheaders=[...widget.el.querySelectorAll(".o_search_panel_category_valueheader")];
    consttarget=headers.find(
        (header)=>header.innerText.trim().startsWith(text)
    );
    returntestUtils.dom.click(target);
}

QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    foo:{string:"Foo",type:'char'},
                    bar:{string:"Bar",type:'boolean'},
                    int_field:{string:"IntField",type:'integer',group_operator:'sum'},
                    company_id:{string:"company",type:'many2one',relation:'company'},
                    company_ids:{string:"Companies",type:'many2many',relation:'company'},
                    category_id:{string:"category",type:'many2one',relation:'category'},
                    state:{string:"State",type:'selection',selection:[['abc',"ABC"],['def',"DEF"],['ghi',"GHI"]]},
                },
                records:[
                    {id:1,bar:true,foo:"yop",int_field:1,company_ids:[3],company_id:3,state:'abc',category_id:6},
                    {id:2,bar:true,foo:"blip",int_field:2,company_ids:[3],company_id:5,state:'def',category_id:7},
                    {id:3,bar:true,foo:"gnap",int_field:4,company_ids:[],company_id:3,state:'ghi',category_id:7},
                    {id:4,bar:false,foo:"blip",int_field:8,company_ids:[5],company_id:5,state:'ghi',category_id:7},
                ]
            },
            company:{
                fields:{
                    name:{string:"DisplayName",type:'char'},
                    parent_id:{string:'Parentcompany',type:'many2one',relation:'company'},
                    category_id:{string:'Category',type:'many2one',relation:'category'},
                },
                records:[
                    {id:3,name:"asustek",category_id:6},
                    {id:5,name:"agrolait",category_id:7},
                ],
            },
            category:{
                fields:{
                    name:{string:"CategoryName",type:'char'},
                },
                records:[
                    {id:6,name:"gold"},
                    {id:7,name:"silver"},
                ]
            },
        };

        this.actions=[{
            id:1,
            name:'Partners',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'kanban'],[false,'list'],[false,'pivot'],[false,'form']],
        },{
            id:2,
            name:'Partners',
            res_model:'partner',
            type:'ir.actions.act_window',
            views:[[false,'form']],
        }];

        this.archs={
            'partner,false,list':'<tree><fieldname="foo"/></tree>',
            'partner,false,kanban':
                `<kanban>
                    <templates>
                        <divt-name="kanban-box"class="oe_kanban_global_click">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            'partner,false,form':
                `<form>
                    <buttonname="1"type="action"string="multiview"/>
                    <fieldname="foo"/>
                </form>`,
            'partner,false,pivot':'<pivot><fieldname="int_field"type="measure"/></pivot>',
            'partner,false,search':
                `<search>
                    <searchpanel>
                        <fieldname="company_id"enable_counters="1"expand="1"/>
                        <fieldname="category_id"select="multi"enable_counters="1"expand="1"/>
                    </searchpanel>
                </search>`,
        };
    },
},function(){

    QUnit.module('SearchPanel');

    QUnit.test('basicrendering',asyncfunction(assert){
        assert.expect(16);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method+'on'+args.model);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                            <fieldname="category_id"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.containsOnce(kanban,'.o_content.o_controller_with_searchpanel>.o_search_panel');
        assert.containsOnce(kanban,'.o_content.o_controller_with_searchpanel>.o_kanban_view');

        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',4);

        assert.containsN(kanban,'.o_search_panel_section',2);

        var$firstSection=kanban.$('.o_search_panel_section:first');
        assert.hasClass($firstSection.find('.o_search_panel_section_headeri'),'fa-folder');
        assert.containsOnce($firstSection,'.o_search_panel_section_header:contains(company)');
        assert.containsN($firstSection,'.o_search_panel_category_value',3);
        assert.containsOnce($firstSection,'.o_search_panel_category_value:first.active');
        assert.strictEqual($firstSection.find('.o_search_panel_category_value').text().replace(/\s/g,''),
            'Allasustek2agrolait2');

        var$secondSection=kanban.$('.o_search_panel_section:nth(1)');
        assert.hasClass($secondSection.find('.o_search_panel_section_headeri'),'fa-filter');
        assert.containsOnce($secondSection,'.o_search_panel_section_header:contains(category)');
        assert.containsN($secondSection,'.o_search_panel_filter_value',2);
        assert.strictEqual($secondSection.find('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'gold1silver3');

        assert.verifySteps([
            'search_panel_select_rangeonpartner',
            'search_panel_select_multi_rangeonpartner',
        ]);

        kanban.destroy();
    });

    QUnit.test('sectionswithcustomiconandcolor',asyncfunction(assert){
        assert.expect(4);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"icon="fa-car"color="blue"enable_counters="1"/>
                            <fieldname="state"select="multi"icon="fa-star"color="#000"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.hasClass(kanban.$('.o_search_panel_section_header:firsti'),'fa-car');
        assert.hasAttrValue(kanban.$('.o_search_panel_section_header:firsti'),'style="{color:blue}"');
        assert.hasClass(kanban.$('.o_search_panel_section_header:nth(1)i'),'fa-star');
        assert.hasAttrValue(kanban.$('.o_search_panel_section_header:nth(1)i'),'style="{color:#000}"');

        kanban.destroy();
    });

    QUnit.test('sectionswithattrinvisible="1"areignored',asyncfunction(assert){
        //'groups'attributesareconvertedserver-sideintoinvisible="1"whentheuserdoesn't
        //belongtothegivengroup
        assert.expect(3);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`<kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                            <fieldname="state"select="multi"invisible="1"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method||route);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(kanban,'.o_search_panel_section');

        assert.verifySteps([
            'search_panel_select_range',
        ]);

        kanban.destroy();
    });

    QUnit.test('categoriesandfiltersorderiskept',asyncfunction(assert){
        assert.expect(4);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                            <fieldname="category_id"select="multi"enable_counters="1"/>
                            <fieldname="state"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            }
        });

        assert.containsN(kanban,'.o_search_panel_section',3);
        assert.strictEqual(kanban.$('.o_search_panel_section_header:nth(0)').text().trim(),
            'company');
        assert.strictEqual(kanban.$('.o_search_panel_section_header:nth(1)').text().trim(),
            'category');
        assert.strictEqual(kanban.$('.o_search_panel_section_header:nth(2)').text().trim(),
            'State');

        kanban.destroy();
    });

    QUnit.test('specifyactivecategoryvalueincontextandmanuallychangecategory',asyncfunction(assert){
        assert.expect(5);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                            <fieldname="state"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnthis._super.apply(this,arguments);
            },
            context:{
                searchpanel_default_company_id:false,
                searchpanel_default_state:'ghi',
            },
        });

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_valueheader.activelabel')].map(
                el=>el.innerText
            ),
            ['All','GHI']
        );

        //select'ABC'inthecategory'state'
        awaittestUtils.dom.click(kanban.el.querySelectorAll('.o_search_panel_category_valueheader')[4]);
        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_valueheader.activelabel')].map(
                el=>el.innerText
            ),
            ['All','ABC']
        );

        assert.verifySteps([
            '[["state","=","ghi"]]',
            '[["state","=","abc"]]'
        ]);
        kanban.destroy();
    });

    QUnit.test('usecategory(onmany2one)torefinesearch',asyncfunction(assert){
        assert.expect(14);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            domain:[['bar','=',true]],
        });

        //select'asustek'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(1).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',2);

        //select'agrolait'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(2)header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //select'All'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:firstheader'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:first.active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',3);

        assert.verifySteps([
            '[["bar","=",true]]',
            '["&",["bar","=",true],["company_id","child_of",3]]',
            '["&",["bar","=",true],["company_id","child_of",5]]',
            '[["bar","=",true]]',
        ]);

        kanban.destroy();
    });

    QUnit.test('usecategory(onselection)torefinesearch',asyncfunction(assert){
        assert.expect(14);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        //select'abc'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(1).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //select'ghi'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(3)header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(3).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',2);

        //select'All'again
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:firstheader'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:first.active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',4);

        assert.verifySteps([
            '[]',
            '[["state","=","abc"]]',
            '[["state","=","ghi"]]',
            '[]',
        ]);

        kanban.destroy();
    });

    QUnit.test('categoryhasbeenarchived',asyncfunction(assert){
        assert.expect(2);

        this.data.company.fields.active={type:'boolean',string:'Archived'};
        this.data.company.records=[
            {
                name:'Company5',
                id:5,
                active:true,
            },{
                name:'childof5archived',
                parent_id:5,
                id:666,
                active:false,
            },{
                name:'childof666',
                parent_id:666,
                id:777,
                active:true,
            }
        ];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                  <templates>
                    <tt-name="kanban-box">
                      <div>
                        <fieldname="foo"/>
                      </div>
                    </t>
                  </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            mockRPC:asyncfunction(route,args){
                if(route==='/web/dataset/call_kw/partner/search_panel_select_range'){
                    varresults=awaitthis._super.apply(this,arguments);
                    results.values=results.values.filter(rec=>rec.active!==false);
                    returnPromise.resolve(results);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(kanban,'.o_search_panel_category_value',2,
            'Thenumberofcategoriesshouldbe2:AllandCompany5');

        assert.containsNone(kanban,'.o_toggle_fold>i',
            'Noneofthecategoriesshouldhavechildren');

        kanban.destroy();
    });

    QUnit.test('usetwocategoriestorefinesearch',asyncfunction(assert){
        assert.expect(14);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                            <fieldname="state"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            domain:[['bar','=',true]],
        });

        assert.containsN(kanban,'.o_search_panel_section',2);
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',3);

        //select'asustek'
        awaittestUtils.dom.click(
            [
                ...kanban.el.querySelectorAll('.o_search_panel_category_valueheader.o_search_panel_label_title')
            ]
            .filter(el=>el.innerText==='asustek')
        );
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',2);

        //select'abc'
        awaittestUtils.dom.click(
            [
                ...kanban.el.querySelectorAll('.o_search_panel_category_valueheader.o_search_panel_label_title')
            ]
            .filter(el=>el.innerText==='ABC')
        );
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //select'ghi'
        awaittestUtils.dom.click(
            [
                ...kanban.el.querySelectorAll('.o_search_panel_category_valueheader.o_search_panel_label_title')
            ]
            .filter(el=>el.innerText==='GHI')
        );
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //select'All'infirstcategory(company_id)
        awaittestUtils.dom.click(kanban.$('.o_search_panel_section:first.o_search_panel_category_value:firstheader'));
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //select'All'insecondcategory(state)
        awaittestUtils.dom.click(kanban.$('.o_search_panel_section:nth(1).o_search_panel_category_value:firstheader'));
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',3);

        assert.verifySteps([
            '[["bar","=",true]]',
            '["&",["bar","=",true],["company_id","child_of",3]]',
            '["&",["bar","=",true],"&",["company_id","child_of",3],["state","=","abc"]]',
            '["&",["bar","=",true],"&",["company_id","child_of",3],["state","=","ghi"]]',
            '["&",["bar","=",true],["state","=","ghi"]]',
            '[["bar","=",true]]',
        ]);

        kanban.destroy();
    });

    QUnit.test('categorywithparent_field',asyncfunction(assert){
        assert.expect(33);

        this.data.company.records.push({id:40,name:'childcompany1',parent_id:5});
        this.data.company.records.push({id:41,name:'childcompany2',parent_id:5});
        this.data.partner.records[1].company_id=40;

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        //'All'isselectedbydefault
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:first.active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',4);
        assert.containsN(kanban,'.o_search_panel_category_value',3);
        assert.containsOnce(kanban,'.o_search_panel_category_value.o_toggle_fold>i');

        //unfoldparentcategoryandselect'All'again
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(2)>header'));
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:first>header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:first.active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',4);
        assert.containsN(kanban,'.o_search_panel_category_value',5);
        assert.containsN(kanban,'.o_search_panel_category_value.o_search_panel_category_value',2);

        //clickonfirstchildcompany
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value.o_search_panel_category_value:firstheader'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value.o_search_panel_category_value:first.active');
        assert.containsOnce(kanban,'.o_kanban_record:not(.o_kanban_ghost)');

        //clickonparentcompany
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(2)>header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsOnce(kanban,'.o_kanban_record:not(.o_kanban_ghost)');

        //foldparentcompanybyclickingonit
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(2)>header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //parentcompanyshouldbefolded
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsN(kanban,'.o_search_panel_category_value',3);
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //foldcategorywithchildren
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(2)>header'));
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(2)>header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsN(kanban,'.o_search_panel_category_value',3);
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        assert.verifySteps([
            '[]',
            '[["company_id","child_of",5]]',
            '[]',
            '[["company_id","child_of",40]]',
            '[["company_id","child_of",5]]',
        ]);

        kanban.destroy();
    });

    QUnit.test('categorywithnoparent_field',asyncfunction(assert){
        assert.expect(10);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="category_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        //'All'isselectedbydefault
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:first.active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',4);
        assert.containsN(kanban,'.o_search_panel_category_value',3);

        //clickon'gold'category
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(1).active');
        assert.containsOnce(kanban,'.o_kanban_record:not(.o_kanban_ghost)');

        assert.verifySteps([
            '[]',
            '[["category_id","=",6]]',//mustuse'='operator(insteadof'child_of')
        ]);

        kanban.destroy();
    });

    QUnit.test('can(un)foldparentcategoryvalues',asyncfunction(assert){
        assert.expect(7);

        this.data.company.records.push({id:40,name:'childcompany1',parent_id:5});
        this.data.company.records.push({id:41,name:'childcompany2',parent_id:5});
        this.data.partner.records[1].company_id=40;

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.strictEqual(kanban.$('.o_search_panel_category_value:contains(agrolait).o_toggle_fold>i').length,1,
            "'agrolait'shouldbedisplayedasaparentcategoryvalue");
        assert.hasClass(kanban.$('.o_search_panel_category_value:contains(agrolait).o_toggle_fold>i'),'fa-caret-right',
            "'agrolait'shouldbefolded");
        assert.containsN(kanban,'.o_search_panel_category_value',3);

        //unfoldagrolait
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:contains(agrolait).o_toggle_fold>i'));
        assert.hasClass(kanban.$('.o_search_panel_category_value:contains(agrolait).o_toggle_fold>i'),'fa-caret-down',
            "'agrolait'shouldbeopen");
        assert.containsN(kanban,'.o_search_panel_category_value',5);

        //foldagrolait
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:contains(agrolait).o_toggle_fold>i'));
        assert.hasClass(kanban.$('.o_search_panel_category_value:contains(agrolait).o_toggle_fold>i'),'fa-caret-right',
            "'agrolait'shouldbefolded");
        assert.containsN(kanban,'.o_search_panel_category_value',3);

        kanban.destroy();
    });

    QUnit.test('foldstatusiskeptatreload',asyncfunction(assert){
        assert.expect(4);

        this.data.company.records.push({id:40,name:'childcompany1',parent_id:5});
        this.data.company.records.push({id:41,name:'childcompany2',parent_id:5});
        this.data.partner.records[1].company_id=40;

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        //unfoldagrolait
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:contains(agrolait)>header'));
        assert.hasClass(kanban.$('.o_search_panel_category_value:contains(agrolait).o_toggle_fold>i'),'fa-caret-down',
            "'agrolait'shouldbeopen");
        assert.containsN(kanban,'.o_search_panel_category_value',5);

        awaitkanban.reload({});

        assert.hasClass(kanban.$('.o_search_panel_category_value:contains(agrolait).o_toggle_fold>i'),'fa-caret-down',
            "'agrolait'shouldbeopen");
        assert.containsN(kanban,'.o_search_panel_category_value',5);

        kanban.destroy();
    });

    QUnit.test('concurrency:delayedsearch_reads',asyncfunction(assert){
        assert.expect(19);

        vardef;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            domain:[['bar','=',true]],
        });

        //'All'shouldbeselectedbydefault
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:first.active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',3);

        //select'asustek'(delaythereload)
        def=testUtils.makeTestPromise();
        varasustekDef=def;
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        //'asustek'shouldbeselected,butthereshouldstillbe3records
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(1).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',3);

        //select'agrolait'(delaythereload)
        def=testUtils.makeTestPromise();
        varagrolaitDef=def;
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(2)header'));

        //'agrolait'shouldbeselected,butthereshouldstillbe3records
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',3);

        //unlockasusteksearch(shouldbeignored,sothereshouldstillbe3records)
        asustekDef.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',3);

        //unlockagrolaitsearch,thereshouldnowbe1record
        agrolaitDef.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        assert.verifySteps([
            '[["bar","=",true]]',
            '["&",["bar","=",true],["company_id","child_of",3]]',
            '["&",["bar","=",true],["company_id","child_of",5]]',
        ]);

        kanban.destroy();
    });

    QUnit.test("concurrency:singlecategory",asyncfunction(assert){
        assert.expect(12);

        letprom=testUtils.makeTestPromise();
        constkanbanPromise=createView({
            arch:`
                <kanban>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            archs:{
                "partner,false,search":`
                    <search>
                        <filtername="Filter"domain="[('id','=',1)]"/>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            context:{
                searchpanel_default_company_id:[5],
            },
            data:this.data,
            asyncmockRPC(route,args){
                const_super=this._super.bind(this);
                if(route!=="/web/dataset/search_read"){
                    awaitprom;
                }
                assert.step(args.method||route);
                return_super(...arguments);
            },
            model:'partner',
            View:KanbanView,
        });

        //Case1:searchpanelisawaitedtobuildthequerywithsearchdefaults
        awaittestUtils.nextTick();
        assert.verifySteps([]);

        prom.resolve();
        constkanban=awaitkanbanPromise;

        assert.verifySteps([
            "search_panel_select_range",
            "/web/dataset/search_read",
        ]);

        //Case2:searchdomainchangedsowewaitforthesearchpanelonceagain
        prom=testUtils.makeTestPromise();

        awaittestUtils.controlPanel.toggleFilterMenu(kanban);
        awaittestUtils.controlPanel.toggleMenuItem(kanban,0);

        assert.verifySteps([]);

        prom.resolve();
        awaittestUtils.nextTick();

        assert.verifySteps([
            "search_panel_select_range",
            "/web/dataset/search_read",
        ]);

        //Case3:searchdomainisthesameanddefaultvaluesdonotmatteranymore
        prom=testUtils.makeTestPromise();

        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        //Thesearchreadisexecutedrightawayinthiscase
        assert.verifySteps(["/web/dataset/search_read"]);

        prom.resolve();
        awaittestUtils.nextTick();

        assert.verifySteps(["search_panel_select_range"]);

        kanban.destroy();
    });

    QUnit.test("concurrency:categoryandfilter",asyncfunction(assert){
        assert.expect(5);

        letprom=testUtils.makeTestPromise();
        constkanbanPromise=createView({
            arch:`
                <kanban>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            archs:{
                "partner,false,search":`
                    <search>
                        <searchpanel>
                            <fieldname="category_id"enable_counters="1"/>
                            <fieldname="company_id"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            asyncmockRPC(route,args){
                const_super=this._super.bind(this);
                if(route!=="/web/dataset/search_read"){
                    awaitprom;
                }
                assert.step(args.method||route);
                return_super(...arguments);
            },
            model:'partner',
            View:KanbanView,
        });

        awaittestUtils.nextTick();
        assert.verifySteps(["/web/dataset/search_read"]);

        prom.resolve();
        constkanban=awaitkanbanPromise;

        assert.verifySteps([
            "search_panel_select_range",
            "search_panel_select_multi_range",
        ]);

        kanban.destroy();
    });

    QUnit.test("concurrency:categoryandfilterwithadomain",asyncfunction(assert){
        assert.expect(5);

        letprom=testUtils.makeTestPromise();
        constkanbanPromise=createView({
            arch:`
                <kanban>
                    <templates>
                        <divt-name="kanban-box">
                            <fieldname="foo"/>
                        </div>
                    </templates>
                </kanban>`,
            archs:{
                "partner,false,search":`
                    <search>
                        <searchpanel>
                            <fieldname="category_id"enable_counters="1"/>
                            <fieldname="company_id"select="multi"domain="[['category_id','=',category_id]]"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            asyncmockRPC(route,args){
                const_super=this._super.bind(this);
                if(route!=="/web/dataset/search_read"){
                    awaitprom;
                }
                assert.step(args.method||route);
                return_super(...arguments);
            },
            model:'partner',
            View:KanbanView,
        });

        awaittestUtils.nextTick();
        assert.verifySteps([]);

        prom.resolve();
        constkanban=awaitkanbanPromise;

        assert.verifySteps([
            "search_panel_select_range",
            "search_panel_select_multi_range",
            "/web/dataset/search_read",
        ]);

        kanban.destroy();
    });

    QUnit.test('concurrency:misorderedget_filters',asyncfunction(assert){
        assert.expect(15);

        vardef;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='search_panel_select_multi_range'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"enable_counters="1"/>
                            <fieldname="company_id"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        //'All'shouldbeselectedbydefault
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:first.active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',4);

        //select'abc'(delaythereload)
        def=testUtils.makeTestPromise();
        varabcDef=def;
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        //'All'shouldstillbeselected,andthereshouldstillbe4records
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(1).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //select'ghi'(delaythereload)
        def=testUtils.makeTestPromise();
        varghiDef=def;
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(3)header'));

        //'All'shouldstillbeselected,andthereshouldstillbe4records
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(3).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',2);

        //unlockghisearch
        ghiDef.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(3).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',2);

        //unlockabcsearch(shouldbeignored)
        abcDef.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(3).active');
        assert.containsN(kanban,'.o_kanban_record:not(.o_kanban_ghost)',2);

        kanban.destroy();
    });

    QUnit.test('concurrency:delayedget_filter',asyncfunction(assert){
        assert.expect(3);

        vardef;
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='search_panel_select_multi_range'){
                    returnPromise.resolve(def).then(_.constant(result));
                }
                returnresult;
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="Filter"domain="[('id','=',1)]"/>
                        <searchpanel>
                            <fieldname="company_id"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',4);

        //triggerareloadanddelaytheget_filter
        def=testUtils.makeTestPromise();
        awaitcpHelpers.toggleFilterMenu(kanban);
        awaitcpHelpers.toggleMenuItem(kanban,0);
        awaittestUtils.nextTick();

        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',4);

        def.resolve();
        awaittestUtils.nextTick();

        assert.containsOnce(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)');

        kanban.destroy();
    });

    QUnit.test('usefilter(onmany2one)torefinesearch',asyncfunction(assert){
        assert.expect(32);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='search_panel_select_multi_range'){
                    //thefollowingkeysshouldhavesamevalueforallcallstothisroute
                    varkeys=['field_name','group_by','comodel_domain','search_domain','category_domain'];
                    assert.deepEqual(_.pick(args.kwargs,keys),{
                        group_by:false,
                        comodel_domain:[],
                        search_domain:[['bar','=',true]],
                        category_domain:[],
                    });
                    //thefilter_domaindependsonthefilterselection
                    assert.step(JSON.stringify(args.kwargs.filter_domain));
                }
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnresult;
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            domain:[['bar','=',true]],
        });

        assert.containsN(kanban,'.o_search_panel_filter_value',2);
        assert.containsNone(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolait1');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',3);

        //check'asustek'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:firstinput'));

        assert.containsOnce(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolait1');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',2);

        //check'agrolait'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:nth(1)input'));

        assert.containsN(kanban,'.o_search_panel_filter_valueinput:checked',2);
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolait1');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',3);

        //uncheck'asustek'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:firstinput'));

        assert.containsOnce(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolait1');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',1);

        //uncheck'agrolait'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:nth(1)input'));

        assert.containsNone(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolait1');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',3);

        assert.verifySteps([
            //nothingchecked
            '[]',
            '[["bar","=",true]]',
            //'asustek'checked
            '[]',
            '["&",["bar","=",true],["company_id","in",[3]]]',
            //'asustek'and'agrolait'checked
            '[]',
            '["&",["bar","=",true],["company_id","in",[3,5]]]',
            //'agrolait'checked
            '[]',
            '["&",["bar","=",true],["company_id","in",[5]]]',
            //nothingchecked
            '[]',
            '[["bar","=",true]]',
        ]);

        kanban.destroy();
    });

    QUnit.test('usefilter(onselection)torefinesearch',asyncfunction(assert){
        assert.expect(32);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='search_panel_select_multi_range'){
                    //thefollowingkeysshouldhavesamevalueforallcallstothisroute
                    varkeys=['group_by','comodel_domain','search_domain','category_domain'];
                    assert.deepEqual(_.pick(args.kwargs,keys),{
                        group_by:false,
                        comodel_domain:[],
                        search_domain:[['bar','=',true]],
                        category_domain:[],
                    });
                    //thefilter_domaindependsonthefilterselection
                    assert.step(JSON.stringify(args.kwargs.filter_domain));
                }
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnresult;
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"select="multi"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            domain:[['bar','=',true]],
        });

        assert.containsN(kanban,'.o_search_panel_filter_value',3);
        assert.containsNone(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'ABC1DEF1GHI1');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',3);

        //check'abc'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:firstinput'));

        assert.containsOnce(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'ABC1DEF1GHI1');
        assert.containsOnce(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',1);

        //check'def'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:nth(1)input'));

        assert.containsN(kanban,'.o_search_panel_filter_valueinput:checked',2);
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'ABC1DEF1GHI1');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',2);

        //uncheck'abc'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:firstinput'));

        assert.containsOnce(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'ABC1DEF1GHI1');
        assert.containsOnce(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)');

        //uncheck'def'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:nth(1)input'));

        assert.containsNone(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'ABC1DEF1GHI1');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',3);

        assert.verifySteps([
            //nothingchecked
            '[]',
            '[["bar","=",true]]',
            //'asustek'checked
            '[]',
            '["&",["bar","=",true],["state","in",["abc"]]]',
            //'asustek'and'agrolait'checked
            '[]',
            '["&",["bar","=",true],["state","in",["abc","def"]]]',
            //'agrolait'checked
            '[]',
            '["&",["bar","=",true],["state","in",["def"]]]',
            //nothingchecked
            '[]',
            '[["bar","=",true]]',
        ]);

        kanban.destroy();
    });

    QUnit.test("onlyreloadcategoriesandfilterswhendomainschange(countersdisabled,selection)",asyncfunction(assert){
        assert.expect(8);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="Filter"domain="[('id','&lt;',5)]"/>
                        <searchpanel>
                            <fieldname="state"expand="1"/>
                            <fieldname="company_id"select="multi"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            viewOptions:{
                limit:2,
            },
        });

        assert.verifySteps([
            'search_panel_select_range',
            'search_panel_select_multi_range',
        ]);

        //gotopage2(thedomaindoesn'tchange,sothefiltersshouldnotbereloaded)
        awaitcpHelpers.pagerNext(kanban);

        assert.verifySteps([]);

        //reloadwithanotherdomain,sothefiltersshouldbereloaded
        awaitcpHelpers.toggleFilterMenu(kanban);
        awaitcpHelpers.toggleMenuItem(kanban,0);

        assert.verifySteps([
            'search_panel_select_multi_range',
        ]);

        //changecategoryvalue,sothefiltersshouldbereloaded
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.verifySteps([
            'search_panel_select_multi_range',
        ]);

        kanban.destroy();
    });

    QUnit.test("onlyreloadcategoriesandfilterswhendomainschange(countersdisabled,many2one)",asyncfunction(assert){
        assert.expect(8);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="domain"domain="[('id','&lt;',5)]"/>
                        <searchpanel>
                            <fieldname="category_id"expand="1"/>
                            <fieldname="company_id"select="multi"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            viewOptions:{
                limit:2,
            },
        });

        assert.verifySteps([
            'search_panel_select_range',
            'search_panel_select_multi_range',
        ]);

        //gotopage2(thedomaindoesn'tchange,sothefiltersshouldnotbereloaded)
        awaitcpHelpers.pagerNext(kanban);

        assert.verifySteps([]);

        //reloadwithanotherdomain,sothefiltersshouldbereloaded
        awaitcpHelpers.toggleFilterMenu(kanban);
        awaitcpHelpers.toggleMenuItem(kanban,0);

        assert.verifySteps([
            'search_panel_select_multi_range',
        ]);

        //changecategoryvalue,sothefiltersshouldbereloaded
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.verifySteps([
            'search_panel_select_multi_range',
        ]);

        kanban.destroy();
    });

    QUnit.test('categorycounters',asyncfunction(assert){
        assert.expect(16);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method);
                }
                if(route==="/web/dataset/call_kw/partner/search_panel_select_range"){
                    assert.step(args.args[0]);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="Filter"domain="[('id','&lt;',3)]"/>
                        <searchpanel>
                            <fieldname="state"enable_counters="1"expand="1"/>
                            <fieldname="company_id"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            viewOptions:{
                limit:2,
            },
        });

        assert.verifySteps([
            'search_panel_select_range',
            'state',
            'search_panel_select_range',
            'company_id',
        ]);

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_value')].map(
                e=>e.innerText.replace(/\s/g,'')
            ),
            [ "All","ABC1","DEF1","GHI2","All","asustek","agrolait"]
        );

        //gotopage2(thedomaindoesn'tchange,sothecategoriesshouldnotbereloaded)
        awaitcpHelpers.pagerNext(kanban);

        assert.verifySteps([]);

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_value')].map(
                e=>e.innerText.replace(/\s/g,'')
            ),
            [ "All","ABC1","DEF1","GHI2","All","asustek","agrolait"]
        );

        //reloadwithanotherdomain,sothecategories'state'and'company_id'shouldbereloaded
        awaitcpHelpers.toggleFilterMenu(kanban);
        awaitcpHelpers.toggleMenuItem(kanban,0);

        assert.verifySteps([
            'search_panel_select_range',
            'state',
        ]);

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_value')].map(
                e=>e.innerText.replace(/\s/g,'')
            ),
            [ "All","ABC1","DEF1","GHI","All","asustek","agrolait"]
        );

        //changecategoryvalue,sothecategory'state'shouldbereloaded
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_value')].map(
                e=>e.innerText.replace(/\s/g,'')
            ),
            [ "All","ABC1","DEF1","GHI","All","asustek","agrolait"]
        );

        assert.verifySteps([
            'search_panel_select_range',
            'state',
        ]);

        kanban.destroy();
    });

    QUnit.test('categoryselectionwithoutcounters',asyncfunction(assert){
        assert.expect(10);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method);
                }
                if(route==="/web/dataset/call_kw/partner/search_panel_select_range"){
                    assert.step(args.args[0]);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="Filter"domain="[('id','&lt;',3)]"/>
                        <searchpanel>
                            <fieldname="state"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            viewOptions:{
                limit:2,
            },
        });

        assert.verifySteps([
            'search_panel_select_range',
            'state',
        ]);

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_value')].map(
                e=>e.innerText.replace(/\s/g,'')
            ),
            [ "All","ABC","DEF","GHI"]
        );

        //gotopage2(thedomaindoesn'tchange,sothecategoriesshouldnotbereloaded)
        awaitcpHelpers.pagerNext(kanban);

        assert.verifySteps([]);

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_value')].map(
                e=>e.innerText.replace(/\s/g,'')
            ),
            [ "All","ABC","DEF","GHI"]
        );

        //reloadwithanotherdomain,sothecategory'state'shouldbereloaded
        awaitcpHelpers.toggleFilterMenu(kanban);
        awaitcpHelpers.toggleMenuItem(kanban,0);

        assert.verifySteps([]);

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_value')].map(
                e=>e.innerText.replace(/\s/g,'')
            ),
            [ "All","ABC","DEF","GHI"]
        );

        //changecategoryvalue,sothecategory'state'shouldbereloaded
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_value')].map(
                e=>e.innerText.replace(/\s/g,'')
            ),
            [ "All","ABC","DEF","GHI"]
        );

        assert.verifySteps([]);

        kanban.destroy();
    });

    QUnit.test('filterwithgroupby',asyncfunction(assert){
        assert.expect(42);

        this.data.company.records.push({id:11,name:'camptocamp',category_id:7});

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='search_panel_select_multi_range'){
                    //thefollowingkeysshouldhavesamevalueforallcallstothisroute
                    varkeys=['group_by','comodel_domain','search_domain','category_domain'];
                    assert.deepEqual(_.pick(args.kwargs,keys),{
                        group_by:'category_id',
                        comodel_domain:[],
                        search_domain:[['bar','=',true]],
                        category_domain:[],
                    });
                    //thefilter_domaindependsonthefilterselection
                    assert.step(JSON.stringify(args.kwargs.filter_domain));
                }
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnresult;
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"groupby="category_id"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            domain:[['bar','=',true]],
        });

        assert.containsN(kanban,'.o_search_panel_filter_group',2);
        assert.containsOnce(kanban,'.o_search_panel_filter_group:first.o_search_panel_filter_value');
        assert.containsN(kanban,'.o_search_panel_filter_group:nth(1).o_search_panel_filter_value',2);
        assert.containsNone(kanban,'.o_search_panel_filter_valueinput:checked');
        assert.strictEqual(kanban.$('.o_search_panel_filter_group>header>div>label').text().replace(/\s/g,''),
            'goldsilver');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolait1camptocamp');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',3);

        //check'asustek'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:firstinput'));

        assert.containsOnce(kanban,'.o_search_panel_filter_valueinput:checked');
        varfirstGroupCheckbox=kanban.$('.o_search_panel_filter_group:first>header>div>input').get(0);
        assert.strictEqual(firstGroupCheckbox.checked,true,
            "firstgroupcheckboxshouldbechecked");
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolaitcamptocamp');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',2);

        //check'agrolait'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:nth(1)input'));

        assert.containsN(kanban,'.o_search_panel_filter_valueinput:checked',2);
        varsecondGroupCheckbox=kanban.$('.o_search_panel_filter_group:nth(1)>header>div>input').get(0);
        assert.strictEqual(secondGroupCheckbox.checked,false,
            "secondgroupcheckboxshouldnotbechecked");
        assert.strictEqual(secondGroupCheckbox.indeterminate,true,
            "secondgroupcheckboxshouldbeindeterminate");
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustekagrolaitcamptocamp');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',0);

        //check'camptocamp'
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_value:nth(2)input'));

        assert.containsN(kanban,'.o_search_panel_filter_valueinput:checked',3);
        secondGroupCheckbox=kanban.$('.o_search_panel_filter_group:nth(1)>header>div>input').get(0);
        assert.strictEqual(secondGroupCheckbox.checked,true,
            "secondgroupcheckboxshouldbechecked");
        assert.strictEqual(secondGroupCheckbox.indeterminate,false,
            "secondgroupcheckboxshouldnotbeindeterminate");
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustekagrolaitcamptocamp');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',0);

        //unchecksecondgroup
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter_group:nth(1)>header>div>input'));

        assert.containsOnce(kanban,'.o_search_panel_filter_valueinput:checked');
        secondGroupCheckbox=kanban.$('.o_search_panel_filter_group:nth(1)>header>div>input').get(0);
        assert.strictEqual(secondGroupCheckbox.checked,false,
            "secondgroupcheckboxshouldnotbechecked");
        assert.strictEqual(secondGroupCheckbox.indeterminate,false,
            "secondgroupcheckboxshouldnotbeindeterminate");
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolaitcamptocamp');
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',2);

        assert.verifySteps([
            //nothingchecked
            '[]',
            '[["bar","=",true]]',
            //'asustek'checked
            '[]',
            '["&",["bar","=",true],["company_id","in",[3]]]',
            //'asustek'and'agrolait'checked
            '[]',
            '["&",["bar","=",true],"&",["company_id","in",[3]],["company_id","in",[5]]]',
            //'asustek','agrolait'and'camptocamp'checked
            '[]',
            '["&",["bar","=",true],"&",["company_id","in",[3]],["company_id","in",[5,11]]]',
            //'asustek'checked
            '[]',
            '["&",["bar","=",true],["company_id","in",[3]]]',
        ]);

        kanban.destroy();
    });

    QUnit.test('filterwithdomain',asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:40,name:'childcompany1',parent_id:3});

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='search_panel_select_multi_range'){
                    assert.deepEqual(args.kwargs,{
                        group_by:false,
                        category_domain:[],
                        expand:true,
                        filter_domain:[],
                        search_domain:[],
                        comodel_domain:[['parent_id','=',false]],
                        group_domain:[],
                        enable_counters:true,
                        limit:200,
                    });
                }
                returnresult;
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"domain="[('parent_id','=',False)]"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.containsN(kanban,'.o_search_panel_filter_value',2);
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'asustek2agrolait2');

        kanban.destroy();
    });

    QUnit.test('filterwithdomaindependingoncategory',asyncfunction(assert){
        assert.expect(22);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='search_panel_select_multi_range'){
                    //thefollowingkeysshouldhavesamevalueforallcallstothisroute
                    varkeys=['group_by','search_domain','filter_domain'];
                    assert.deepEqual(_.pick(args.kwargs,keys),{
                        group_by:false,
                        filter_domain:[],
                        search_domain:[],
                    });
                    assert.step(JSON.stringify(args.kwargs.category_domain));
                    assert.step(JSON.stringify(args.kwargs.comodel_domain));
                }
                returnresult;
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="category_id"enable_counters="1"/>
                            <fieldname="company_id"select="multi"domain="[['category_id','=',category_id]]"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        //select'gold'category
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value.active');
        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(1).active');
        assert.containsOnce(kanban,'.o_search_panel_filter_value');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            "asustek1");

        //select'silver'category
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(2)header'));

        assert.containsOnce(kanban,'.o_search_panel_category_value:nth(2).active');
        assert.containsOnce(kanban,'.o_search_panel_filter_value');
        assert.strictEqual(kanban.$('.o_search_panel_filter_value').text().replace(/\s/g,''),
            "agrolait2");

        //selectAll
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:firstheader'));

        assert.containsOnce(kanban,'.o_search_panel_category_value:first.active');
        assert.containsNone(kanban,'.o_search_panel_filter_value');

        assert.verifySteps([
            '[]',//category_domain(All)
            '[["category_id","=",false]]',//comodel_domain(All)
            '[["category_id","=",6]]',//category_domain('gold')
            '[["category_id","=",6]]',//comodel_domain('gold')
            '[["category_id","=",7]]',//category_domain('silver')
            '[["category_id","=",7]]',//comodel_domain('silver')
            '[]',//category_domain(All)
            '[["category_id","=",false]]',//comodel_domain(All)
        ]);

        kanban.destroy();
    });

    QUnit.test('specifyactivefiltervaluesincontext',asyncfunction(assert){
        assert.expect(4);

        varexpectedDomain=[
            "&",
            ['company_id','in',[5]],
            ['state','in',['abc','ghi']],
        ];
        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"enable_counters="1"/>
                            <fieldname="state"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.deepEqual(args.domain,expectedDomain);
                }
                returnthis._super.apply(this,arguments);
            },
            context:{
                searchpanel_default_company_id:[5],
                searchpanel_default_state:['abc','ghi'],
            },
        });

        assert.containsN(kanban,'.o_search_panel_filter_valueinput:checked',3);

        //manuallyuntickadefaultvalue
        expectedDomain=[['state','in',['abc','ghi']]];
        awaittestUtils.dom.click(kanban.$('.o_search_panel_filter:first.o_search_panel_filter_value:nth(1)input'));

        assert.containsN(kanban,'.o_search_panel_filter_valueinput:checked',2);

        kanban.destroy();
    });

    QUnit.test('retrievedfiltervaluefromcontextdoesnotexist',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.deepEqual(args.domain,[["company_id","in",[3]]]);
                }
                returnthis._super.apply(this,arguments);
            },
            context:{
                searchpanel_default_company_id:[1,3],
            },
        });

        kanban.destroy();
    });

    QUnit.test('filterwithgroupbyanddefaultvaluesincontext',asyncfunction(assert){
        assert.expect(2);

        this.data.company.records.push({id:11,name:'camptocamp',category_id:7});

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"groupby="category_id"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.deepEqual(args.domain,[['company_id','in',[5]]]);
                }
                returnthis._super.apply(this,arguments);
            },
            context:{
                searchpanel_default_company_id:[5],
            },
        });

        varsecondGroupCheckbox=kanban.$('.o_search_panel_filter_group:nth(1)>header>div>input').get(0);
        assert.strictEqual(secondGroupCheckbox.indeterminate,true);

        kanban.destroy();
    });

    QUnit.test('Doesnotconfusefalseand"false"groupbyvalues',asyncfunction(assert){
        assert.expect(6);

        this.data.company.fields.char_field={string:"CharField",type:'char'};

        this.data.company.records=[
            {id:3,name:'A',char_field:false,},
            {id:5,name:'B',char_field:'false',}
        ];

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`<kanban>
                    <templates><tt-name="kanban-box">
                        <div>
                            <fieldname="foo"/>
                        </div>
                    </t></templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"groupby="char_field"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.containsOnce(kanban,'.o_search_panel_section');
        var$firstSection=kanban.$('.o_search_panel_section');

        //Thereshouldbeagroup'false'displayedwithonlyvalueBinsideit.
        assert.containsOnce($firstSection,'.o_search_panel_filter_group');
        assert.strictEqual($firstSection.find('.o_search_panel_filter_group').text().replace(/\s/g,''),
            'falseB');
        assert.containsOnce($firstSection.find('.o_search_panel_filter_group'),'.o_search_panel_filter_value');

        //Globally,thereshouldbetwovalues,onedisplayedinthegroup'false',andoneattheendofthesection
        //(thegroupfalseisnotdisplayedanditsvaluesaredisplayedatthefirstlevel)
        assert.containsN($firstSection,'.o_search_panel_filter_value',2);
        assert.strictEqual($firstSection.find('.o_search_panel_filter_value').text().replace(/\s/g,''),
            'BA');

        kanban.destroy();
    });

    QUnit.test('testsconservationofcategoryrecordorder',asyncfunction(assert){
        assert.expect(1);

        this.data.company.records.push({id:56,name:'highID',category_id:6});
        this.data.company.records.push({id:2,name:'lowID',category_id:6});

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"expand="1"/>
                            <fieldname="category_id"select="multi"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        var$firstSection=kanban.$('.o_search_panel_section:first');
        assert.strictEqual($firstSection.find('.o_search_panel_category_value').text().replace(/\s/g,''),
            'Allasustek2agrolait2highIDlowID');
        kanban.destroy();
    });

    QUnit.test('searchpanelisavailableonlistandkanbanbydefault',asyncfunction(assert){
        assert.expect(8);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(1);

        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_kanban_view');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_search_panel');

        awaitcpHelpers.switchView(actionManager,'pivot');
        awaittestUtils.nextTick();
        assert.containsOnce(actionManager,'.o_content.o_pivot');
        assert.containsNone(actionManager,'.o_content.o_search_panel');

        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_list_view');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_search_panel');

        awaittestUtils.dom.click(actionManager.$('.o_data_row.o_data_cell:first'));
        assert.containsOnce(actionManager,'.o_content.o_form_view');
        assert.containsNone(actionManager,'.o_content.o_search_panel');

        actionManager.destroy();
    });

    QUnit.test('searchpanelwithview_typesattribute',asyncfunction(assert){
        assert.expect(6);

        this.archs['partner,false,search']=
            `<search>
                <searchpanelview_types="kanban,pivot">
                    <fieldname="company_id"enable_counters="1"/>
                    <fieldname="category_id"select="multi"enable_counters="1"/>
                </searchpanel>
            </search>`;


        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(1);

        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_kanban_view');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_search_panel');

        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsOnce(actionManager,'.o_content.o_list_view');
        assert.containsNone(actionManager,'.o_content.o_search_panel');

        awaitcpHelpers.switchView(actionManager,'pivot');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_pivot');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_search_panel');

        actionManager.destroy();
    });

    QUnit.test('searchpanelstateissharedbetweenviews',asyncfunction(assert){
        assert.expect(16);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(1);

        assert.hasClass(actionManager.$('.o_search_panel_category_value:firstheader'),'active');
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',4);

        //select'asustek'company
        awaittestUtils.dom.click(actionManager.$('.o_search_panel_category_value:nth(1)header'));
        assert.hasClass(actionManager.$('.o_search_panel_category_value:nth(1)header'),'active');
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',2);

        awaitcpHelpers.switchView(actionManager,'list');
        assert.hasClass(actionManager.$('.o_search_panel_category_value:nth(1)header'),'active');
        assert.containsN(actionManager,'.o_data_row',2);

        //select'agrolait'company
        awaittestUtils.dom.click(actionManager.$('.o_search_panel_category_value:nth(2)header'));
        assert.hasClass(actionManager.$('.o_search_panel_category_value:nth(2)header'),'active');
        assert.containsN(actionManager,'.o_data_row',2);

        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.hasClass(actionManager.$('.o_search_panel_category_value:nth(2)header'),'active');
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',2);

        assert.verifySteps([
            '[]',//initialsearch_read
            '[["company_id","child_of",3]]',//kanban,afterselectingthefirstcompany
            '[["company_id","child_of",3]]',//list
            '[["company_id","child_of",5]]',//list,afterselectingtheothercompany
            '[["company_id","child_of",5]]',//kanban
        ]);

        actionManager.destroy();
    });

    QUnit.test('searchpanelfiltersarekeptbetweenswitchviews',asyncfunction(assert){
        assert.expect(17);

        constactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.step(JSON.stringify(args.domain));
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(1);

        assert.containsNone(actionManager,'.o_search_panel_filter_valueinput:checked');
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',4);

        //selectgoldfilter
        awaittestUtils.dom.click(actionManager.$('.o_search_panel_filterinput[type="checkbox"]:nth(0)'));
        assert.containsOnce(actionManager,'.o_search_panel_filter_valueinput:checked');
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',1);

        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsOnce(actionManager,'.o_search_panel_filter_valueinput:checked');
        assert.containsN(actionManager,'.o_data_row',1);

        //selectsilverfilter
        awaittestUtils.dom.click(actionManager.$('.o_search_panel_filterinput[type="checkbox"]:nth(1)'));
        assert.containsN(actionManager,'.o_search_panel_filter_valueinput:checked',2);
        assert.containsN(actionManager,'.o_data_row',4);

        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.containsN(actionManager,'.o_search_panel_filter_valueinput:checked',2);
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',4);

        awaittestUtils.dom.click(actionManager.$(".o_kanban_record:nth(0)"));
        awaittestUtils.dom.click(actionManager.$(".breadcrumb-item:nth(0)"));

        assert.verifySteps([
            '[]',//initialsearch_read
            '[["category_id","in",[6]]]',//kanban,afterselectingthegoldfilter
            '[["category_id","in",[6]]]',//list
            '[["category_id","in",[6,7]]]',//list,afterselectingthesilverfilter
            '[["category_id","in",[6,7]]]',//kanban
            '[["category_id","in",[6,7]]]',//kanban,afterswitchingbackfromformview
        ]);

        actionManager.destroy();
    });

    QUnit.test('searchpanelfiltersarekeptwhenswitchingtoaviewwithnosearchpanel',asyncfunction(assert){
        assert.expect(13);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        awaitactionManager.doAction(1);

        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_kanban_view');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_search_panel');
        assert.containsNone(actionManager,'.o_search_panel_filter_valueinput:checked');
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',4);

        //selectgoldfilter
        awaittestUtils.dom.click(actionManager.$('.o_search_panel_filterinput[type="checkbox"]:nth(0)'));
        assert.containsOnce(actionManager,'.o_search_panel_filter_valueinput:checked');
        assert.containsN(actionManager,'.o_kanban_record:not(.o_kanban_ghost)',1);

        //switchtopivot
        awaitcpHelpers.switchView(actionManager,'pivot');
        assert.containsOnce(actionManager,'.o_content.o_pivot');
        assert.containsNone(actionManager,'.o_content.o_search_panel');
        assert.strictEqual(actionManager.$('.o_pivot_cell_value').text(),'15');

        //switchtolist
        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_list_view');
        assert.containsOnce(actionManager,'.o_content.o_controller_with_searchpanel.o_search_panel');
        assert.containsOnce(actionManager,'.o_search_panel_filter_valueinput:checked');
        assert.containsN(actionManager,'.o_data_row',1);

        actionManager.destroy();
    });

    QUnit.test('afteronExecuteAction,selects"All"asdefaultcategoryvalue',asyncfunction(assert){
        assert.expect(4);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(2);
        awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton:contains("multiview")'));

        assert.containsOnce(actionManager,'.o_kanban_view');
        assert.containsOnce(actionManager,'.o_search_panel');
        assert.containsOnce(actionManager,'.o_search_panel_category_value:first.active');

        assert.verifySteps([]);//shouldnotcommunicatewithlocalStorage

        actionManager.destroy();
    });

    QUnit.test('searchpanelisnotinstantiatedifstatedincontext',asyncfunction(assert){
        assert.expect(2);

        this.actions[0].context={search_panel:false};
        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });

        awaitactionManager.doAction(2);
        awaittestUtils.dom.click(actionManager.$('.o_form_viewbutton:contains("multiview")'));

        assert.containsOnce(actionManager,'.o_kanban_view');
        assert.containsNone(actionManager,'.o_search_panel');

        actionManager.destroy();
    });

    QUnit.test('categoriesandfiltersarenotreloadedwhenswitchingbetweenviews',asyncfunction(assert){
        assert.expect(3);

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaitactionManager.doAction(1);

        awaitcpHelpers.switchView(actionManager,'list');
        awaitcpHelpers.switchView(actionManager,'kanban');

        assert.verifySteps([
            'search_panel_select_range',//kanban:categories
            'search_panel_select_multi_range',//kanban:filters
        ]);

        actionManager.destroy();
    });

    QUnit.test('scrollpositioniskeptwhenswitchingbetweencontrollers',asyncfunction(assert){
        assert.expect(6);

        constoriginalDebounce=SearchPanel.scrollDebounce;
        SearchPanel.scrollDebounce=0;

        for(vari=10;i<20;i++){
            this.data.category.records.push({id:i,name:"Cat"+i});
        }

        varactionManager=awaitcreateActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
        });
        actionManager.$el.css('max-height',300);

        asyncfunctionscroll(top){
            actionManager.el.querySelector(".o_search_panel").scrollTop=top;
            awaittestUtils.nextTick();
        }

        awaitactionManager.doAction(1);

        assert.containsOnce(actionManager,'.o_content.o_kanban_view');
        assert.strictEqual(actionManager.$('.o_search_panel').scrollTop(),0);

        //simulateascrollinthesearchpanelandswitchintolist
        awaitscroll(50);
        awaitcpHelpers.switchView(actionManager,'list');
        assert.containsOnce(actionManager,'.o_content.o_list_view');
        assert.strictEqual(actionManager.$('.o_search_panel').scrollTop(),50);

        //simulateanotherscrollandswitchbacktokanban
        awaitscroll(30);
        awaitcpHelpers.switchView(actionManager,'kanban');
        assert.containsOnce(actionManager,'.o_content.o_kanban_view');
        assert.strictEqual(actionManager.$('.o_search_panel').scrollTop(),30);

        actionManager.destroy();
        SearchPanel.scrollDebounce=originalDebounce;
    });

    QUnit.test('searchpanelisnotinstantiatedindialogs',asyncfunction(assert){
        assert.expect(2);

        this.data.company.records=[
            {id:1,name:'Company1'},
            {id:2,name:'Company2'},
            {id:3,name:'Company3'},
            {id:4,name:'Company4'},
            {id:5,name:'Company5'},
            {id:6,name:'Company6'},
            {id:7,name:'Company7'},
            {id:8,name:'Company8'},
        ];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="company_id"/></form>',
            archs:{
                'company,false,list':'<tree><fieldname="name"/></tree>',
                'company,false,search':
                    `<search>
                        <fieldname="name"/>
                        <searchpanel>
                            <fieldname="category_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        awaittestUtils.fields.many2one.clickOpenDropdown('company_id');
        awaittestUtils.fields.many2one.clickItem('company_id','SearchMore');

        assert.containsOnce(document.body,'.modal.o_list_view');
        assert.containsNone(document.body,'.modal.o_search_panel');

        form.destroy();
    });


    QUnit.test("Reloadcategorieswithcounterswhenfiltervaluesareselected",asyncfunction(assert){
        assert.expect(8);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="category_id"enable_counters="1"/>
                            <fieldname="state"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.verifySteps([
            'search_panel_select_range',
            "search_panel_select_multi_range",
        ]);

        assert.deepEqual(getCounters(kanban),[
            1,3,//categorycounts(inorder)
            1,1,2//filtercounts
        ]);

        awaittestUtils.dom.click(kanban.el.querySelector('.o_search_panel_filter_valueinput'));

        assert.deepEqual(getCounters(kanban),[
            1,//categorycounts(forsilver:0isnotdisplayed)
            1,1,2//filtercounts
        ]);

        assert.verifySteps([
            'search_panel_select_range',
            "search_panel_select_multi_range",
        ]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectone,expand,hierarchize,counters",asyncfunction(assert){
        assert.expect(5);

        this.data.company.records.push({id:50,name:'agrobeurre',parent_id:5});
        this.data.company.records.push({id:51,name:'agrocrèmefraiche',parent_id:5});
        this.data.partner.records[1].company_id=50;
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',3);
        assert.containsOnce(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,1]);

        awaittoggleFold(kanban,"agrolait");

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',5);
        assert.deepEqual(getCounters(kanban),[2,1,1]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectone,noexpand,hierarchize,counters",asyncfunction(assert){
        assert.expect(5);

        this.data.company.records.push({id:50,name:'agrobeurre',parent_id:5});
        this.data.company.records.push({id:51,name:'agrocrèmefraiche',parent_id:5});
        this.data.partner.records[1].company_id=50;
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',3);
        assert.containsOnce(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,1]);

        awaittoggleFold(kanban,"agrolait");

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',4);
        assert.deepEqual(getCounters(kanban),[2,1,1]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectone,expand,nohierarchize,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:50,name:'agrobeurre',parent_id:5});
        this.data.company.records.push({id:51,name:'agrocrèmefraiche',parent_id:5});
        this.data.partner.records[1].company_id=50;
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"hierarchize="0"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',5);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,1,1]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectone,noexpand,nohierarchize,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:50,name:'agrobeurre',parent_id:5});
        this.data.company.records.push({id:51,name:'agrocrèmefraiche',parent_id:5});
        this.data.partner.records[1].company_id=50;
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"hierarchize="0"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',4);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,1,1]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectone,expand,hierarchize,nocounters",asyncfunction(assert){
        assert.expect(5);

        this.data.company.records.push({id:50,name:'agrobeurre',parent_id:5});
        this.data.company.records.push({id:51,name:'agrocrèmefraiche',parent_id:5});
        this.data.partner.records[1].company_id=50;
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',3);
        assert.containsOnce(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        awaittoggleFold(kanban,"agrolait");

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',5);
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectone,noexpand,hierarchize,nocounters",asyncfunction(assert){
        assert.expect(5);

        this.data.company.records.push({id:50,name:'agrobeurre',parent_id:5});
        this.data.company.records.push({id:51,name:'agrocrèmefraiche',parent_id:5});
        this.data.partner.records[1].company_id=50;
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',3);
        assert.containsOnce(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        awaittoggleFold(kanban,"agrolait");

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',4);
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectone,expand,nohierarchize,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:50,name:'agrobeurre',parent_id:5});
        this.data.company.records.push({id:51,name:'agrocrèmefraiche',parent_id:5});
        this.data.partner.records[1].company_id=50;
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"hierarchize="0"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',5);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectone,noexpand,nohierarchize,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:50,name:'agrobeurre',parent_id:5});
        this.data.company.records.push({id:51,name:'agrocrèmefraiche',parent_id:5});
        this.data.partner.records[1].company_id=50;
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"hierarchize="0"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',4);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectmulti,expand,groupby,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"groupby="category_id"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',5);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,2]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectmulti,noexpand,groupby,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"groupby="category_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',4);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,2]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectmulti,expand,nogroupby,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',3);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,2]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectmulti,noexpand,nogroupby,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',2);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,2]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectmulti,expand,groupby,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"groupby="category_id"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',5);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectmulti,noexpand,groupby,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"groupby="category_id"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',4);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectmulti,expand,nogroupby,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',3);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2one:selectmulti,noexpand,nogroupby,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',2);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2many:selectmulti,expand,groupby,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_ids"select="multi"groupby="category_id"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',5);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,1]);

        kanban.destroy();
    });

    QUnit.test("many2many:selectmulti,noexpand,groupby,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_ids"select="multi"groupby="category_id"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',4);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,1]);

        kanban.destroy();
    });

    QUnit.test("many2many:selectmulti,expand,nogroupby,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_ids"select="multi"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',3);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,1]);

        kanban.destroy();
    });

    QUnit.test("many2many:selectmulti,noexpand,nogroupby,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_ids"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',2);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[2,1]);

        kanban.destroy();
    });

    QUnit.test("many2many:selectmulti,expand,groupby,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_ids"select="multi"groupby="category_id"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',5);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2many:selectmulti,noexpand,groupby,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_ids"select="multi"groupby="category_id"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',4);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2many:selectmulti,expand,nogroupby,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_ids"select="multi"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',3);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("many2many:selectmulti,noexpand,nogroupby,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.company.records.push({id:666,name:"MordorInc.",category_id:6});
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_ids"select="multi"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',2);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("selection:selectone,expand,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',4);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[1,2]);

        kanban.destroy();
    });

    QUnit.test("selection:selectone,noexpand,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',3);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[1,2]);

        kanban.destroy();
    });

    QUnit.test("selection:selectone,expand,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',4);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("selection:selectone,noexpand,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_field.o_search_panel_category_value',3);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("selection:selectmulti,expand,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"select="multi"enable_counters="1"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',3);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[1,2]);

        kanban.destroy();
    });

    QUnit.test("selection:selectmulti,noexpand,counters",asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',2);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[1,2]);

        kanban.destroy();
    });

    QUnit.test("selection:selectmulti,expand,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"select="multi"expand="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',3);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    QUnit.test("selection:selectmulti,noexpand,nocounters",asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="state"select="multi"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',2);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[]);

        kanban.destroy();
    });

    //-------------------------------------------------------------------------
    //Modeldomainandcountdomaindistinction
    //-------------------------------------------------------------------------

    QUnit.test("selection:selectmulti,noexpand,counters,extra_domain",asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records.shift();
        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"/>
                            <fieldname="state"select="multi"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsN(kanban,'.o_search_panel_label',5);
        assert.containsNone(kanban,'.o_toggle_fold>i');
        assert.deepEqual(getCounters(kanban),[1,2]);

        awaittoggleFold(kanban,"asustek");

        assert.containsN(kanban,'.o_search_panel_label',5);
        assert.deepEqual(getCounters(kanban),[1]);

        kanban.destroy();
    });

    //-------------------------------------------------------------------------
    //Limit
    //-------------------------------------------------------------------------

    QUnit.test("reachedlimitforacategory",asyncfunction(assert){
        assert.expect(6);

        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"limit="2"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsOnce(kanban,'.o_search_panel_section');
        assert.containsOnce(kanban,'.o_search_panel_section_header');
        assert.strictEqual(kanban.el.querySelector('.o_search_panel_section_header').innerText,"COMPANY");
        assert.containsOnce(kanban,'sectiondiv.alert.alert-warning');
        assert.strictEqual(kanban.el.querySelector('sectiondiv.alert.alert-warning').innerText,"Toomanyitemstodisplay.");
        assert.containsNone(kanban,'.o_search_panel_category_value');

        kanban.destroy();
    });

    QUnit.test("reachedlimitforafilter",asyncfunction(assert){
        assert.expect(6);

        constkanban=awaitcreateView({
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="company_id"select="multi"limit="2"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:'partner',
            View:KanbanView,
        });

        assert.containsOnce(kanban,'.o_search_panel_section');
        assert.containsOnce(kanban,'.o_search_panel_section_header');
        assert.strictEqual(kanban.el.querySelector('.o_search_panel_section_header').innerText,"COMPANY");
        assert.containsOnce(kanban,'sectiondiv.alert.alert-warning');
        assert.strictEqual(kanban.el.querySelector('sectiondiv.alert.alert-warning').innerText,"Toomanyitemstodisplay.");
        assert.containsNone(kanban,'.o_search_panel_filter_value');

        kanban.destroy();
    });

    QUnit.test("aselectedvaluebecomminginvalidshouldnomoreimpacttheview",asyncfunction(assert){
        assert.expect(13);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="filter_on_def"string="DEF"domain="[('state','=','def')]"/>
                        <searchpanel>
                            <fieldname="state"enable_counters="1"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.verifySteps([
            'search_panel_select_range',
        ]);

        assert.containsN(kanban,'.o_kanban_recordspan',4);

        //select'ABC'insearchpanel
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.verifySteps([
            'search_panel_select_range',
        ]);

        assert.containsOnce(kanban,'.o_kanban_recordspan');
        assert.strictEqual(kanban.el.querySelector('.o_kanban_recordspan').innerText,'yop');

        //selectDEFinfiltermenu
        awaittestUtils.controlPanel.toggleFilterMenu(kanban);
        awaittestUtils.controlPanel.toggleMenuItem(kanban,'DEF');

        assert.verifySteps([
            'search_panel_select_range',
        ]);

        constfirstCategoryValue=kanban.el.querySelector('.o_search_panel_category_valueheader');
        assert.strictEqual(firstCategoryValue.innerText,'All');
        assert.hasClass(
            firstCategoryValue,'active',
            "thevalue'All'shouldbeselectedsinceABCisnolongeravalidvaluewithrespecttosearchdomain"
        );
        assert.containsOnce(kanban,'.o_kanban_recordspan');
        assert.strictEqual(kanban.el.querySelector('.o_kanban_recordspan').innerText,'blip');

        kanban.destroy();
    });

    QUnit.test("Categorieswithdefaultattributesshouldbeudpatedwhenexternaldomainchanges",asyncfunction(assert){
        assert.expect(8);

        constkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            mockRPC:function(route,args){
                if(args.method&&args.method.includes('search_panel_')){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div>
                                <fieldname="foo"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            archs:{
                'partner,false,search':`
                    <search>
                        <filtername="filter_on_def"string="DEF"domain="[('state','=','def')]"/>
                        <searchpanel>
                            <fieldname="state"/>
                        </searchpanel>
                    </search>`,
            },
        });

        assert.verifySteps([
            'search_panel_select_range',
        ]);
        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_valueheaderlabel')].map(el=>el.innerText),
            ['All','ABC','DEF','GHI']
        );

        //select'ABC'insearchpanel-->noneedtoupdatethecategoryvalue
        awaittestUtils.dom.click(kanban.$('.o_search_panel_category_value:nth(1)header'));

        assert.verifySteps([]);
        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_valueheaderlabel')].map(el=>el.innerText),
            ['All','ABC','DEF','GHI']
        );

        //selectDEFinfiltermenu-->theexternaldomainchanges-->thevaluesshouldbeupdated
        awaittestUtils.controlPanel.toggleFilterMenu(kanban);
        awaittestUtils.controlPanel.toggleMenuItem(kanban,'DEF');

        assert.verifySteps([
            'search_panel_select_range',
        ]);
        assert.deepEqual(
            [...kanban.el.querySelectorAll('.o_search_panel_category_valueheaderlabel')].map(el=>el.innerText),
            ['All','DEF']
        );

        kanban.destroy();
    });

    QUnit.test("Categorywithcountersandfilterwithdomain",asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            arch:'<tree><fieldname="foo"/></tree>',
            archs:{
                'partner,false,search':`
                    <search>
                        <searchpanel>
                            <fieldname="category_id"enable_counters="1"/>
                            <fieldname="company_id"select="multi"domain="[['category_id','=',category_id]]"/>
                        </searchpanel>
                    </search>`,
            },
            data:this.data,
            model:"partner",
            services:this.services,
            View:ListView,
        });

        assert.containsN(list,".o_data_row",4);
        assert.strictEqual(
            list.$(".o_search_panel_category_value").text().replace(/\s/g,""),
            "Allgoldsilver",
            "Categorycountersshouldbeemptyifafilterhasadomainattribute"
        );

        list.destroy();
    });
});
});
