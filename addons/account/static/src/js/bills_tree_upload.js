flectra.define('account.upload.bill.mixin',function(require){
"usestrict";

    varcore=require('web.core');
    var_t=core._t;

    varqweb=core.qweb;

    varUploadBillMixin={

        start:function(){
            //defineauniqueuploadIdandacallbackmethod
            this.fileUploadID=_.uniqueId('account_bill_file_upload');
            $(window).on(this.fileUploadID,this._onFileUploaded.bind(this));
            returnthis._super.apply(this,arguments);
        },

        _onAddAttachment:function(ev){
            //Autosubmitformoncewe'veselectedanattachment
            var$input=$(ev.currentTarget).find('input.o_input_file');
            if($input.val()!==''){
                var$binaryForm=this.$('.o_vendor_bill_uploadform.o_form_binary_form');
                $binaryForm.submit();
            }
        },

        _onFileUploaded:function(){
            //Callbackonceattachmenthavebeencreated,createabillwithattachmentids
            varself=this;
            varattachments=Array.prototype.slice.call(arguments,1);
            //Getidfromresult
            varattachent_ids=attachments.reduce(function(filtered,record){
                if(record.id){
                    filtered.push(record.id);
                }
                returnfiltered;
            },[]);
            returnthis._rpc({
                model:'account.journal',
                method:'create_invoice_from_attachment',
                args:["",attachent_ids],
                context:this.initialState.context,
            }).then(function(result){
                self.do_action(result);
            }).catch(function(){
                //Resetthefileinput,allowingtoselectagainthesamefileifneeded
                self.$('.o_vendor_bill_upload.o_input_file').val('');
            });
        },

        _onUpload:function(event){
            varself=this;
            //Ifhiddenuploadformdon'texists,createit
            var$formContainer=this.$('.o_content').find('.o_vendor_bill_upload');
            if(!$formContainer.length){
                $formContainer=$(qweb.render('account.BillsHiddenUploadForm',{widget:this}));
                $formContainer.appendTo(this.$('.o_content'));
            }
            //Triggertheinputtoselectafile
            this.$('.o_vendor_bill_upload.o_input_file').click();
        },
    }
    returnUploadBillMixin;
});


flectra.define('account.bills.tree',function(require){
"usestrict";
    varcore=require('web.core');
    varListController=require('web.ListController');
    varListView=require('web.ListView');
    varUploadBillMixin=require('account.upload.bill.mixin');
    varviewRegistry=require('web.view_registry');

    varBillsListController=ListController.extend(UploadBillMixin,{
        buttons_template:'BillsListView.buttons',
        events:_.extend({},ListController.prototype.events,{
            'click.o_button_upload_bill':'_onUpload',
            'change.o_vendor_bill_upload.o_form_binary_form':'_onAddAttachment',
        }),
    });

    varBillsListView=ListView.extend({
        config:_.extend({},ListView.prototype.config,{
            Controller:BillsListController,
        }),
    });

    viewRegistry.add('account_tree',BillsListView);
});

flectra.define('account.dashboard.kanban',function(require){
"usestrict";
    varcore=require('web.core');
    varKanbanController=require('web.KanbanController');
    varKanbanView=require('web.KanbanView');
    varUploadBillMixin=require('account.upload.bill.mixin');
    varviewRegistry=require('web.view_registry');

    varDashboardKanbanController=KanbanController.extend(UploadBillMixin,{
        events:_.extend({},KanbanController.prototype.events,{
            'click.o_button_upload_bill':'_onUpload',
            'change.o_vendor_bill_upload.o_form_binary_form':'_onAddAttachment',
        }),
        /**
         *Weoverride_onUpload(fromtheuploadbillmixin)topassdefault_journal_id
         *anddefault_move_typeincontext.
         *
         *@override
         */
        _onUpload:function(event){
            varkanbanRecord=$(event.currentTarget).closest('.o_kanban_record').data('record');
            this.initialState.context['default_journal_id']=kanbanRecord.id;
            if($(event.currentTarget).attr('journal_type')=='sale'){
                this.initialState.context['default_move_type']='out_invoice'
            }elseif($(event.currentTarget).attr('journal_type')=='purchase'){
                this.initialState.context['default_move_type']='in_invoice'
            }
            UploadBillMixin._onUpload.apply(this,arguments);
        }
    });

    varDashboardKanbanView=KanbanView.extend({
        config:_.extend({},KanbanView.prototype.config,{
            Controller:DashboardKanbanController,
        }),
    });

    viewRegistry.add('account_dashboard_kanban',DashboardKanbanView);
});
