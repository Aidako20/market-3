flectra.define('web.popover_tests',function(require){
    'usestrict';

    constmakeTestEnvironment=require('web.test_env');
    constPopover=require('web.Popover');
    consttestUtils=require('web.test_utils');

    const{Component,tags,hooks}=owl;
    const{useRef,useState}=hooks;
    const{xml}=tags;

    QUnit.module('core',{},function(){
        QUnit.module('Popover');

        QUnit.test('Basicrendering&props',asyncfunction(assert){
            assert.expect(11);

            classSubComponentextendsComponent{}
            SubComponent.template=xml`
                <divclass="o_subcomponent"style="width:280px;"t-esc="props.text"/>
            `;

            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.state=useState({
                        position:'right',
                        title:'👋',
                        textContent:'sup',
                    });
                    this.popoverRef=useRef('popoverRef');
                }
            }
            //PopovershouldbeincludedasagloballyavailableComponent
            Parent.components={SubComponent};
            Parent.env=makeTestEnvironment();
            Parent.template=xml`
                <div>
                    <buttonid="passiveTarget">🚫</button>
                    <Popovert-ref="popoverRef"
                        position="state.position"
                        title="state.title"
                        >
                        <tt-set="opened">
                            <SubComponenttext="state.textContent"/>
                        </t>
                        <buttonid="target">
                            Noticeme,senpai👀
                        </button>
                    </Popover>
                </div>`;

            constparent=newParent();
            constfixture=testUtils.prepareTarget();
            /**
             *Thecomponentbeingtestedbehavesdifferentlybasedonits
             *visibility(ornot)intheviewport.Thequnitfixturehastobe
             *intheviewportfortheseteststobemeaningful.
             */
            fixture.style.top='300px';
            fixture.style.left='150px';
            fixture.style.width='300px';

            //Helperfunctions
            asyncfunctionchangeProps(key,value){
                parent.state[key]=value;
                awaittestUtils.nextTick();
            }
            functionpointsTo(popover,element,position){
                consthasCorrectClass=popover.classList.contains(
                    `o_popover--${position}`
                );
                constexpectedPosition=Popover.computePositioningData(
                    popover,
                    element
                )[position];
                constcorrectLeft=
                    parseFloat(popover.style.left)===
                    Math.round(expectedPosition.left*100)/100;
                constcorrectTop=
                    parseFloat(popover.style.top)===
                    Math.round(expectedPosition.top*100)/100;
                returnhasCorrectClass&&correctLeft&&correctTop;
            }

            awaitparent.mount(fixture);
            constbody=document.querySelector('body');
            letpopover,title;
            //Show/hide
            assert.containsNone(body,'.o_popover');
            awaittestUtils.dom.click('#target');
            assert.containsOnce(body,'.o_popover');
            assert.containsOnce(body,'.o_subcomponent');
            assert.containsOnce(body,'.o_popover--right');
            awaittestUtils.dom.click('#passiveTarget');
            assert.containsNone(body,'.o_popover');
            //Reactivityoftitle
            awaittestUtils.dom.click('#target');
            popover=document.querySelector('.o_popover');
            title=popover.querySelector('.o_popover_header').innerText.trim();
            assert.strictEqual(title,'👋');
            awaitchangeProps('title','🤔');
            title=popover.querySelector('.o_popover_header').innerText.trim();
            assert.strictEqual(
                title,
                '🤔',
                'Thetitleofthepopovershouldhavechanged.'
            );
            //Positionandtargetreactivity
            constelement=parent.popoverRef.el;
            assert.ok(
                pointsTo(
                    document.querySelector('.o_popover'),
                    element,
                    parent.state.position
                ),
                'Popovershouldbevisuallyalignedwithitstarget'
            );
            awaitchangeProps('position','bottom');
            assert.ok(
                pointsTo(
                    document.querySelector('.o_popover'),
                    element,
                    parent.state.position
                ),
                'Popovershouldbebottomedpositioned'
            );
            //Reactivityofsubcomponents
            awaitchangeProps('textContent','wassup');
            assert.strictEqual(
                popover.querySelector('.o_subcomponent').innerText.trim(),
                'wassup',
                'Subcomponentshouldmatchwithitsgiventext'
            );
            awaittestUtils.dom.click('#passiveTarget');
            //Requestedpositionnotfitting
            awaitchangeProps('position','left');
            awaittestUtils.dom.click('#target');
            assert.ok(
                pointsTo(document.querySelector('.o_popover'),element,'right'),
                "Popovershouldberight-positionedbecauseitdoesn'tfitleft"
            );
            awaittestUtils.dom.click('#passiveTarget');
            parent.destroy();
        });

        QUnit.test('Multiplepopovers',asyncfunction(assert){
            assert.expect(9);

            classParentextendsComponent{}
            Parent.components={Popover};
            Parent.env=makeTestEnvironment();
            Parent.template=xml`
                <div>
                    <Popover>
                        <buttonid="firstTarget">👋</button>
                        <tt-set="opened">
                            <pid="firstContent">firstpopover</p>
                        </t>
                    </Popover>
                    <br/>
                    <Popover>
                        <buttonid="secondTarget">👏</button>
                        <tt-set="opened">
                            <pid="secondContent">secondpopover</p>
                        </t>
                    </Popover>
                    <br/>
                    <spanid="dismissPopovers">💀</span>
                </div>`;

            constparent=newParent();
            constfixture=testUtils.prepareTarget();

            constbody=document.querySelector('body');
            awaitparent.mount(fixture);
            //Showfirstpopover
            assert.containsNone(body,'.o_popover');
            awaittestUtils.dom.click('#firstTarget');
            assert.containsOnce(body,'#firstContent');
            assert.containsNone(body,'#secondContent');
            awaittestUtils.dom.click('#dismissPopovers');
            assert.containsNone(body,'.o_popover');
            //Showfirstthendisplaysecond
            awaittestUtils.dom.click('#firstTarget');
            assert.containsOnce(body,'#firstContent');
            assert.containsNone(body,'#secondContent');
            awaittestUtils.dom.click('#secondTarget');
            assert.containsNone(body,'#firstContent');
            assert.containsOnce(body,'#secondContent');
            awaittestUtils.dom.click('#dismissPopovers');
            assert.containsNone(body,'.o_popover');
            parent.destroy();
        });

        QUnit.test('toggle',asyncfunction(assert){
            assert.expect(4);

            classParentextendsComponent{}
            //PopovershouldbeincludedasagloballyavailableComponent
            Object.assign(Parent,{
                env:makeTestEnvironment(),
                template:xml`
                    <div>
                        <Popover>
                            <buttonid="open">Open</button>
                            <tt-set="opened">
                                Opened!
                            </t>
                        </Popover>
                    </div>
                `,
            });

            constparent=newParent();
            constfixture=testUtils.prepareTarget();
            awaitparent.mount(fixture);

            constbody=document.querySelector('body');
            assert.containsOnce(body,'#open');
            assert.containsNone(body,'.o_popover');

            awaittestUtils.dom.click('#open');
            assert.containsOnce(body,'.o_popover');

            awaittestUtils.dom.click('#open');
            assert.containsNone(body,'.o_popover');

            parent.destroy();
        });

        QUnit.test('closeevent',asyncfunction(assert){
            assert.expect(7);

            //NeededtotriggertheeventfrominsidethePopoverslot.
            classContentextendsComponent{}
            Content.template=xml`
                <buttonid="close"t-on-click="trigger('o-popover-close')">
                    Close
                </button>
            `;

            classParentextendsComponent{}
            //PopovershouldbeincludedasagloballyavailableComponent
            Object.assign(Parent,{
                components:{Content},
                env:makeTestEnvironment(),
                template:xml`
                    <div>
                        <Popover>
                            <buttonid="open">Open</button>
                            <tt-set="opened">
                                <Content/>
                            </t>
                        </Popover>
                    </div>
                `,
            });

            constparent=newParent();
            constfixture=testUtils.prepareTarget();
            awaitparent.mount(fixture);

            constbody=document.querySelector('body');
            assert.containsOnce(body,'#open');
            assert.containsNone(body,'.o_popover');
            assert.containsNone(body,'#close');

            awaittestUtils.dom.click('#open');
            assert.containsOnce(body,'.o_popover');
            assert.containsOnce(body,'#close');

            awaittestUtils.dom.click('#close');
            assert.containsNone(body,'.o_popover');
            assert.containsNone(body,'#close');

            parent.destroy();
        });
    });
});
