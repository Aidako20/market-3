flectra.define('web.dropdown_menu_tests',function(require){
    "usestrict";

    constDropdownMenu=require('web.DropdownMenu');
    consttestUtils=require('web.test_utils');

    const{createComponent}=testUtils;

    QUnit.module('Components',{
        beforeEach:function(){
            this.items=[
                {
                    isActive:false,
                    description:'SomeItem',
                    id:1,
                    groupId:1,
                    groupNumber:1,
                    options:[
                        {description:"FirstOption",groupNumber:1,id:1},
                        {description:"SecondOption",groupNumber:2,id:2},
                    ],
                },{
                    isActive:true,
                    description:'SomeotherItem',
                    id:2,
                    groupId:2,
                    groupNumber:2,
                },
            ];
        },
    },function(){
        QUnit.module('DropdownMenu');

        QUnit.test('simplerenderingandbasicinteractions',asyncfunction(assert){
            assert.expect(8);

            constdropdown=awaitcreateComponent(DropdownMenu,{
                props:{
                    items:this.items,
                    title:"Dropdown",
                },
            });

            assert.strictEqual(dropdown.el.querySelector('button').innerText.trim(),"Dropdown");
            assert.containsNone(dropdown,'ul.o_dropdown_menu');

            awaittestUtils.dom.click(dropdown.el.querySelector('button'));

            assert.containsN(dropdown,'.dropdown-divider,.dropdown-item',3,
                'shouldhave3elementscountingthedivider');
            constitemEls=dropdown.el.querySelectorAll('.o_menu_item>.dropdown-item');
            assert.strictEqual(itemEls[0].innerText.trim(),'SomeItem');
            assert.doesNotHaveClass(itemEls[0],'selected');
            assert.hasClass(itemEls[1],'selected');

            constdropdownElements=dropdown.el.querySelectorAll('.o_menu_item*');
            for(constdropdownElofdropdownElements){
                awaittestUtils.dom.click(dropdownEl);
            }
            assert.containsOnce(dropdown,'ul.o_dropdown_menu',
                "Clickingonanyitemofthedropdownshouldnotcloseit");

            awaittestUtils.dom.click(document.body);

            assert.containsNone(dropdown,'ul.o_dropdown_menu',
                "Clickingoutsideofthedropdownshouldcloseit");

            dropdown.destroy();
        });

        QUnit.test('onlyonedropdownrenderingatsametime(owlvsbootstrapdropdown)',asyncfunction(assert){
            assert.expect(12);

            constbsDropdown=document.createElement('div');
            bsDropdown.innerHTML=`<divclass="dropdown">
                <buttonclass="btndropdown-toggle"type="button"
                        data-toggle="dropdown"aria-expanded="false">
                    BSDropdownbutton
                </button>
                <divclass="dropdown-menu">
                    <aclass="dropdown-item"href="#">BSAction</a>
                </div>
            </div>`;
            document.body.append(bsDropdown);

            constdropdown=awaitcreateComponent(DropdownMenu,{
                props:{
                    items:this.items,
                    title:"Dropdown",
                },
            });

            awaittestUtils.dom.click(dropdown.el.querySelector('button'));

            assert.hasClass(dropdown.el.querySelector('.dropdown-menu'),'show');
            assert.doesNotHaveClass(bsDropdown.querySelector('.dropdown-menu'),'show');

            assert.isVisible(dropdown.el.querySelector('.dropdown-menu'),
                "owldropdownmenushouldbevisible");
            assert.isNotVisible(bsDropdown.querySelector('.dropdown-menu'),
                "bsdropdownmenushouldnotbevisible");

            awaittestUtils.dom.click(bsDropdown.querySelector('.btn.dropdown-toggle'));

            assert.doesNotHaveClass(dropdown.el,'show');
            assert.containsNone(dropdown.el,'.dropdown-menu',
                "owldropdownmenushouldnotbesetinsidethedom");

            assert.hasClass(bsDropdown.querySelector('.dropdown-menu'),'show');
            assert.isVisible(bsDropdown.querySelector('.dropdown-menu'),
                "bsdropdownmenushouldbevisible");

            awaittestUtils.dom.click(document.body);

            assert.doesNotHaveClass(dropdown.el,'show');
            assert.containsNone(dropdown.el,'.dropdown-menu',
                "owldropdownmenushouldnotbesetinsidethedom");

            assert.doesNotHaveClass(bsDropdown.querySelector('.dropdown-menu'),'show');
            assert.isNotVisible(bsDropdown.querySelector('.dropdown-menu'),
                "bsdropdownmenushouldnotbevisible");

            bsDropdown.remove();
            dropdown.destroy();
        });

        QUnit.test('clickonanitemwithoutoptionsshouldtoggleit',asyncfunction(assert){
            assert.expect(7);

            deletethis.items[0].options;

            constdropdown=awaitcreateComponent(DropdownMenu,{
                props:{items:this.items},
                intercepts:{
                    'item-selected':function(ev){
                        assert.strictEqual(ev.detail.item.id,1);
                        this.state.items[0].isActive=!this.state.items[0].isActive;
                    },
                }
            });

            awaittestUtils.dom.click(dropdown.el.querySelector('button'));

            constfirstItemEl=dropdown.el.querySelector('.o_menu_item>a');
            assert.doesNotHaveClass(firstItemEl,'selected');
            awaittestUtils.dom.click(firstItemEl);
            assert.hasClass(firstItemEl,'selected');
            assert.isVisible(firstItemEl);
            awaittestUtils.dom.click(firstItemEl);
            assert.doesNotHaveClass(firstItemEl,'selected');
            assert.isVisible(firstItemEl);

            dropdown.destroy();
        });

        QUnit.test('clickonanitemshouldnotchangeurl',asyncfunction(assert){
            assert.expect(1);

            deletethis.items[0].options;

            constinitialHref=window.location.href;
            constdropdown=awaitcreateComponent(DropdownMenu,{
                props:{items:this.items},
            });

            awaittestUtils.dom.click(dropdown.el.querySelector('button'));
            awaittestUtils.dom.click(dropdown.el.querySelector('.o_menu_item>a'));
            assert.strictEqual(window.location.href,initialHref,
                "theurlshouldnothavechangedafteraclickonanitem");

            dropdown.destroy();
        });

        QUnit.test('optionsrendering',asyncfunction(assert){
            assert.expect(6);

            constdropdown=awaitcreateComponent(DropdownMenu,{
                props:{items:this.items},
            });

            awaittestUtils.dom.click(dropdown.el.querySelector('button'));
            assert.containsN(dropdown,'.dropdown-divider,.dropdown-item',3);

            constfirstItemEl=dropdown.el.querySelector('.o_menu_item>a');
            assert.hasClass(firstItemEl.querySelector('i'),'o_icon_rightfafa-caret-right');
            //openoptionsmenu
            awaittestUtils.dom.click(firstItemEl);
            assert.hasClass(firstItemEl.querySelector('i'),'o_icon_rightfafa-caret-down');
            assert.containsN(dropdown,'.dropdown-divider,.dropdown-item',6);

            //closeoptionsmenu
            awaittestUtils.dom.click(firstItemEl);
            assert.hasClass(firstItemEl.querySelector('i'),'o_icon_rightfafa-caret-right');
            assert.containsN(dropdown,'.dropdown-divider,.dropdown-item',3);

            dropdown.destroy();
        });

        QUnit.test('closemenuclosesalsosubmenus',asyncfunction(assert){
            assert.expect(2);

            constdropdown=awaitcreateComponent(DropdownMenu,{
                props:{items:this.items},
            });

            //opendropdownmenu
            awaittestUtils.dom.click(dropdown.el.querySelector('button'));
            //openoptionsmenuoffirstitem
            awaittestUtils.dom.click(dropdown.el.querySelector('.o_menu_itema'));

            assert.containsN(dropdown,'.dropdown-divider,.dropdown-item',6);
            awaittestUtils.dom.click(dropdown.el.querySelector('button'));

            awaittestUtils.dom.click(dropdown.el.querySelector('button'));
            assert.containsN(dropdown,'.dropdown-divider,.dropdown-item',3);

            dropdown.destroy();
        });

        QUnit.test('clickonanoptionshouldtriggertheevent"item_option_clicked"withappropriatedata',asyncfunction(assert){
            assert.expect(18);

            leteventNumber=0;
            constdropdown=awaitcreateComponent(DropdownMenu,{
                props:{items:this.items},
                intercepts:{
                    'item-selected':function(ev){
                        eventNumber++;
                        const{option}=ev.detail;
                        assert.strictEqual(ev.detail.item.id,1);
                        if(eventNumber===1){
                            assert.strictEqual(option.id,1);
                            this.state.items[0].isActive=true;
                            this.state.items[0].options[0].isActive=true;
                        }
                        if(eventNumber===2){
                            assert.strictEqual(option.id,2);
                            this.state.items[0].options[1].isActive=true;
                        }
                        if(eventNumber===3){
                            assert.strictEqual(option.id,1);
                            this.state.items[0].options[0].isActive=false;
                        }
                        if(eventNumber===4){
                            assert.strictEqual(option.id,2);
                            this.state.items[0].isActive=false;
                            this.state.items[0].options[1].isActive=false;
                        }
                    },
                }
            });

            //opendropdownmenu
            awaittestUtils.dom.click(dropdown.el.querySelector('button'));
            assert.containsN(dropdown,'.dropdown-divider,.o_menu_item',3);

            //openmenuoptionsoffirstitem
            awaittestUtils.dom.click(dropdown.el.querySelector('.o_menu_item>a'));
            letoptionELs=dropdown.el.querySelectorAll('.o_menu_item.o_item_option>a');

            //clickonfirstoption
            awaittestUtils.dom.click(optionELs[0]);
            assert.hasClass(dropdown.el.querySelector('.o_menu_item>a'),'selected');
            optionELs=dropdown.el.querySelectorAll('.o_menu_item.o_item_option>a');
            assert.hasClass(optionELs[0],'selected');
            assert.doesNotHaveClass(optionELs[1],'selected');

            //clickonsecondoption
            awaittestUtils.dom.click(optionELs[1]);
            assert.hasClass(dropdown.el.querySelector('.o_menu_item>a'),'selected');
            optionELs=dropdown.el.querySelectorAll('.o_menu_item.o_item_option>a');
            assert.hasClass(optionELs[0],'selected');
            assert.hasClass(optionELs[1],'selected');

            //clickagainonfirstoption
            awaittestUtils.dom.click(optionELs[0]);
            //clickagainonsecondoption
            awaittestUtils.dom.click(optionELs[1]);
            assert.doesNotHaveClass(dropdown.el.querySelector('.o_menu_item>a'),'selected');
            optionELs=dropdown.el.querySelectorAll('.o_menu_item.o_item_option>a');
            assert.doesNotHaveClass(optionELs[0],'selected');
            assert.doesNotHaveClass(optionELs[1],'selected');

            dropdown.destroy();
        });

        QUnit.test('keyboardnavigation',asyncfunction(assert){
            assert.expect(12);

            //Shorthandmethodtotriggeraspecifickeydown.
            //NotethatBootStraphandlessomeofthenavigationmoves(upanddown)
            //soweneedtogivetheeventtheproper"which"property.Wealsogive
            //itwhenit'snotrequiredtocheckifithasbeencorrectlyprevented.
            asyncfunctionnavigate(key,global){
                constwhich={
                    Enter:13,
                    Escape:27,
                    ArrowLeft:37,
                    ArrowUp:38,
                    ArrowRight:39,
                    ArrowDown:40,
                }[key];
                consttarget=global?document.body:document.activeElement;
                awaittestUtils.dom.triggerEvent(target,'keydown',{key,which});
                if(key==='Enter'){
                    //Pressing"Enter"onafocusedelementtriggersaclick(HTML5specs)
                    awaittestUtils.dom.click(target);
                }
            }

            constdropdown=awaitcreateComponent(DropdownMenu,{
                props:{items:this.items},
            });

            //Initializeactiveelement(startattogglebutton)
            dropdown.el.querySelector('button').focus();
            awaittestUtils.dom.click(dropdown.el.querySelector('button'));

            awaitnavigate('ArrowDown');//Gotonextitem

            assert.strictEqual(document.activeElement,dropdown.el.querySelector('.o_menu_itema'));
            assert.containsNone(dropdown,'.o_item_option');

            awaitnavigate('ArrowRight');//Unfoldfirstitem'soptions(w/Right)

            assert.strictEqual(document.activeElement,dropdown.el.querySelector('.o_menu_itema'));
            assert.containsN(dropdown,'.o_item_option',2);

            awaitnavigate('ArrowDown');//Gotonextoption

            assert.strictEqual(document.activeElement,dropdown.el.querySelector('.o_item_optiona'));

            awaitnavigate('ArrowLeft');//Foldfirstitem'soptions(w/Left)

            assert.strictEqual(document.activeElement,dropdown.el.querySelector('.o_menu_itema'));
            assert.containsNone(dropdown,'.o_item_option');

            awaitnavigate('Enter');//Unfoldfirstitem'soptions(w/Enter)

            assert.strictEqual(document.activeElement,dropdown.el.querySelector('.o_menu_itema'));
            assert.containsN(dropdown,'.o_item_option',2);

            awaitnavigate('ArrowDown');//Gotonextoption
            awaitnavigate('Escape');//Foldfirstitem'soptions(w/Escape)
            awaittestUtils.nextTick();

            assert.strictEqual(dropdown.el.querySelector('.o_menu_itema'),document.activeElement);
            assert.containsNone(dropdown,'.o_item_option');

            awaitnavigate('Escape',true);//Closethedropdown

            assert.containsNone(dropdown,'ul.o_dropdown_menu',"Dropdownshouldbefolded");

            dropdown.destroy();
        });

        QUnit.test('interactionsbetweenmultipledropdowns',asyncfunction(assert){
            assert.expect(7);

            constprops={items:this.items};
            classParentextendsowl.Component{
                constructor(){
                    super(...arguments);
                    this.state=owl.useState(props);
                }
            }
            Parent.components={DropdownMenu};
            Parent.template=owl.tags.xml`
                <div>
                    <DropdownMenuclass="first"title="'First'"items="state.items"/>
                    <DropdownMenuclass="second"title="'Second'"items="state.items"/>
                </div>`;
            constparent=newParent();
            awaitparent.mount(testUtils.prepareTarget(),{position:'first-child'});

            const[menu1,menu2]=parent.el.querySelectorAll('.o_dropdown');

            assert.containsNone(parent,'.o_dropdown_menu');

            awaittestUtils.dom.click(menu1.querySelector('button'));

            assert.containsOnce(parent,'.o_dropdown_menu');
            assert.containsOnce(parent,'.o_dropdown.first.o_dropdown_menu');

            awaittestUtils.dom.click(menu2.querySelector('button'));

            assert.containsOnce(parent,'.o_dropdown_menu');
            assert.containsOnce(parent,'.o_dropdown.second.o_dropdown_menu');

            awaittestUtils.dom.click(menu2.querySelector('.o_menu_itema'));
            awaittestUtils.dom.click(menu1.querySelector('button'));

            assert.containsOnce(parent,'.o_dropdown_menu');
            assert.containsOnce(parent,'.o_dropdown.first.o_dropdown_menu');

            parent.destroy();
        });

        QUnit.test("dropdowndoesn'tgetcloseonmousedowninsideandmouseupoutsidedropdown",asyncfunction(assert){
            //Inthistest,wesimulateacasewheretheuserclicksinsideadropdownmenuitem
            //(e.g.intheinputofthe'Savecurrentsearch'itemintheFavoritesmenu),keeps
            //theclickpressed,movesthecursoroutsidethedropdownandreleasestheclick
            //(i.e.mousedownandfocusinsidetheitem,mouseupandclickoutsidethedropdown).
            //Inthiscase,wewanttokeepthedropdownmenuopen.
            assert.expect(5);

            constitems=this.items;
            classParentextendsowl.Component{
                constructor(){
                    super(...arguments);
                    this.items=items;
                }
            }
            Parent.components={DropdownMenu};
            Parent.template=owl.tags.xml`
                <div>
                    <DropdownMenuclass="first"title="'First'"items="items"/>
                </div>`;
            constparent=newParent();
            awaitparent.mount(testUtils.prepareTarget(),{position:"first-child"});

            constmenu=parent.el.querySelector(".o_dropdown");
            assert.doesNotHaveClass(menu,"show","dropdownshouldnotbeopen");

            awaittestUtils.dom.click(menu.querySelector("button"));
            assert.hasClass(menu,"show","dropdownshouldbeopen");

            constfirstItemEl=menu.querySelector(".o_menu_item>a");
            //openoptionsmenu
            awaittestUtils.dom.click(firstItemEl);
            assert.hasClass(firstItemEl.querySelector("i"),"o_icon_rightfafa-caret-down");

            //forcethefocusinsidethedropdownitemandclickoutside
            firstItemEl.parentElement.querySelector(".o_menu_item_options.o_item_optiona").focus();
            awaittestUtils.dom.triggerEvents(parent.el,"click");
            assert.hasClass(menu,"show","dropdownshouldstillbeopen");
            assert.hasClass(firstItemEl.querySelector("i"),"o_icon_rightfafa-caret-down");

            parent.destroy();
        });
    });
});
