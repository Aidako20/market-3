flectra.define('web.signature_widget',function(require){
"usestrict";

constframework=require('web.framework');
constSignatureDialog=require('web.signature_dialog');
constwidgetRegistry=require('web.widget_registry');
constWidget=require('web.Widget');


constWidgetSignature=Widget.extend({
    custom_events:Object.assign({},Widget.prototype.custom_events,{
        upload_signature:'_onUploadSignature',
    }),
    events:Object.assign({},Widget.prototype.events,{
        'click.o_sign_label':'_onClickSignature',
    }),
    template:'SignButton',
    /**
     *@constructor
     *@param{Widget}parent
     *@param{Object}record
     *@param{Object}nodeInfo
     */
    init:function(parent,record,nodeInfo){
        this._super.apply(this,arguments);
        this.res_id=record.res_id;
        this.res_model=record.model;
        this.state=record;
        this.node=nodeInfo;
        //signature_fieldisthefieldonwhichthesignatureimagewillbe
        //saved(`signature`bydefault).
        this.signature_field=this.node.attrs.signature_field||'signature';
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Openadialogtosign.
     *
     *@private
     */
    _onClickSignature:function(){
        constnameAndSignatureOptions={
            displaySignatureRatio:3,
            mode:'draw',
            noInputName:true,
            signatureType:'signature',
        };

        if(this.node.attrs.full_name){
            letsignName;
            constfieldFullName=this.state.data[this.node.attrs.full_name];
            if(fieldFullName&&fieldFullName.type==='record'){
                signName=fieldFullName.data.display_name;
            }else{
                signName=fieldFullName;
            }
            nameAndSignatureOptions.defaultName=signName||undefined;
        }

        nameAndSignatureOptions.defaultFont=this.node.attrs.default_font||'';
        this.signDialog=newSignatureDialog(this,{
            nameAndSignatureOptions:nameAndSignatureOptions,
        });
        this.signDialog.open();
    },
    /**
     *Uploadthesignatureimage(writeitonthecorrespondingfield)and
     *closethedialog.
     *
     *@returns{Promise}
     *@private
     */
    _onUploadSignature:function(ev){
        constfile=ev.data.signatureImage[1];
        constalways=()=>{
            this.trigger_up('reload');
            framework.unblockUI();
        };
        framework.blockUI();
        constrpcProm=this._rpc({
            model:this.res_model,
            method:'write',
            args:[[this.res_id],{
                [this.signature_field]:file,
            }],
        });
        rpcProm.then(always).guardedCatch(always);
        returnrpcProm;
    },
});

widgetRegistry.add('signature',WidgetSignature);

});
