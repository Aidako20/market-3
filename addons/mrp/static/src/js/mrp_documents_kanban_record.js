flectra.define('mrp.MrpDocumentsKanbanRecord',function(require){
"usestrict";

/**
 *ThisfiledefinestheKanbanRecordfortheMRPDocumentsKanbanview.
 */

constKanbanRecord=require('web.KanbanRecord');

constMrpDocumentsKanbanRecord=KanbanRecord.extend({
    events:Object.assign({},KanbanRecord.prototype.events,{
        'click.o_mrp_download':'_onDownload',
        'click.o_kanban_previewer':'_onImageClicked',
    }),

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Handlestheclickonthedownloadlinktosavetheattachmentlocally.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onDownload(ev){
        ev.preventDefault();
        window.location=`/web/content/${this.modelName}/${this.id}/datas?download=true`;
    },

    /**
     *Handlestheclickonthepreviewimage.Triggersup`_onKanbanPreview`to
     *display`DocumentViewer`.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onImageClicked(ev){
        ev.preventDefault();
        ev.stopPropagation();
        this.trigger_up('kanban_image_clicked',{
            recordList:[this.recordData],
            recordID:this.recordData.id
        });
    },
});

returnMrpDocumentsKanbanRecord;

});
