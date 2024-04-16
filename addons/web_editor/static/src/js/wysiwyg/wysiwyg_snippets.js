flectra.define('web_editor.wysiwyg.snippets',function(require){
'usestrict';
vareditor=require('web_editor.editor');
varWysiwyg=require('web_editor.wysiwyg');


Wysiwyg.include({
    init:function(parent,options){
        this._super.apply(this,arguments);
        this.Editor=editor.Class;
        if(!this.options.toolbarHandler){
            this.options.toolbarHandler=$('#web_editor-top-edit');
        }
    },
    start:asyncfunction(){
        if(this.options.snippets){
            varself=this;
            this.editor=new(this.Editor)(this,this.options);
            this.$editor=this.editor.rte.editable();
            const$body=this.$editor[0]?this.$editor[0].ownerDocument.body:document.body;
            awaitthis.editor.prependTo($body);
            this._relocateEditorBar();
            this.$el.on('content_changed',function(e){
                self.trigger_up('wysiwyg_change');
            });
        }else{
            returnthis._super();
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _relocateEditorBar:function(){
        if(!this.options.toolbarHandler.length){
            this.options.toolbarHandler=$('.o_we_snippet_text_tools');
        }
        this.options.toolbarHandler.append(this.editor.$el);

        //TODOthenextfourlinesareahugehack:sincetheeditor.$el
        //isrepositioned,thesnippetsMenuelementsarenotatthe
        //correctpositionanymoreifitwasrepositionedoutsideofit...
        //thewholelogichastoberefactored...hopefullynotneededanymore
        //witheditorteamchanges
        if(this.editor.snippetsMenu&&!this.editor.snippetsMenu.$el.has(this.options.toolbarHandler).length){
            this.editor.snippetsMenu.$el.insertAfter(this.options.toolbarHandler);
            this.editor.snippetsMenu.$snippetEditorArea.insertAfter(this.editor.snippetsMenu.$el);
        }
    },
});

});
