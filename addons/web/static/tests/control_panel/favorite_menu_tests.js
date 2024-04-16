flectra.define('web.favorite_menu_tests',function(require){
    "usestrict";

    constFormView=require('web.FormView');
    consttestUtils=require('web.test_utils');

    constcpHelpers=testUtils.controlPanel;
    const{createControlPanel,createView,mock}=testUtils;
    const{patchDate}=mock;

    constsearchMenuTypes=['favorite'];

    QUnit.module('Components',{
        beforeEach:function(){
            this.fields={
                bar:{string:"Bar",type:"many2one",relation:'partner'},
                birthday:{string:"Birthday",type:"date",store:true,sortable:true},
                date_field:{string:"Date",type:"date",store:true,sortable:true},
                float_field:{string:"Float",type:"float",group_operator:'sum'},
                foo:{string:"Foo",type:"char",store:true,sortable:true},
            };
        },
    },function(){

        QUnit.module('FavoriteMenu');

        QUnit.test('simplerenderingwithnofavorite',asyncfunction(assert){
            assert.expect(8);

            constparams={
                cpModelConfig:{searchMenuTypes},
                cpProps:{fields:this.fields,searchMenuTypes,action:{name:"ActionName"}},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.containsOnce(controlPanel,'div.o_favorite_menu>buttoni.fa.fa-star');
            assert.strictEqual(controlPanel.el.querySelector('div.o_favorite_menu>buttonspan').innerText.trim(),"Favorites");

            awaitcpHelpers.toggleFavoriteMenu(controlPanel);
            assert.containsNone(controlPanel,'.dropdown-divider');
            assert.containsOnce(controlPanel,'.o_add_favorite');
            assert.strictEqual(controlPanel.el.querySelector('.o_add_favorite>button').innerText.trim(),
                "Savecurrentsearch");

            awaitcpHelpers.toggleSaveFavorite(controlPanel);
            assert.strictEqual(
                controlPanel.el.querySelector('.o_add_favoriteinput[type="text"]').value,
                'ActionName'
            );
            assert.containsN(controlPanel,'.o_add_favorite.custom-checkboxinput[type="checkbox"]',2);
            constlabelEls=controlPanel.el.querySelectorAll('.o_add_favorite.custom-checkboxlabel');
            assert.deepEqual(
                [...labelEls].map(e=>e.innerText.trim()),
                ["Usebydefault","Sharewithallusers"]
            );

            controlPanel.destroy();
        });

        QUnit.test('favoritesusebydefaultandshareareexclusive',asyncfunction(assert){
            assert.expect(11);

            constparams={
                cpModelConfig:{
                    viewInfo:{fields:this.fields},
                    searchMenuTypes
                },
                cpProps:{
                    fields:this.fields,
                    searchMenuTypes,
                    action:{},
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFavoriteMenu(controlPanel);
            awaitcpHelpers.toggleSaveFavorite(controlPanel);
            constcheckboxes=controlPanel.el.querySelectorAll('input[type="checkbox"]');

            assert.strictEqual(checkboxes.length,2,'2checkboxesarepresent');

            assert.notOk(checkboxes[0].checked,'Start:Noneofthecheckboxesarechecked(1)');
            assert.notOk(checkboxes[1].checked,'Start:Noneofthecheckboxesarechecked(2)');

            awaittestUtils.dom.click(checkboxes[0]);
            assert.ok(checkboxes[0].checked,'Thefirstcheckboxischecked');
            assert.notOk(checkboxes[1].checked,'Thesecondcheckboxisnotchecked');

            awaittestUtils.dom.click(checkboxes[1]);
            assert.notOk(checkboxes[0].checked,
                'Clickingonthesecondcheckboxchecksit,andunchecksthefirst(1)');
            assert.ok(checkboxes[1].checked,
                'Clickingonthesecondcheckboxchecksit,andunchecksthefirst(2)');

            awaittestUtils.dom.click(checkboxes[0]);
            assert.ok(checkboxes[0].checked,
                'Clickingonthefirstcheckboxchecksit,andunchecksthesecond(1)');
            assert.notOk(checkboxes[1].checked,
                'Clickingonthefirstcheckboxchecksit,andunchecksthesecond(2)');

            awaittestUtils.dom.click(checkboxes[0]);
            assert.notOk(checkboxes[0].checked,'End:Noneofthecheckboxesarechecked(1)');
            assert.notOk(checkboxes[1].checked,'End:Noneofthecheckboxesarechecked(2)');

            controlPanel.destroy();
        });

        QUnit.test('savefilter',asyncfunction(assert){
            assert.expect(1);

            constparams={
                cpModelConfig:{
                    fields:this.fields,
                    searchMenuTypes
                },
                cpProps:{
                    fields:this.fields,
                    searchMenuTypes,
                    action:{},
                },
                'get-controller-query-params':function(callback){
                    callback({
                        orderedBy:[
                            {asc:true,name:'foo'},
                            {asc:false,name:'bar'}
                        ]
                    });
                },
                env:{
                    dataManager:{
                        create_filter:asyncfunction(filter){
                            assert.strictEqual(filter.sort,'["foo","bardesc"]',
                                'Therightformatforthestring"sort"shouldbesenttotheserver'
                            );
                        }
                    }
                },
            };

            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFavoriteMenu(controlPanel);
            awaitcpHelpers.toggleSaveFavorite(controlPanel);
            awaitcpHelpers.editFavoriteName(controlPanel,"aaa");
            awaitcpHelpers.saveFavorite(controlPanel);

            controlPanel.destroy();
        });

        QUnit.test('dynamicfiltersaresaveddynamic',asyncfunction(assert){
            assert.expect(3);

            constarch=`
            <search>
                <filterstring="Float"name="positive"domain="[('date_field','>=',(context_today()+relativedelta()).strftime('%Y-%m-%d'))]"/>
            </search>
        `;
            constparams={
                cpModelConfig:{
                    fields:{},
                    arch,
                    searchMenuTypes,
                    context:{
                        search_default_positive:true,
                    }
                },
                cpProps:{
                    fields:{},
                    searchMenuTypes,
                    action:{},
                },
                'get-controller-query-params':function(callback){
                    callback();
                },
                env:{
                    dataManager:{
                        create_filter:asyncfunction(filter){
                            assert.strictEqual(
                                filter.domain,
                                "[(\"date_field\",\">=\",(context_today()+relativedelta()).strftime(\"%Y-%m-%d\"))]"
                            );
                            return1;//serverSideId
                        }
                    }
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),['Float']);

            awaitcpHelpers.toggleFavoriteMenu(controlPanel);
            awaitcpHelpers.toggleSaveFavorite(controlPanel);
            awaitcpHelpers.editFavoriteName(controlPanel,"Myfavorite");
            awaitcpHelpers.saveFavorite(controlPanel);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),["Myfavorite"]);

            controlPanel.destroy();
        });

        QUnit.test('savefilterscreatedviaautocompletionworks',asyncfunction(assert){
            assert.expect(4);

            constarch=`<search><fieldname="foo"/></search>`;
            constparams={
                cpModelConfig:{
                    fields:this.fields,
                    arch,
                    searchMenuTypes,
                },
                cpProps:{
                    fields:this.fields,
                    searchMenuTypes,
                    action:{},
                },
                'get-controller-query-params':function(callback){
                    callback();
                },
                env:{
                    dataManager:{
                        create_filter:asyncfunction(filter){
                            assert.strictEqual(
                                filter.domain,
                                `[["foo","ilike","a"]]`
                            );
                            return1;//serverSideId
                        }
                    }
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);

            awaitcpHelpers.editSearch(controlPanel,"a");
            awaitcpHelpers.validateSearch(controlPanel);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),["Foo\na"]);

            awaitcpHelpers.toggleFavoriteMenu(controlPanel);
            awaitcpHelpers.toggleSaveFavorite(controlPanel);
            awaitcpHelpers.editFavoriteName(controlPanel,"Myfavorite");
            awaitcpHelpers.saveFavorite(controlPanel);

            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),["Myfavorite"]);

            controlPanel.destroy();
        });

        QUnit.test('deleteanactivefavoriteremoveitbothinlistoffavoriteandinsearchbar',asyncfunction(assert){
            assert.expect(6);

            constfavoriteFilters=[{
                context:"{}",
                domain:"[['foo','=','qsdf']]",
                id:7,
                is_default:true,
                name:"Myfavorite",
                sort:"[]",
                user_id:[2,"MitchellAdmin"],
            }];
            constparams={
                cpModelConfig:{favoriteFilters,searchMenuTypes},
                cpProps:{searchMenuTypes,action:{}},
                search:function(searchQuery){
                    const{domain}=searchQuery;
                    assert.deepEqual(domain,[]);
                },
                env:{
                    dataManager:{
                        delete_filter:function(){
                            returnPromise.resolve();
                        }
                    }
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFavoriteMenu(controlPanel);

            const{domain}=controlPanel.getQuery();
            assert.deepEqual(domain,[["foo","=","qsdf"]]);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),["Myfavorite"]);
            assert.hasClass(controlPanel.el.querySelector('.o_favorite_menu.o_menu_item>a'),'selected');

            awaitcpHelpers.deleteFavorite(controlPanel,0);

            //confirmdeletion
            awaittestUtils.dom.click(document.querySelector('div.o_dialogfooterbutton'));
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);
            constitemEls=controlPanel.el.querySelectorAll('.o_favorite_menu.o_menu_item');
            assert.deepEqual([...itemEls].map(e=>e.innerText.trim()),["Savecurrentsearch"]);

            controlPanel.destroy();
        });

        QUnit.test('defaultfavoriteisnotactivatedifkeysearch_disable_custom_filtersissettotrue',asyncfunction(assert){
            assert.expect(2);

            constfavoriteFilters=[{
                context:"{}",
                domain:"",
                id:7,
                is_default:true,
                name:"Myfavorite",
                sort:"[]",
                user_id:[2,"MitchellAdmin"],
            }];
            constparams={
                cpModelConfig:{
                    favoriteFilters,
                    searchMenuTypes,
                    context:{search_disable_custom_filters:true}
                },
                cpProps:{searchMenuTypes,action:{}},
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFavoriteMenu(controlPanel);

            const{domain}=controlPanel.getQuery();
            assert.deepEqual(domain,[]);
            assert.deepEqual(cpHelpers.getFacetTexts(controlPanel),[]);

            controlPanel.destroy();
        });

        QUnit.test('togglefavoritecorrectlyclearsfilter,groupbys,comparisonandfield"options"',asyncfunction(assert){
            assert.expect(11);

            constunpatchDate=patchDate(2019,6,31,13,43,0);

            constfavoriteFilters=[{
                context:`
                    {
                        "group_by":["foo"],
                        "comparison":{
                            "favoritecomparisoncontent":"blabla..."
                        },
                    }
                `,
                domain:"['!',['foo','=','qsdf']]",
                id:7,
                is_default:false,
                name:"Myfavorite",
                sort:"[]",
                user_id:[2,"MitchellAdmin"],
            }];
            letfirstSearch=true;
            constarch=`
            <search>
                <fieldstring="Foo"name="foo"/>
                <filterstring="DateFieldFilter"name="positive"date="date_field"default_period="this_year"/>
                <filterstring="DateFieldGroupby"name="coolName"context="{'group_by':'date_field'}"/>
            </search>
        `;
            constsearchMenuTypes=['filter','groupBy','comparison','favorite'];
            constparams={
                cpModelConfig:{
                    favoriteFilters,
                    arch,
                    fields:this.fields,
                    searchMenuTypes,
                    context:{
                        search_default_positive:true,
                        search_default_coolName:true,
                        search_default_foo:"a",
                    }
                },
                cpProps:{searchMenuTypes,action:{},fields:this.fields},
                search:function(searchQuery){
                    const{domain,groupBy,timeRanges}=searchQuery;
                    if(firstSearch){
                        assert.deepEqual(domain,[['foo','ilike','a']]);
                        assert.deepEqual(groupBy,['date_field:month']);
                        assert.deepEqual(timeRanges,{
                            comparisonId:"previous_period",
                            comparisonRange:["&",["date_field",">=","2018-01-01"],["date_field","<=","2018-12-31"]],
                            comparisonRangeDescription:"2018",
                            fieldDescription:"DateFieldFilter",
                            fieldName:"date_field",
                            range:["&",["date_field",">=","2019-01-01"],["date_field","<=","2019-12-31"]],
                            rangeDescription:"2019",
                        });
                        firstSearch=false;
                    }else{
                        assert.deepEqual(domain,['!',['foo','=','qsdf']]);
                        assert.deepEqual(groupBy,['foo']);
                        assert.deepEqual(timeRanges,{
                            "favoritecomparisoncontent":"blabla...",
                            range:undefined,
                            comparisonRange:undefined,
                        });
                    }
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            const{domain,groupBy,timeRanges}=controlPanel.getQuery();
            assert.deepEqual(domain,[
                "&",
                ["foo","ilike","a"],
                "&",
                ["date_field",">=","2019-01-01"],
                ["date_field","<=","2019-12-31"]
            ]);
            assert.deepEqual(groupBy,['date_field:month']);
            assert.deepEqual(timeRanges,{});

            assert.deepEqual(
                cpHelpers.getFacetTexts(controlPanel),
                [
                    'Foo\na',
                    'DateFieldFilter:2019',
                    'DateFieldGroupby:Month',
                ]
                );

            //activateacomparison
            awaitcpHelpers.toggleComparisonMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,"DateFieldFilter:Previousperiod");

            //activatetheuniqueexistingfavorite
            awaitcpHelpers.toggleFavoriteMenu(controlPanel);
            awaitcpHelpers.toggleMenuItem(controlPanel,0);

            assert.deepEqual(
                cpHelpers.getFacetTexts(controlPanel),
                ["Myfavorite"]
            );

            controlPanel.destroy();
            unpatchDate();
        });

        QUnit.test('favoriteshaveuniquedescriptions(thesubmenusofthefavoritemenuarecorrectlyupdated)',asyncfunction(assert){
            assert.expect(3);

            constfavoriteFilters=[{
                context:"{}",
                domain:"[]",
                id:1,
                is_default:false,
                name:"Myfavorite",
                sort:"[]",
                user_id:[2,"MitchellAdmin"],
            }];
            constparams={
                cpModelConfig:{favoriteFilters,searchMenuTypes},
                cpProps:{searchMenuTypes,action:{}},
                'get-controller-query-params':function(callback){
                    callback();
                },
                env:{
                    session:{uid:4},
                    services:{
                        notification:{
                            notify:function(params){
                                assert.deepEqual(params,{
                                    message:"Filterwithsamenamealreadyexists.",
                                    type:"danger"
                                });
                            },
                        }
                    },
                    dataManager:{
                        create_filter:asyncfunction(irFilter){
                            assert.deepEqual(irFilter,{
                                "action_id":undefined,
                                "context":{"group_by":[]},
                                "domain":"[]",
                                "is_default":false,
                                "model_id":undefined,
                                "name":"Myfavorite2",
                                "sort":"[]",
                                "user_id":4,
                            });
                            return2;//serverSideId
                        }
                    }
                },
            };
            constcontrolPanel=awaitcreateControlPanel(params);

            awaitcpHelpers.toggleFavoriteMenu(controlPanel);
            awaitcpHelpers.toggleSaveFavorite(controlPanel);

            //firsttry:shouldfail
            awaitcpHelpers.editFavoriteName(controlPanel,"Myfavorite");
            awaitcpHelpers.saveFavorite(controlPanel);

            //secondtry:shouldsucceed
            awaitcpHelpers.editFavoriteName(controlPanel,"Myfavorite2");
            awaitcpHelpers.saveFavorite(controlPanel);
            awaitcpHelpers.toggleSaveFavorite(controlPanel);

            //thirdtry:shouldfail
            awaitcpHelpers.editFavoriteName(controlPanel,"Myfavorite2");
            awaitcpHelpers.saveFavorite(controlPanel);

            controlPanel.destroy();
        });

        QUnit.test('savesearchfilterinmodal',asyncfunction(assert){
            assert.expect(5);
            constdata={
                partner:{
                    fields:{
                        date_field:{string:"Date",type:"date",store:true,sortable:true,searchable:true},
                        birthday:{string:"Birthday",type:"date",store:true,sortable:true},
                        foo:{string:"Foo",type:"char",store:true,sortable:true},
                        bar:{string:"Bar",type:"many2one",relation:'partner'},
                        float_field:{string:"Float",type:"float",group_operator:'sum'},
                    },
                    records:[
                        {id:1,display_name:"Firstrecord",foo:"yop",bar:2,date_field:"2017-01-25",birthday:"1983-07-15",float_field:1},
                        {id:2,display_name:"Secondrecord",foo:"blip",bar:1,date_field:"2017-01-24",birthday:"1982-06-04",float_field:2},
                        {id:3,display_name:"Thirdrecord",foo:"gnap",bar:1,date_field:"2017-01-13",birthday:"1985-09-13",float_field:1.618},
                        {id:4,display_name:"Fourthrecord",foo:"plop",bar:2,date_field:"2017-02-25",birthday:"1983-05-05",float_field:-1},
                        {id:5,display_name:"Fifthrecord",foo:"zoup",bar:2,date_field:"2016-01-25",birthday:"1800-01-01",float_field:13},
                        {id:7,display_name:"Partner6",},
                        {id:8,display_name:"Partner7",},
                        {id:9,display_name:"Partner8",},
                        {id:10,display_name:"Partner9",}
                    ],
                },
            };
            constform=awaitcreateView({
                arch:`
                <formstring="Partners">
                    <sheet>
                        <group>
                            <fieldname="bar"/>
                        </group>
                    </sheet>
                </form>`,
                archs:{
                    'partner,false,list':'<tree><fieldname="display_name"/></tree>',
                    'partner,false,search':'<search><fieldname="date_field"/></search>',
                },
                data,
                model:'partner',
                res_id:1,
                View:FormView,
                env:{
                    dataManager:{
                        create_filter(filter){
                            assert.strictEqual(filter.name,"AwesomeTestCustomerFilter",
                                "filternameshouldbecorrect");
                        },
                    }
                },
            });

            awaittestUtils.form.clickEdit(form);

            awaittestUtils.fields.many2one.clickOpenDropdown('bar');
            awaittestUtils.fields.many2one.clickItem('bar','Search');

            assert.containsN(document.body,'tr.o_data_row',9,"shoulddisplay9records");

            awaitcpHelpers.toggleFilterMenu('.modal');
            awaitcpHelpers.toggleAddCustomFilter('.modal');
            assert.strictEqual(document.querySelector('.o_filter_conditionselect.o_generator_menu_field').value,
                'date_field',
                "datefieldshouldbeselected");
            awaitcpHelpers.applyFilter('.modal');

            assert.containsNone(document.body,'tr.o_data_row',"shoulddisplay0records");

            //Savethissearch
            awaitcpHelpers.toggleFavoriteMenu('.modal');
            awaitcpHelpers.toggleSaveFavorite('.modal');

            constfilterNameInput=document.querySelector('.o_add_favoriteinput[type="text"]');
            assert.isVisible(filterNameInput,"shoulddisplayaninputfieldforthefiltername");

            awaittestUtils.fields.editInput(filterNameInput,'AwesomeTestCustomerFilter');
            awaittestUtils.dom.click(document.querySelector('.o_add_favoritebutton.btn-primary'));

            form.destroy();
        });

        QUnit.test('modalloadssavedsearchfilters',asyncfunction(assert){
            assert.expect(1);
            constdata={
                partner:{
                    fields:{
                        bar:{string:"Bar",type:"many2one",relation:'partner'},
                    },
                    //10recordssothattheSearchbuttonshows
                    records:Array.apply(null,Array(10)).map(function(_,i){
                        return{id:i,display_name:"Record"+i,bar:1};
                    })
                },
            };
            constform=awaitcreateView({
                arch:`
                <formstring="Partners">
                    <sheet>
                        <group>
                            <fieldname="bar"/>
                        </group>
                    </sheet>
                </form>`,
                data,
                model:'partner',
                res_id:1,
                View:FormView,
                interceptsPropagate:{
                    load_views:function(ev){
                        assert.ok(ev.data.options.load_filters,"openingdialogshouldloadthefilters");
                    },
                },
            });

            awaittestUtils.form.clickEdit(form);

            awaittestUtils.fields.many2one.clickOpenDropdown('bar');
            awaittestUtils.fields.many2one.clickItem('bar','Search');

            form.destroy();
        });
    });
});
