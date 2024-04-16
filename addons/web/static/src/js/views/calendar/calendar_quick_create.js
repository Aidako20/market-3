flectra.define('web.CalendarQuickCreate',function(require){
"usestrict";

varcore=require('web.core');
varDialog=require('web.Dialog');

var_t=core._t;
varQWeb=core.qweb;

/**
 *Quickcreationview.
 *
 *Triggersasingleevent"added"withasingleparameter"name",whichisthe
 *nameenteredbytheuser
 *
 *@class
 *@type{*}
 */
varQuickCreate=Dialog.extend({
    events:_.extend({},Dialog.events,{
        'keyupinput':'_onkeyup',
    }),

    /**
     *@constructor
     *@param{Widget}parent
     *@param{Object}buttons
     *@param{Object}options
     *@param{Object}dataTemplate
     *@param{Object}dataCalendar
     */
    init:function(parent,buttons,options,dataTemplate,dataCalendar){
        this._buttons=buttons||false;
        this.options=options;

        //Canholddatapre-setfromwhereyouclickedonagenda
        this.dataTemplate=dataTemplate||{};
        this.dataCalendar=dataCalendar;

        varself=this;
        this._super(parent,{
            title:options.title,
            size:'small',
            buttons:this._buttons?[
                {text:_t("Create"),classes:'btn-primary',click:function(){
                    if(!self._quickAdd(dataCalendar)){
                        self.focus();
                    }
                }},
                {text:_t("Edit"),click:function(){
                    dataCalendar.disableQuickCreate=true;
                    dataCalendar.title=self.$('input').val().trim();
                    dataCalendar.on_save=self.destroy.bind(self);
                    self.trigger_up('openCreate',dataCalendar);
                }},
                {text:_t("Cancel"),close:true},
            ]:[],
            $content:QWeb.render('CalendarView.quick_create',{widget:this})
        });
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    focus:function(){
        this.$('input').focus();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Gathersdatafromthequickcreatedialogalaunchquick_create(data)method
     */
    _quickAdd:function(dataCalendar){
        dataCalendar=$.extend({},this.dataTemplate,dataCalendar);
        varval=this.$('input').val().trim();
        if(!val){
            this.$('label,input').addClass('o_field_invalid');
            varwarnings=_.str.sprintf('<ul><li>%s</li></ul>',_t("Summary"));
            this.do_warn(_t("Invalidfields:"),warnings);
        }
        dataCalendar.title=val;
        return(val)?this.trigger_up('quickCreate',{data:dataCalendar,options:this.options}):false;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{keyEvent}event
     */
    _onkeyup:function(event){
        if(this._flagEnter){
            return;
        }
        if(event.keyCode===$.ui.keyCode.ENTER){
            this._flagEnter=true;
            if(!this._quickAdd(this.dataCalendar)){
                this._flagEnter=false;
            }
        }elseif(event.keyCode===$.ui.keyCode.ESCAPE&&this._buttons){
            this.close();
        }
    },
});

returnQuickCreate;

});
