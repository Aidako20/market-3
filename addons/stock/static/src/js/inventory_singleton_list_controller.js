flectra.define('stock.SingletonListController',function(require){
"usestrict";

varcore=require('web.core');
varInventoryReportListController=require('stock.InventoryReportListController');

var_t=core._t;

/**
 *Thepurposeofthisoverrideistoavoidtohavetwoormoresimilarrecords
 *inthelistview.
 *
 *It'susedinquantlistview,alisteditablewherewhenyoucreateanew
 *lineaboutaquantwhoalreadyexists,wewanttoupdatetheexistingone
 *insteadofcreateanewone,andthenwedon'twanttohavetwosimilarline
 *inthelistview,sowerefreshit.
 */

varSingletonListController=InventoryReportListController.extend({
    /**
     *@override
     *@return{Promise}rejectedwhenupdatethelistbecausewedon'twant
     *anymoretoselectacellwhomaybedoesn'texistanymore.
     */
    _confirmSave:function(id){
        varnewRecord=this.model.localData[id];
        varmodel=newRecord.model;
        varres_id=newRecord.res_id;

        varfindSimilarRecords=function(record){
            if((record.groupedBy&&record.groupedBy.length>0)||record.data.length){
                varrecordsToReturn=[];
                for(variinrecord.data){
                    varfoundRecords=findSimilarRecords(record.data[i]);
                    recordsToReturn=recordsToReturn.concat(foundRecords||[]);
                }
                returnrecordsToReturn;
            }else{
                if(record.res_id===res_id&&record.model===model){
                    if(record.count===0){
                        return[record];
                    }
                    elseif(record.ref&&record.ref.indexOf('virtual')!==-1){
                        return[record];
                    }
                }
            }
        };

        varhandle=this.model.get(this.handle);
        varsimilarRecords=findSimilarRecords(handle);

        if(similarRecords.length>1){
            varnotification=_t("Youtriedtocreatearecordwhoalreadyexists."+
            "<br/>Thislastonehasbeenmodifiedinstead.");
            this.do_notify(_t("Thisrecordalreadyexists."),notification);
            this.reload();
            returnPromise.reject();
        }
        else{
            returnthis._super.apply(this,arguments);
        }
    },
});

returnSingletonListController;

});
