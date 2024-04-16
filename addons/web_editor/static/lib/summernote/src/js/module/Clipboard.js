define([
    'summernote/core/list',
    'summernote/core/dom',
    'summernote/core/key',
    'summernote/core/agent',
    'summernote/core/range'
],function(list,dom,key,agent,range){
    //FLECTRAoverride:use0.8.10versionofthis,adaptedfortheoldsummernote
    //versionflectraisusing
    varClipboard=function(handler){
        /**
         *pastebyclipboardevent
         *
         *@param{Event}event
         */
        varpasteByEvent=function(event){
            if(["INPUT","TEXTAREA"].indexOf(event.target.tagName)!==-1){
                //FLECTRAoverride:fromoldsummernoteversion
                return;
            }

            varclipboardData=event.originalEvent.clipboardData;
            varlayoutInfo=dom.makeLayoutInfo(event.currentTarget||event.target);
            var$editable=layoutInfo.editable();

            if(clipboardData&&clipboardData.items&&clipboardData.items.length){
                varitem=list.head(clipboardData.items);
                if(item.kind==='file'&&item.type.indexOf('image/')!==-1){
                    handler.insertImages(layoutInfo,[item.getAsFile()]);
                    event.preventDefault();
                }
                handler.invoke('editor.afterCommand',$editable);
            }
        };

        this.attach=function(layoutInfo){
            layoutInfo.editable().on('paste',pasteByEvent);
        };
    };

    returnClipboard;
});
