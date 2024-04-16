flectra.define('product_matrix.section_and_note_widget',function(require){

varDialog=require('web.Dialog');
varcore=require('web.core');
var_t=core._t;
varqweb=core.qweb;
varfieldRegistry=require('web.field_registry');
require('account.section_and_note_backend');

varSectionAndNoteFieldOne2Many=fieldRegistry.get('section_and_note_one2many');

SectionAndNoteFieldOne2Many.include({
    custom_events:_.extend({},SectionAndNoteFieldOne2Many.prototype.custom_events,{
        open_matrix:'_openMatrix',
    }),

    /**
     *Sendsthematrixmodificationstotheserver
     *Throughachangeonaninvisiblenonstoredfield.
     *
     *@param{List}listofchangesinthematrix,tobeappliedtotheorder.
     *   {integer}quantity:float
     *   {List}ptav_ids:product.template.attribute.valueids
     *
     *@private
    */
    _applyGrid:function(changes,productTemplateId){
        //thegetParentistotriggertheeventontheformControllerinsteadoftheone2many.
        //Ifnot,theone2manycrashesonresetbecauseittriestofindanoperationintheevent
        //evenifthereisn'tany.
        //theonlysolutionwouldbetouseacustomeventcatchedonanewcontroller
        //ontheso/poform(asajs_class).
        this.trigger_up('field_changed',{
            dataPointID:this.dataPointID,
            changes:{
                grid:JSON.stringify({changes:changes,product_template_id:productTemplateId}),
                grid_update:true//tosaythatthechangestogridhavetobeappliedtotheSO.
            },
            viewType:'form',
        });
    },

    /**
     *Catchestheeventaskingformatrixopening
     *
     *@param{FlectraEvent}evvariousvaluesneededtoopenthematrix
     * {integer}data.product_template_idproduct.templateid
     * {list}data.editedCellAttributeslistofproduct.template.attribute.valueids
     * {bool}data.editwhetherthelinesourceshouldbedeletedornot.
     *
     *@private
    */
    _openMatrix:function(ev){
        ev.stopPropagation();
        varself=this;
        vardataPointId=ev.data.dataPointId;
        varproductTemplateId=ev.data.product_template_id;
        vareditedCellAttributes=ev.data.editedCellAttributes;
        if(!ev.data.edit){
            //removethelineusedtoopenthematrix
            this._setValue({operation:'DELETE',ids:[dataPointId]});
        }
        //thegetParentistotriggertheeventontheformControllerinsteadoftheone2many.
        //Ifnot,theone2manycrashesonresetbecauseittriestofindanoperationintheevent
        //evenifthereisn'tany.
        //theonlysolutionwouldbetouseacustomeventcatchedonanewcontroller
        //ontheso/poform(asajs_class).
        this.trigger_up('field_changed',{
            dataPointID:this.dataPointID,
            changes:{
                grid_product_tmpl_id:{id:productTemplateId}
            },
            viewType:'form',
            onSuccess:function(){
                constgridInfo=self.recordData.grid;
                self._openMatrixConfigurator(gridInfo,productTemplateId,editedCellAttributes);
            }
        });
    },

    /**
     *TriggersMatrixDialogopening
     *
     *@param{String}jsonInfomatrixdialogcontent
     *@param{integer}productTemplateIdproduct.templateid
     *@param{editedCellAttributes}listofproduct.template.attribute.valueids
     * usedtofocusonthematrixcellrepresentingtheeditedline.
     *
     *@private
    */
    _openMatrixConfigurator:function(jsonInfo,productTemplateId,editedCellAttributes){
        varself=this;
        varinfos=JSON.parse(jsonInfo);
        varMatrixDialog=newDialog(this,{
            title:_t('ChooseProductVariants'),
            size:'extra-large',//adaptsizedependingonmatrixsize?
            $content:$(qweb.render(
                'product_matrix.matrix',{
                    header:infos.header,
                    rows:infos.matrix,
                }
            )),
            buttons:[
                {text:_t('Confirm'),classes:'btn-primary',close:true,click:function(result){
                    var$inputs=this.$('.o_matrix_input');
                    varmatrixChanges=[];
                    _.each($inputs,function(matrixInput){
                        if(matrixInput.value&&matrixInput.value!==matrixInput.attributes.value.nodeValue){
                            matrixChanges.push({
                                qty:parseFloat(matrixInput.value),
                                ptav_ids:matrixInput.attributes.ptav_ids.nodeValue.split(",").map(function(id){
                                      returnparseInt(id);
                                }),
                            });
                        }
                    });
                    if(matrixChanges.length>0){
                        self._applyGrid(matrixChanges,productTemplateId);
                    }
                }},
                {text:_t('Close'),close:true},
            ],
        }).open();

        MatrixDialog.opened(function(){
            if(editedCellAttributes.length>0){
                varstr=editedCellAttributes.toString();
                MatrixDialog.$content.find('.o_matrix_input').filter((k,v)=>v.attributes.ptav_ids.nodeValue===str)[0].focus();
            }else{
                MatrixDialog.$content.find('.o_matrix_input:first()').focus();
            }
        });
    },

});

returnSectionAndNoteFieldOne2Many;

});
