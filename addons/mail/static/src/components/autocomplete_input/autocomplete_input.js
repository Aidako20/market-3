flectra.define('mail/static/src/components/autocomplete_input/autocomplete_input.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');

const{Component}=owl;

classAutocompleteInputextendsComponent{

    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
    }

    mounted(){
        if(this.props.isFocusOnMount){
            this.el.focus();
        }

        letargs={
            autoFocus:true,
            select:(ev,ui)=>this._onAutocompleteSelect(ev,ui),
            source:(req,res)=>this._onAutocompleteSource(req,res),
            focus:ev=>this._onAutocompleteFocus(ev),
            html:this.props.isHtml||false,
        };

        if(this.props.customClass){
            args.classes={'ui-autocomplete':this.props.customClass};
        }

        constautoCompleteElem=$(this.el).autocomplete(args);
        //Resizetheautocompletedropdownoptionstohandlethelongstrings
        //Bysettingthewidthofdropdownbasedonthewidthoftheinputelement.
        autoCompleteElem.data("ui-autocomplete")._resizeMenu=function(){
            constul=this.menu.element;
            ul.outerWidth(this.element.outerWidth());
        };
    }

    willUnmount(){
        $(this.el).autocomplete('destroy');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Returnswhetherthegivennodeisselforachildrenofself,including
     *thesuggestionmenu.
     *
     *@param{Node}node
     *@returns{boolean}
     */
    contains(node){
        if(this.el.contains(node)){
            returntrue;
        }
        if(!this.props.customClass){
            returnfalse;
        }
        constelement=document.querySelector(`.${this.props.customClass}`);
        if(!element){
            returnfalse;
        }
        returnelement.contains(node);
    }

    focus(){
        if(!this.el){
            return;
        }
        this.el.focus();
    }

    focusout(){
        if(!this.el){
            return;
        }
        this.el.blur();
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{FocusEvent}ev
     */
    _onAutocompleteFocus(ev){
        if(this.props.focus){
            this.props.focus(ev);
        }else{
            ev.preventDefault();
        }
    }

    /**
     *@private
     *@param{Event}ev
     *@param{Object}ui
     */
    _onAutocompleteSelect(ev,ui){
        if(this.props.select){
            this.props.select(ev,ui);
        }
    }

    /**
     *@private
     *@param{Object}req
     *@param{function}res
     */
    _onAutocompleteSource(req,res){
        if(this.props.source){
            this.props.source(req,res);
        }
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onBlur(ev){
        this.trigger('o-hide');
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onKeydown(ev){
        if(ev.key==='Escape'){
            this.trigger('o-hide');
        }
    }

}

Object.assign(AutocompleteInput,{
    defaultProps:{
        isFocusOnMount:false,
        isHtml:false,
        placeholder:'',
    },
    props:{
        customClass:{
            type:String,
            optional:true,
        },
        focus:{
            type:Function,
            optional:true,
        },
        isFocusOnMount:Boolean,
        isHtml:Boolean,
        placeholder:String,
        select:{
            type:Function,
            optional:true,
        },
        source:{
            type:Function,
            optional:true,
        },
    },
    template:'mail.AutocompleteInput',
});

returnAutocompleteInput;

});
