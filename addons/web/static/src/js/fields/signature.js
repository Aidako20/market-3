flectra.define('web.Signature',function(require){
    "usestrict";

    varAbstractFieldBinary=require('web.basic_fields').AbstractFieldBinary;
    varcore=require('web.core');
    varfield_utils=require('web.field_utils');
    varregistry=require('web.field_registry');
    varsession=require('web.session');
    constSignatureDialog=require('web.signature_dialog');
    varutils=require('web.utils');


    varqweb=core.qweb;
    var_t=core._t;
    var_lt=core._lt;

varFieldBinarySignature=AbstractFieldBinary.extend({
    description:_lt("Signature"),
    fieldDependencies:_.extend({},AbstractFieldBinary.prototype.fieldDependencies,{
        __last_update:{type:'datetime'},
    }),
    resetOnAnyFieldChange:true,
    custom_events:_.extend({},AbstractFieldBinary.prototype.custom_events,{
        upload_signature:'_onUploadSignature',
    }),
    events:_.extend({},AbstractFieldBinary.prototype.events,{
        'click.o_signature':'_onClickSignature',
    }),
    template:null,
    supportedFieldTypes:['binary'],
    file_type_magic_word:{
        '/':'jpg',
        'R':'gif',
        'i':'png',
        'P':'svg+xml',
    },
    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Thiswidgetmustalwayshaverendereveniftherearenosignature.
     *Ineditmode,therealvalueisreturntomanagerequiredfields.
     *
     *@override
     */
    isSet:function(){
        if(this.mode==='edit'){
            returnthis.value;
        }
        returntrue;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Rendersanemptysignatureorthesavedsignature.Bothmusthavethesamesize.
     *
     *@override
     *@private
     */

    _render:function(){
        varself=this;
        vardisplaySignatureRatio=3;
        varurl;
        var$img;
        varwidth=this.nodeOptions.size?this.nodeOptions.size[0]:this.attrs.width;
        varheight=this.nodeOptions.size?this.nodeOptions.size[1]:this.attrs.height;
        if(this.value){
            if(!utils.is_bin_size(this.value)){
                //Usemagic-wordtechniquefordetectingimagetype
                url='data:image/'+(this.file_type_magic_word[this.value[0]]||'png')+';base64,'+this.value;
            }else{
                url=session.url('/web/image',{
                    model:this.model,
                    id:JSON.stringify(this.res_id),
                    field:this.nodeOptions.preview_image||this.name,
                    //uniqueforcesareloadoftheimagewhentherecordhasbeenupdated
                    unique:field_utils.format.datetime(this.recordData.__last_update).replace(/[^0-9]/g,''),
                });
            }
            $img=$(qweb.render("FieldBinarySignature-img",{widget:this,url:url}));
        }else{
            $img=$('<divclass="o_signatureo_signature_empty"><svg></svg><p>'+_t('SIGNATURE')+'</p></div>');
            if(width&&height){
                width=Math.min(width,displaySignatureRatio*height);
                height=width/displaySignatureRatio;
            }elseif(width){
                height=width/displaySignatureRatio;
            }elseif(height){
                width=height*displaySignatureRatio;
            }
        }
        if(width){
            $img.attr('width',width);
            $img.css('max-width',width+'px');
        }
        if(height){
            $img.attr('height',height);
            $img.css('max-height',height+'px');
        }
        this.$('>div').remove();
        this.$('>img').remove();

        this.$el.prepend($img);

        $img.on('error',function(){
            self._clearFile();
            $img.attr('src',self.placeholder);
            self.do_warn(false,_t("Couldnotdisplaytheselectedimage"));
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Iftheviewisineditmode,opendialogtosign.
     *
     *@private
     */
    _onClickSignature:function(){
        varself=this;
        if(this.mode==='edit'){

            varnameAndSignatureOptions={
                mode:'draw',
                displaySignatureRatio:3,
                signatureType:'signature',
                noInputName:true,
            };

            if(this.nodeOptions.full_name){
                varsignName;
                if(this.fields[this.nodeOptions.full_name].type==='many2one'){
                    //Ifm2oisempty,itwillhavefalsyvalueinrecordData
                    signName=this.recordData[this.nodeOptions.full_name]&&this.recordData[this.nodeOptions.full_name].data.display_name;
                }else{
                     signName=this.recordData[this.nodeOptions.full_name];
                 }
                nameAndSignatureOptions.defaultName=(signName==='')?undefined:signName;
            }

            nameAndSignatureOptions.defaultFont=this.nodeOptions.default_font||'';
            this.signDialog=newSignatureDialog(self,{nameAndSignatureOptions:nameAndSignatureOptions});

            this.signDialog.open();
        }
    },

    /**
     *Uploadthesignatureimageifvalidandclosethedialog.
     *
     *@private
     */
    _onUploadSignature:function(ev){
        varsignatureImage=ev.data.signatureImage;
        if(signatureImage!==this.signDialog.emptySignature){
            vardata=signatureImage[1];
            vartype=signatureImage[0].split('/')[1];
            this.on_file_uploaded(data.length,ev.data.name,type,data);
        }
        this.signDialog.close();
    }
});

registry.add('signature',FieldBinarySignature);

});
