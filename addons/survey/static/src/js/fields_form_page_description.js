flectra.define('survey.fields_form',function(require){
"usestrict";

varFieldRegistry=require('web.field_registry');
varFieldChar=require('web.basic_fields').FieldChar;

varFormDescriptionPage=FieldChar.extend({

    //--------------------------------------------------------------------------
    //WidgetAPI
    //--------------------------------------------------------------------------

    /**
     *@private
     *@override
     */
    _renderEdit:function(){
        vardef=this._super.apply(this,arguments);
        this.$el.addClass('col');
        var$inputGroup=$('<divclass="input-group">');
        this.$el=$inputGroup.append(this.$el);
        var$button=$(
            '<divclass="input-group-append">\
                <buttontype="button"title="Opensection"class="btnoe_edit_onlyo_icon_button">\
                    <iclass="fafa-fwo_button_iconfa-info-circle"/>\
                </button>\
            </div>'
        );
        this.$el=this.$el.append($button);
        $button.on('click',this._onClickEdit.bind(this));

        returndef;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClickEdit:function(ev){
        ev.stopPropagation();
        varid=this.record.id;
        if(id){
            this.trigger_up('open_record',{id:id,target:ev.target});
        }
    },
});

FieldRegistry.add('survey_description_page',FormDescriptionPage);

});
