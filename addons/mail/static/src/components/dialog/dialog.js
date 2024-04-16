flectra.define('mail/static/src/components/dialog/dialog.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

constpatchMixin=require('web.patchMixin');

const{Component}=owl;
const{useRef}=owl.hooks;

classDialogextendsComponent{

    /**
     *@param{...any}args
     */
    constructor(...args){
        super(...args);
        /**
         *Referencetothecomponentusedinsidethisdialog.
         */
        this._componentRef=useRef('component');
        this._onClickGlobal=this._onClickGlobal.bind(this);
        this._onKeydownDocument=this._onKeydownDocument.bind(this);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constdialog=this.env.models['mail.dialog'].get(props.dialogLocalId);
            return{
                dialog:dialog?dialog.__state:undefined,
            };
        });
        this._constructor();
    }

    /**
     *Allowspatchingconstructor.
     */
    _constructor(){}

    mounted(){
        document.addEventListener('click',this._onClickGlobal,true);
        document.addEventListener('keydown',this._onKeydownDocument);
    }

    willUnmount(){
        document.removeEventListener('click',this._onClickGlobal,true);
        document.removeEventListener('keydown',this._onKeydownDocument);
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.dialog}
     */
    getdialog(){
        returnthis.env.models['mail.dialog'].get(this.props.dialogLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenclickingonthisdialog.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClick(ev){
        ev.stopPropagation();
    }

    /**
     *Closesthedialogwhenclickingoutside.
     *Doesnotworkwithattachmentviewerbecauseittakesthewholespace.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClickGlobal(ev){
        if(this._componentRef.el&&this._componentRef.el.contains(ev.target)){
            return;
        }
        //TODO:thisshouldbechildlogic(willcrashifchilddoesn'thaveisCloseable!!)
        //task-2092965
        if(
            this._componentRef.comp&&
            this._componentRef.comp.isCloseable&&
            !this._componentRef.comp.isCloseable()
        ){
            return;
        }
        this.dialog.delete();
    }

    /**
     *@private
     *@param{KeyboardEvent}ev
     */
    _onKeydownDocument(ev){
        if(ev.key==='Escape'){
            this.dialog.delete();
        }
    }

}

Object.assign(Dialog,{
    props:{
        dialogLocalId:String,
    },
    template:'mail.Dialog',
});

returnpatchMixin(Dialog);

});
