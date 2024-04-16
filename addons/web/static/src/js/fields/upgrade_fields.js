flectra.define('web.upgrade_widgets',function(require){
"usestrict";

/**
 * Theupgradewidgetsareintendedtobeusedinconfigsettings.
 * Whenchecked,anupgradepopupisshowedtotheuser.
 */

varAbstractField=require('web.AbstractField');
varbasic_fields=require('web.basic_fields');
varcore=require('web.core');
varDialog=require('web.Dialog');
varfield_registry=require('web.field_registry');
varframework=require('web.framework');
varrelational_fields=require('web.relational_fields');

var_t=core._t;
varQWeb=core.qweb;

varFieldBoolean=basic_fields.FieldBoolean;
varFieldRadio=relational_fields.FieldRadio;


/**
 *MixinthatdefinesthecommonfunctionssharedbetweenBooleanandRadio
 *upgradewidgets
 */
varAbstractFieldUpgrade={
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Redirectstheusertotheflectra-enterprise/upradepage
     *
     *@private
     *@returns{Promise}
     */
    _confirmUpgrade:function(){
        returnthis._rpc({
                model:'res.users',
                method:'search_count',
                args:[[["share","=",false]]],
            })
            .then(function(data){
                framework.redirect("https://www.flectrahq.com/flectra-enterprise/upgrade?num_users="+data);
            });
    },
    /**
     *Thisfunctionismeanttobeoverriddentoinsertthe'Enterprise'label
     *JQuerynodeattherightplace.
     *
     *@abstract
     *@private
     *@param{jQuery}$enterpriseLabelthe'Enterprise'labeltoinsert
     */
    _insertEnterpriseLabel:function($enterpriseLabel){},
    /**
     *OpenstheUpgradedialog.
     *
     *@private
     *@returns{Dialog}theinstanceoftheopenedDialog
     */
    _openDialog:function(){
        varmessage=$(QWeb.render('EnterpriseUpgrade'));

        varbuttons=[
            {
                text:_t("Upgradenow"),
                classes:'btn-primary',
                close:true,
                click:this._confirmUpgrade.bind(this),
            },
            {
                text:_t("Cancel"),
                close:true,
            },
        ];

        returnnewDialog(this,{
            size:'medium',
            buttons:buttons,
            $content:$('<div>',{
                html:message,
            }),
            title:_t("FlectraEnterprise"),
        }).open();
    },
    /**
     *@override
     *@private
     */
    _render:function(){
        this._super.apply(this,arguments);
        this._insertEnterpriseLabel($("<span>",{
            text:"Enterprise",
            'class':"badgebadge-primaryoe_inlineo_enterprise_label"
        }));
    },
    /**
     *Thisfunctionismeanttobeoverriddentoresetthe$eltoitsinitial
     *state.
     *
     *@abstract
     *@private
     */
    _resetValue:function(){},

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}event
     */
    _onInputClicked:function(event){
        if($(event.currentTarget).prop("checked")){
            this._openDialog().on('closed',this,this._resetValue.bind(this));
        }
    },

};

varUpgradeBoolean=FieldBoolean.extend(AbstractFieldUpgrade,{
    supportedFieldTypes:[],
    events:_.extend({},AbstractField.prototype.events,{
        'clickinput':'_onInputClicked',
    }),
    /**
     *Re-rendersthewidgetwiththelabel
     *
     *@param{jQuery}$label
     */
    renderWithLabel:function($label){
        this.$label=$label;
        this._render();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _insertEnterpriseLabel:function($enterpriseLabel){
        var$el=this.$label||this.$el;
        $el.append('&nbsp;').append($enterpriseLabel);
    },
    /**
     *@override
     *@private
     */
    _resetValue:function(){
        this.$input.prop("checked",false).change();
    },
});

varUpgradeRadio=FieldRadio.extend(AbstractFieldUpgrade,{
    supportedFieldTypes:[],
    events:_.extend({},FieldRadio.prototype.events,{
        'clickinput:last':'_onInputClicked',
    }),

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    isSet:function(){
        returntrue;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _insertEnterpriseLabel:function($enterpriseLabel){
        this.$('label').last().append('&nbsp;').append($enterpriseLabel);
    },
    /**
     *@override
     *@private
     */
    _resetValue:function(){
        this.$('input').first().prop("checked",true).click();
    },
});

field_registry
    .add('upgrade_boolean',UpgradeBoolean)
    .add('upgrade_radio',UpgradeRadio);

});
