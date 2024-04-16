flectra.define('mrp.MrpDocumentViewer',function(require){
"usestrict";

constDocumentViewer=require('mail.DocumentViewer');

/**
 *ThisfiledefinestheDocumentViewerfortheMRPDocumentsKanbanview.
 */
constMrpDocumentsDocumentViewer=DocumentViewer.extend({
    init(parent,attachments,activeAttachmentID){
        this._super(...arguments);
        this.modelName='mrp.document';
    },
});

returnMrpDocumentsDocumentViewer;

});

