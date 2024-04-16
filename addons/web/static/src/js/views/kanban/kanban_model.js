flectra.define('web.KanbanModel',function(require){
"usestrict";

/**
 *TheKanbanModelextendstheBasicModeltoaddKanbanspecificfeatureslike
 *movingarecordfromagrouptoanother,resequencingrecords...
 */

varBasicModel=require('web.BasicModel');
varviewUtils=require('web.viewUtils');

varKanbanModel=BasicModel.extend({
    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *AddsarecordtoagroupinthelocalData,andfetchtherecord.
     *
     *@param{string}groupIDlocalIDofthegroup
     *@param{integer}resIdidoftherecord
     *@returns{Promise<string>}resolvestothelocalidofthenewrecord
     */
    addRecordToGroup:function(groupID,resId){
        varself=this;
        vargroup=this.localData[groupID];
        varnew_record=this._makeDataPoint({
            res_id:resId,
            modelName:group.model,
            fields:group.fields,
            fieldsInfo:group.fieldsInfo,
            viewType:group.viewType,
            parentID:groupID,
        });

        vardef=this._fetchRecord(new_record).then(function(result){
            group.data.unshift(new_record.id);
            group.res_ids.unshift(resId);
            group.count++;

            //updatetheres_idsandcountoftheparent
            self.localData[group.parentID].count++;
            self._updateParentResIDs(group);

            returnresult.id;
        });
        returnthis._reloadProgressBarGroupFromRecord(new_record.id,def);
    },
    /**
     *Createsanewgroupfromaname(performsaname_create).
     *
     *@param{string}name
     *@param{string}parentIDlocalIDoftheparentofthegroup
     *@returns{Promise<string>}resolvestothelocalidofthenewgroup
     */
    createGroup:function(name,parentID){
        varself=this;
        varparent=this.localData[parentID];
        vargroupBy=parent.groupedBy[0];
        vargroupByField=parent.fields[groupBy];
        if(!groupByField||groupByField.type!=='many2one'){
            returnPromise.reject();//onlysupportedwhengroupedonm2o
        }
        returnthis._rpc({
                model:groupByField.relation,
                method:'name_create',
                args:[name],
                context:parent.context,//todo:combinewithviewcontext
            })
            .then(function(result){
                constcreateGroupDataPoint=(model,parent)=>{
                    constnewGroup=model._makeDataPoint({
                        modelName:parent.model,
                        context:parent.context,
                        domain:parent.domain.concat([[groupBy,"=",result[0]]]),
                        fields:parent.fields,
                        fieldsInfo:parent.fieldsInfo,
                        isOpen:true,
                        limit:parent.limit,
                        parentID:parent.id,
                        openGroupByDefault:true,
                        orderedBy:parent.orderedBy,
                        value:result,
                        viewType:parent.viewType,
                    });
                    if(parent.progressBar){
                        newGroup.progressBarValues=_.extend({
                            counts:{},
                        },parent.progressBar);
                    }
                    returnnewGroup;
                };
                constnewGroup=createGroupDataPoint(self,parent);
                parent.data.push(newGroup.id);
                if(self.isInSampleMode()){
                    //insamplemode,createthenewgroupinbothmodels(main+sample)
                    constsampleParent=self.sampleModel.localData[parentID];
                    constnewSampleGroup=createGroupDataPoint(self.sampleModel,sampleParent);
                    sampleParent.data.push(newSampleGroup.id);
                }
                returnnewGroup.id;
            });
    },
    /**
     *Createsanewrecordfromthegivenvalue,andaddittothegivengroup.
     *
     *@param{string}groupID
     *@param{Object}values
     *@returns{Promise}resolvedwiththelocalidofthecreatedrecord
     */
    createRecordInGroup:function(groupID,values){
        varself=this;
        vargroup=this.localData[groupID];
        varcontext=this._getContext(group);
        varparent=this.localData[group.parentID];
        vargroupedBy=parent.groupedBy;
        context['default_'+groupedBy]=viewUtils.getGroupValue(group,groupedBy);
        vardef;
        if(Object.keys(values).length===1&&'display_name'invalues){
            //only'display_nameisgiven,performa'name_create'
            def=this._rpc({
                    model:parent.model,
                    method:'name_create',
                    args:[values.display_name],
                    context:context,
                }).then(function(records){
                    returnrecords[0];
                });
        }else{
            //otherfieldsarespecified,performaclassical'create'
            def=this._rpc({
                model:parent.model,
                method:'create',
                args:[values],
                context:context,
            });
        }
        returndef.then(function(resID){
            returnself.addRecordToGroup(group.id,resID);
        });
    },
    /**
     *Addthefollowing(kanbanspecific)keyswhenperforminga`get`:
     *
     *-tooltipData
     *-progressBarValues
     *-isGroupedByM2ONoColumn
     *
     *@override
     *@see_readTooltipFields
     *@returns{Object}
     */
    __get:function(){
        varresult=this._super.apply(this,arguments);
        vardp=result&&this.localData[result.id];
        if(dp){
            if(dp.tooltipData){
                result.tooltipData=$.extend(true,{},dp.tooltipData);
            }
            if(dp.progressBarValues){
                result.progressBarValues=$.extend(true,{},dp.progressBarValues);
            }
            if(dp.fields[dp.groupedBy[0]]){
                vargroupedByM2O=dp.fields[dp.groupedBy[0]].type==='many2one';
                result.isGroupedByM2ONoColumn=!dp.data.length&&groupedByM2O;
            }else{
                result.isGroupedByM2ONoColumn=false;
            }
        }
        returnresult;
    },
    /**
     *Sameas@seegetbutgettingtheparentelementwhoseIDisgiven.
     *
     *@param{string}id
     *@returns{Object}
     */
    getColumn:function(id){
        varelement=this.localData[id];
        if(element){
            returnthis.get(element.parentID);
        }
        returnnull;
    },
    /**
     *@override
     */
    __load:function(params){
        this.defaultGroupedBy=params.groupBy||[];
        params.groupedBy=(params.groupedBy&&params.groupedBy.length)?params.groupedBy:this.defaultGroupedBy;
        returnthis._super(params);
    },
    /**
     *Loadmorerecordsinagroup.
     *
     *@param{string}groupIDlocalIDofthegroup
     *@returns{Promise<string>}resolvestothelocalIDofthegroup
     */
    loadMore:function(groupID){
        vargroup=this.localData[groupID];
        varoffset=group.loadMoreOffset+group.limit;
        returnthis.reload(group.id,{
            loadMoreOffset:offset,
        });
    },
    /**
     *Movesarecordfromagrouptoanother.
     *
     *@param{string}recordIDlocalIDoftherecord
     *@param{string}groupIDlocalIDofthenewgroupoftherecord
     *@param{string}parentIDlocalIDoftheparent
     *@returns{Promise<string[]>}resolvestoapair[oldGroupID,newGroupID]
     */
    moveRecord:function(recordID,groupID,parentID){
        varself=this;
        varparent=this.localData[parentID];
        varnew_group=this.localData[groupID];
        varchanges={};
        vargroupedFieldName=parent.groupedBy[0];
        vargroupedField=parent.fields[groupedFieldName];
        if(groupedField.type==='many2one'){
            changes[groupedFieldName]={
                id:new_group.res_id,
                display_name:new_group.value,
            };
        }elseif(groupedField.type==='selection'){
            varvalue=_.findWhere(groupedField.selection,{1:new_group.value});
            changes[groupedFieldName]=value&&value[0]||false;
        }else{
            changes[groupedFieldName]=new_group.value;
        }

        //Manuallyupdatesgroupsdata.Note:thisisdonebeforetheactual
        //saveasitmightneedtoperformareadgroupinsomecasessothose
        //updateddatamightbeoverriddenagain.
        varrecord=self.localData[recordID];
        varresID=record.res_id;
        //Removerecordfromitscurrentgroup
        varold_group;
        for(vari=0;i<parent.data.length;i++){
            old_group=self.localData[parent.data[i]];
            varindex=_.indexOf(old_group.data,recordID);
            if(index>=0){
                old_group.data.splice(index,1);
                old_group.count--;
                old_group.res_ids=_.without(old_group.res_ids,resID);
                self._updateParentResIDs(old_group);
                break;
            }
        }
        //Addrecordtoitsnewgroup
        new_group.data.push(recordID);
        new_group.res_ids.push(resID);
        new_group.count++;

        returnthis.notifyChanges(recordID,changes).then(function(){
            returnself.save(recordID);
        }).then(function(){
            record.parentID=new_group.id;
            return[old_group.id,new_group.id];
        });
    },
    /**
     *@override
     */
    reload:function(id,options){
        //ifthegroupByisgivenintheoptionsandifitisanemptyarray,
        //fallbackonthedefaultgroupBy
        if(options&&options.groupBy&&!options.groupBy.length){
            options.groupBy=this.defaultGroupedBy;
        }
        returnthis._super(id,options);
    },
    /**
     *@override
     */
    __reload:function(id,options){
        vardef=this._super(id,options);
        if(options&&options.loadMoreOffset){
            returndef;
        }
        returnthis._reloadProgressBarGroupFromRecord(id,def);
    },
    /**
     *@override
     */
    save:function(recordID){
        vardef=this._super.apply(this,arguments);
        returnthis._reloadProgressBarGroupFromRecord(recordID,def);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _makeDataPoint:function(params){
        vardataPoint=this._super.apply(this,arguments);
        if(params.progressBar){
            dataPoint.progressBar=params.progressBar;
        }
        returndataPoint;
    },
    /**
     *@override
     */
    _load:function(dataPoint,options){
        if(dataPoint.groupedBy.length&&dataPoint.progressBar){
            returnthis._readProgressBarGroup(dataPoint,options);
        }
        returnthis._super.apply(this,arguments);
    },
    /**
     *EnsuresthatthereisnonestedgroupsinKanban(onlythefirstgrouping
     *levelistakenintoaccount).
     *
     *@override
     *@private
     *@param{Object}listvalidresourceobject
     */
    _readGroup:function(list){
        varself=this;
        if(list.groupedBy.length>1){
            list.groupedBy=[list.groupedBy[0]];
        }
        returnthis._super.apply(this,arguments).then(function(result){
            returnself._readTooltipFields(list).then(_.constant(result));
        });
    },
    /**
     *@private
     *@param{Object}dataPoint
     *@returns{Promise<Object>}
     */
    _readProgressBarGroup:function(list,options){
        varself=this;
        vargroupsDef=this._readGroup(list,options);
        varprogressBarDef=this._rpc({
            model:list.model,
            method:'read_progress_bar',
            kwargs:{
                domain:list.domain,
                group_by:list.groupedBy[0],
                progress_bar:list.progressBar,
                context:list.context,
            },
        });
        returnPromise.all([groupsDef,progressBarDef]).then(function(results){
            vardata=results[1];
            _.each(list.data,function(groupID){
                vargroup=self.localData[groupID];
                varvalue=group.value;
                if(value===true){
                    value="True";
                }elseif(value===false){
                    value="False";
                }
                group.progressBarValues=_.extend({
                    counts:data[value]||{},
                },list.progressBar);
            });
            returnlist;
        });
    },
    /**
     *Fetchestooltipspecificfieldsonthegroupbyrelationandstoresitin
     *thecolumndatapointinaspecialkey`tooltipData`.
     *Dataforthetooltips(group_by_tooltip)arefetchedinbatchforall
     *groups,toavoiddoingmultiplecalls.
     *Dataarestoredinaspecialkey`tooltipData`onthedatapoint.
     *Notethattheoption`group_by_tooltip`isonlyform2ofields.
     *
     *@private
     *@param{Object}listalistofgroups
     *@returns{Promise}
     */
    _readTooltipFields:function(list){
        varself=this;
        vargroupedByField=list.fields[list.groupedBy[0].split(':')[0]];
        if(groupedByField.type!=='many2one'){
            returnPromise.resolve();
        }
        vargroupIds=_.reduce(list.data,function(groupIds,id){
            varres_id=self.get(id,{raw:true}).res_id;
            //Thefieldonwhichwearegroupingmightnotbesetonallrecords
            if(res_id){
                groupIds.push(res_id);
            }
            returngroupIds;
        },[]);
        vartooltipFields=[];
        vargroupedByFieldInfo=list.fieldsInfo.kanban[list.groupedBy[0]];
        if(groupedByFieldInfo&&groupedByFieldInfo.options){
            tooltipFields=Object.keys(groupedByFieldInfo.options.group_by_tooltip||{});
        }
        if(groupIds.length&&tooltipFields.length){
            varfieldNames=_.union(['display_name'],tooltipFields);
            returnthis._rpc({
                model:groupedByField.relation,
                method:'read',
                args:[groupIds,fieldNames],
                context:list.context,
            }).then(function(result){
                _.each(list.data,function(id){
                    vardp=self.localData[id];
                    dp.tooltipData=_.findWhere(result,{id:dp.res_id});
                });
            });
        }
        returnPromise.resolve();
    },
    /**
     *Reloadsallprogressbardata.Thisisdoneaftergivenpromiseand
     *insuresthatthegivenpromise'sresultisnotlost.
     *
     *@private
     *@param{string}recordID
     *@param{Promise}def
     *@returns{Promise}
     */
    _reloadProgressBarGroupFromRecord:function(recordID,def){
        varelement=this.localData[recordID];
        if(element.type==='list'&&!element.parentID){
            //wearereloadingthewholeview,sothereisnoneedtomanually
            //reloadtheprogressbars
            returndef;
        }

        //Ifweupdatedarecord,thenwemustpotentiallyupdatecolumns'
        //progressbars,soweneedtoloadgroupsinfoagain
        varself=this;
        while(element){
            if(element.progressBar){
                returndef.then(function(data){
                    returnself._load(element,{
                        keepEmptyGroups:true,
                        onlyGroups:true,
                    }).then(function(){
                        returndata;
                    });
                });
            }
            element=this.localData[element.parentID];
        }
        returndef;
    },
});
returnKanbanModel;
});
