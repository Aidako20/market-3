flectra.define('web.owl_dialog_tests',function(require){
    "usestrict";

    constLegacyDialog=require('web.Dialog');
    constmakeTestEnvironment=require('web.test_env');
    constDialog=require('web.OwlDialog');
    consttestUtils=require('web.test_utils');

    const{Component,tags,useState}=owl;
    constEscapeKey={key:'Escape',keyCode:27,which:27};
    const{xml}=tags;

    QUnit.module('core',{},function(){
        QUnit.module('OwlDialog');

        QUnit.test("Renderingofallprops",asyncfunction(assert){
            assert.expect(35);

            classSubComponentextendsComponent{
                //Handlers
                _onClick(){
                    assert.step('subcomponent_clicked');
                }
            }
            SubComponent.template=xml`<divclass="o_subcomponent"t-esc="props.text"t-on-click="_onClick"/>`;

            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.state=useState({textContent:"sup"});
                }
                //Handlers
                _onButtonClicked(ev){
                    assert.step('button_clicked');
                }
                _onDialogClosed(){
                    assert.step('dialog_closed');
                }
            }
            Parent.components={Dialog,SubComponent};
            Parent.env=makeTestEnvironment();
            Parent.template=xml`
                <Dialog
                    backdrop="state.backdrop"
                    contentClass="state.contentClass"
                    fullscreen="state.fullscreen"
                    renderFooter="state.renderFooter"
                    renderHeader="state.renderHeader"
                    size="state.size"
                    subtitle="state.subtitle"
                    technical="state.technical"
                    title="state.title"
                    t-on-dialog-closed="_onDialogClosed"
                    >
                    <SubComponenttext="state.textContent"/>
                    <tt-set="buttons">
                        <buttonclass="btnbtn-primary"t-on-click="_onButtonClicked">TheButton</button>
                    </t>
                </Dialog>`;

            constparent=newParent();
            awaitparent.mount(testUtils.prepareTarget());
            constdialog=document.querySelector('.o_dialog');

            //Helperfunction
            asyncfunctionchangeProps(key,value){
                parent.state[key]=value;
                awaittestUtils.nextTick();
            }

            //Basiclayoutwithdefaultproperties
            assert.containsOnce(dialog,'.modal.o_technical_modal');
            assert.hasClass(dialog.querySelector('.modal.modal-dialog'),'modal-lg');
            assert.containsOnce(dialog,'.modal-header>button.close');
            assert.containsOnce(dialog,'.modal-footer>button.btn.btn-primary');
            assert.strictEqual(dialog.querySelector('.modal-body').innerText.trim(),"sup",
                "Subcomponentshouldmatchwithitsgiventext");

            //Backdrop(default:'static')
            //Staticbackdropclickshouldfocusfirstbutton
            //=>weneedtoresetthatproperty
            dialog.querySelector('.btn-primary').blur();//Removethefocusexplicitely
            assert.containsNone(document.body,'.modal-backdrop');//Nobackdrop*element*forFlectramodal...
            assert.notEqual(window.getComputedStyle(dialog.querySelector('.modal')).backgroundColor,'rgba(0,0,0,0)');//...butanontransparentmodal
            awaittestUtils.dom.click(dialog.querySelector('.modal'));
            assert.strictEqual(document.activeElement,dialog.querySelector('.btn-primary'),
                "Buttonshouldbefocusedwhenclickingonbackdrop");
            assert.verifySteps([]);//Ensurenotclosed
            dialog.querySelector('.btn-primary').blur();//Removethefocusexplicitely

            awaitchangeProps('backdrop',false);
            assert.containsNone(document.body,'.modal-backdrop');//Nobackdrop*element*forFlectramodal...
            assert.strictEqual(window.getComputedStyle(dialog.querySelector('.modal')).backgroundColor,'rgba(0,0,0,0)');
            awaittestUtils.dom.click(dialog.querySelector('.modal'));
            assert.notEqual(document.activeElement,dialog.querySelector('.btn-primary'),
                "Buttonshouldnotbefocusedwhenclickingonbackdrop'false'");
            assert.verifySteps([]);//Ensurenotclosed

            awaitchangeProps('backdrop',true);
            assert.containsNone(document.body,'.modal-backdrop');//Nobackdrop*element*forFlectramodal...
            assert.notEqual(window.getComputedStyle(dialog.querySelector('.modal')).backgroundColor,'rgba(0,0,0,0)');//...butanontransparentmodal
            awaittestUtils.dom.click(dialog.querySelector('.modal'));
            assert.notEqual(document.activeElement,dialog.querySelector('.btn-primary'),
                "Buttonshouldnotbefocusedwhenclickingonbackdrop'true'");
            assert.verifySteps(['dialog_closed']);

            //Dialogclass(default:'')
            awaitchangeProps('contentClass','my_dialog_class');
            assert.hasClass(dialog.querySelector('.modal-content'),'my_dialog_class');

            //Fullscreen(default:false)
            assert.doesNotHaveClass(dialog.querySelector('.modal'),'o_modal_full');
            awaitchangeProps('fullscreen',true);
            assert.hasClass(dialog.querySelector('.modal'),'o_modal_full');

            //Sizeclass(default:'large')
            awaitchangeProps('size','extra-large');
            assert.strictEqual(dialog.querySelector('.modal-dialog').className,'modal-dialogmodal-xl',
                "Modalshouldhavetakentheclassmodal-xl");
            awaitchangeProps('size','medium');
            assert.strictEqual(dialog.querySelector('.modal-dialog').className,'modal-dialog',
                "Modalshouldnothaveanyadditionnalclasswith'medium'");
            awaitchangeProps('size','small');
            assert.strictEqual(dialog.querySelector('.modal-dialog').className,'modal-dialogmodal-sm',
                "Modalshouldhavetakentheclassmodal-sm");

            //Subtitle(default:'')
            awaitchangeProps('subtitle',"TheSubtitle");
            assert.strictEqual(dialog.querySelector('span.o_subtitle').innerText.trim(),"TheSubtitle",
                "Subtitleshouldmatchwithitsgiventext");

            //Technical(default:true)
            assert.hasClass(dialog.querySelector('.modal'),'o_technical_modal');
            awaitchangeProps('technical',false);
            assert.doesNotHaveClass(dialog.querySelector('.modal'),'o_technical_modal');

            //Title(default:'Flectra')
            assert.strictEqual(dialog.querySelector('h4.modal-title').innerText.trim(),"Flectra"+"TheSubtitle",
                "Titleshouldmatchwithitsdefaulttext");
            awaitchangeProps('title',"TheTitle");
            assert.strictEqual(dialog.querySelector('h4.modal-title').innerText.trim(),"TheTitle"+"TheSubtitle",
                "Titleshouldmatchwithitsgiventext");

            //Reactivityofbuttons
            awaittestUtils.dom.click(dialog.querySelector('.modal-footer.btn-primary'));

            //Renderfooter(default:true)
            awaitchangeProps('renderFooter',false);
            assert.containsNone(dialog,'.modal-footer');

            //Renderheader(default:true)
            awaitchangeProps('renderHeader',false);
            assert.containsNone(dialog,'.header');

            //Reactivityofsubcomponents
            awaitchangeProps('textContent',"wassup");
            assert.strictEqual(dialog.querySelector('.o_subcomponent').innerText.trim(),"wassup",
                "Subcomponentshouldmatchwithitsgiventext");
            awaittestUtils.dom.click(dialog.querySelector('.o_subcomponent'));

            assert.verifySteps(['button_clicked','subcomponent_clicked']);

            parent.destroy();
        });

        QUnit.test("Interactionsbetweenmultipledialogs",asyncfunction(assert){
            assert.expect(22);

            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.dialogIds=useState([]);
                }
                //Handlers
                _onDialogClosed(id){
                    assert.step(`dialog_${id}_closed`);
                    this.dialogIds.splice(this.dialogIds.findIndex(d=>d===id),1);
                }
            }
            Parent.components={Dialog};
            Parent.env=makeTestEnvironment();
            Parent.template=xml`
                <div>
                    <Dialogt-foreach="dialogIds"t-as="dialogId"t-key="dialogId"
                        contentClass="'dialog_'+dialogId"
                        t-on-dialog-closed="_onDialogClosed(dialogId)"
                    />
                </div>`;

            constparent=newParent();
            awaitparent.mount(testUtils.prepareTarget());

            //Dialog1:Owl
            parent.dialogIds.push(1);
            awaittestUtils.nextTick();
            //Dialog2:Legacy
            newLegacyDialog(null,{}).open();
            awaittestUtils.nextTick();
            //Dialog3:Legacy
            newLegacyDialog(null,{}).open();
            awaittestUtils.nextTick();
            //Dialog4:Owl
            parent.dialogIds.push(4);
            awaittestUtils.nextTick();
            //Dialog5:Owl
            parent.dialogIds.push(5);
            awaittestUtils.nextTick();
            //Dialog6:Legacy(unopened)
            constunopenedModal=newLegacyDialog(null,{});
            awaittestUtils.nextTick();

            //Manuallyclosesthelastlegacydialog.Shouldnotaffecttheother
            //existingdialogs(3owland2legacy).
            unopenedModal.close();

            letmodals=document.querySelectorAll('.modal');
            assert.notOk(modals[modals.length-1].classList.contains('o_inactive_modal'),
                "lastdialogshouldhavetheactiveclass");
            assert.notOk(modals[modals.length-1].classList.contains('o_legacy_dialog'),
                "activedialogshouldnothavethelegacyclass");
            assert.containsN(document.body,'.o_dialog',3);
            assert.containsN(document.body,'.o_legacy_dialog',2);

            //Reactivitywithowldialogs
            awaittestUtils.dom.triggerEvent(modals[modals.length-1],'keydown',EscapeKey);//PressEscape

            modals=document.querySelectorAll('.modal');
            assert.notOk(modals[modals.length-1].classList.contains('o_inactive_modal'),
                "lastdialogshouldhavetheactiveclass");
            assert.notOk(modals[modals.length-1].classList.contains('o_legacy_dialog'),
                "activedialogshouldnothavethelegacyclass");
            assert.containsN(document.body,'.o_dialog',2);
            assert.containsN(document.body,'.o_legacy_dialog',2);

            awaittestUtils.dom.click(modals[modals.length-1].querySelector('.btn.btn-primary'));//Clickon'Ok'button

            modals=document.querySelectorAll('.modal');
            assert.containsOnce(document.body,'.modal.o_legacy_dialog:not(.o_inactive_modal)',
                "activedialogshouldhavethelegacyclass");
            assert.containsOnce(document.body,'.o_dialog');
            assert.containsN(document.body,'.o_legacy_dialog',2);

            //Reactivitywithlegacydialogs
            awaittestUtils.dom.triggerEvent(modals[modals.length-1],'keydown',EscapeKey);

            modals=document.querySelectorAll('.modal');
            assert.containsOnce(document.body,'.modal.o_legacy_dialog:not(.o_inactive_modal)',
                "activedialogshouldhavethelegacyclass");
            assert.containsOnce(document.body,'.o_dialog');
            assert.containsOnce(document.body,'.o_legacy_dialog');

            awaittestUtils.dom.click(modals[modals.length-1].querySelector('.close'));

            modals=document.querySelectorAll('.modal');
            assert.notOk(modals[modals.length-1].classList.contains('o_inactive_modal'),
                "lastdialogshouldhavetheactiveclass");
            assert.notOk(modals[modals.length-1].classList.contains('o_legacy_dialog'),
                "activedialogshouldnothavethelegacyclass");
            assert.containsOnce(document.body,'.o_dialog');
            assert.containsNone(document.body,'.o_legacy_dialog');

            parent.unmount();

            assert.containsNone(document.body,'.modal');
            //dialog1isclosedthroughtheremovalofitsparent=>nocallback
            assert.verifySteps(['dialog_5_closed','dialog_4_closed']);

            parent.destroy();
        });
    });

    QUnit.test("Z-indextogglingandinteractions",asyncfunction(assert){
        assert.expect(3);

        functioncreateCustomModal(className){
            const$modal=$(
                `<divrole="dialog"class="${className}"tabindex="-1">
                    <divclass="modal-dialogmedium">
                        <divclass="modal-content">
                            <mainclass="modal-body">Themodalbody</main>
                        </div>
                    </div>
                </div>`
            ).appendTo('body').modal();
            constmodal=$modal[0];
            modal.destroy=function(){
                $modal.modal('hide');
                this.remove();
            };
            returnmodal;
        }

        classParentextendsComponent{
            constructor(){
                super(...arguments);
                this.state=useState({showSecondDialog:true});
            }
        }
        Parent.components={Dialog};
        Parent.env=makeTestEnvironment();
        Parent.template=xml`
            <div>
                <Dialog/>
                <Dialogt-if="state.showSecondDialog"/>
            </div>`;

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        constfrontEndModal=createCustomModal('modal');
        constbackEndModal=createCustomModal('modalo_technical_modal');

        //querySelectorwilltargetthefirstmodal(thestaticone).
        constowlIndexBefore=getComputedStyle(document.querySelector('.o_dialog.modal')).zIndex;
        constfeZIndexBefore=getComputedStyle(frontEndModal).zIndex;
        constbeZIndexBefore=getComputedStyle(backEndModal).zIndex;

        parent.state.showSecondDialog=false;
        awaittestUtils.nextTick();

        assert.ok(owlIndexBefore<getComputedStyle(document.querySelector('.o_dialog.modal')).zIndex,
            "z-indexoftheowldialogshouldbeincrementedsincetheactivemodalwasdestroyed");
        assert.strictEqual(feZIndexBefore,getComputedStyle(frontEndModal).zIndex,
            "z-indexoffront-endmodalsshouldnotbeimpactedbyOwlDialogactivitysystem");
        assert.strictEqual(beZIndexBefore,getComputedStyle(backEndModal).zIndex,
            "z-indexofcustomback-endmodalsshouldnotbeimpactedbyOwlDialogactivitysystem");

        parent.destroy();
        frontEndModal.destroy();
        backEndModal.destroy();
    });
});
