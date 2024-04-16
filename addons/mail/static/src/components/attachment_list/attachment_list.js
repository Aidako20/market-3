flectra.define('mail/static/src/components/attachment_list/attachment_list.js',function(require){
'usestrict';

constcomponents={
    Attachment:require('mail/static/src/components/attachment/attachment.js'),
};

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classAttachmentListextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps({
            compareDepth:{
                attachmentLocalIds:1,
            },
        });
        useStore(props=>{
            constattachments=this.env.models['mail.attachment'].all().filter(attachment=>
                props.attachmentLocalIds.includes(attachment.localId)
            );
            return{
                attachments:attachments
                    ?attachments.map(attachment=>attachment.__state)
                    :undefined,
            };
        },{
            compareDepth:{
                attachments:1,
            },
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.attachment[]}
     */
    getattachments(){
        returnthis.env.models['mail.attachment'].all().filter(attachment=>
            this.props.attachmentLocalIds.includes(attachment.localId)
        );
    }

    /**
     *@returns{mail.attachment[]}
     */
    getimageAttachments(){
        returnthis.attachments.filter(attachment=>attachment.fileType==='image');
    }

    /**
     *@returns{mail.attachment[]}
     */
    getnonImageAttachments(){
        returnthis.attachments.filter(attachment=>attachment.fileType!=='image');
    }

    /**
     *@returns{mail.attachment[]}
     */
    getviewableAttachments(){
        returnthis.attachments.filter(attachment=>attachment.isViewable);
    }

}

Object.assign(AttachmentList,{
    components,
    defaultProps:{
        attachmentLocalIds:[],
    },
    props:{
        areAttachmentsDownloadable:{
            type:Boolean,
            optional:true,
        },
        areAttachmentsEditable:{
            type:Boolean,
            optional:true,
        },
        attachmentLocalIds:{
            type:Array,
            element:String,
        },
        attachmentsDetailsMode:{
            type:String,
            optional:true,
            validate:prop=>['auto','card','hover','none'].includes(prop),
        },
        attachmentsImageSize:{
            type:String,
            optional:true,
            validate:prop=>['small','medium','large'].includes(prop),
        },
        showAttachmentsExtensions:{
            type:Boolean,
            optional:true,
        },
        showAttachmentsFilenames:{
            type:Boolean,
            optional:true,
        },
    },
    template:'mail.AttachmentList',
});

returnAttachmentList;

});
